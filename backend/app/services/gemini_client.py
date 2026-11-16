import os
import logging
from typing import Optional, Any
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from backend.app.core.config import settings

logger = logging.getLogger("gemini.client")

try:
    from google import genai
    from google.genai import types
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False
    genai = None
    types = None


class GeminiClientManager:
    """Manages the official google-genai Client instance with retries."""

    def __init__(self):
        self._client: Optional[genai.Client] = None
        self._init_client()

    def _init_client(self):
        if not GENAI_AVAILABLE:
            logger.warning("google-genai SDK not installed or available.")
            return

        api_key = settings.GEMINI_API_KEY
        if api_key and api_key != "your_gemini_api_key_here":
            try:
                self._client = genai.Client(api_key=api_key)
                logger.info("google-genai Client successfully initialized.")
            except Exception as e:
                logger.error(f"Failed to initialize google-genai Client: {e}")
        else:
            logger.info("No GEMINI_API_KEY set. Running in mock/fallback resilient mode.")

    @property
    def client(self) -> Optional[genai.Client]:
        return self._client

    def reload(self):
        self._init_client()


gemini_manager = GeminiClientManager()


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=10),
    reraise=True
)
async def generate_with_retry(client: Any, model: str, contents: Any, config: Any = None):
    """Executes Gemini generation with exponential backoff retry."""
    return await client.aio.models.generate_content(
        model=model,
        contents=contents,
        config=config
    )
