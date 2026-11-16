import os
import json
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles

from backend.app.core.config import settings
from backend.app.db.database import init_db
from backend.app.services.chat_orchestrator import orchestrator
from backend.app.api.admin_routes import router as admin_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize Database & Vector Knowledge Base
    logger.info("Initializing SQLite database tables...")
    await init_db()
    logger.info("Initializing ChromaDB knowledge base embeddings...")
    await orchestrator.init()
    yield
    # Shutdown
    logger.info("Shutting down application...")


app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all for development & testing
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Admin REST routes
app.include_router(admin_router)


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "environment": settings.APP_ENV,
        "gemini_api_configured": settings.has_gemini_key,
        "gemini_chat_model": settings.GEMINI_CHAT_MODEL,
        "gemini_complex_model": settings.GEMINI_COMPLEX_MODEL,
    }


@app.websocket("/ws/chat/{session_id}")
async def websocket_chat_endpoint(websocket: WebSocket, session_id: str):
    await websocket.accept()
    logger.info(f"WebSocket client connected for session: {session_id}")

    async def emit(payload: dict):
        """Helper to send JSON payloads back to the frontend."""
        try:
            await websocket.send_text(json.dumps(payload))
        except Exception as e:
            logger.warning(f"Failed to send websocket packet to {session_id}: {e}")

    try:
        # Send initial connection confirmation
        await emit({
            "type": "connection_ack",
            "session_id": session_id,
            "message": "Connected to NovaTech Real-Time Support Agent."
        })

        while True:
            data = await websocket.receive_text()
            try:
                packet = json.loads(data)
                content = packet.get("content", "").strip()
                if not content:
                    continue

                # Process turn through the orchestrator
                await orchestrator.process_turn(session_id, content, emit)
            except json.JSONDecodeError:
                await emit({"type": "error", "message": "Invalid JSON format."})
            except Exception as e:
                logger.error(f"Error processing turn for session {session_id}: {e}", exc_info=True)
                await emit({"type": "error", "message": f"Server processing error: {str(e)}"})

    except WebSocketDisconnect:
        logger.info(f"WebSocket client disconnected for session: {session_id}")
    except Exception as e:
        logger.error(f"Unexpected WebSocket error: {e}")


# Serve built production frontend files if present
dist_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../frontend/dist"))
assets_path = os.path.join(dist_path, "assets")
if os.path.exists(assets_path):
    app.mount("/assets", StaticFiles(directory=assets_path), name="assets")


@app.get("/")
async def serve_index():
    index_file = os.path.join(dist_path, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return {"message": "NovaTech Customer Service Bot API running."}


