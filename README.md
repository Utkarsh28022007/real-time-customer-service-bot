# NovaTech AI Real-Time Customer Service Platform

A production-ready, low-latency, real-time Generative AI Customer Service Bot built with **Python 3.11/3.13**, **FastAPI**, **WebSockets**, **Google Gemini API** (via the modern `google-genai` SDK), **ChromaDB Vector Store**, and **React 18 + Tailwind CSS**.

---

## 🌟 Key Features

1. **Real-Time Streaming over WebSocket**: Token-by-token streaming generation with sub-second time-to-first-token (TTFT).
2. **LLM Powered by Gemini**:
   - `gemini-2.5-flash` for high-speed streaming conversations and structured JSON NLP extraction.
   - `gemini-2.5-pro` for deep complaints and complex escalations.
   - `text-embedding-004` for semantic vector search.
3. **Structured NLP Pipeline**:
   - Automatic intent detection: `ORDER_STATUS`, `REFUND_REQUEST`, `BILLING_INQUIRY`, `TECHNICAL_SUPPORT`, `COMPLAINT`, `GENERAL_FAQ`, `HUMAN_ESCALATION`, `OUT_OF_SCOPE`.
   - Real-time sentiment analysis scoring from `-1.0` (Critical/Furious) to `+1.0` (Delighted).
   - Entity extraction (`order_id`, email, products) and language detection (English, Spanish, French, German).
4. **Automated Human Escalation**:
   - Detects `VERY_NEGATIVE` sentiment or direct escalation demands.
   - Automatically provisions and tracks a high-priority support ticket in the database.
   - Alerts the customer with ticket reference and live agent routing banner.
5. **RAG Knowledge Base**:
   - Grounded in company policy Markdown files located in `/data/knowledge_base`.
   - Cosine similarity matching via ChromaDB with strict grounding guardrails against hallucinations.
6. **Function Calling & Tools**:
   - `check_order_status(order_id)`: Real-time parcel tracking, carrier, and ETA lookup.
   - `create_ticket(summary, priority, reason)`: Persistent ticket logging.
   - `get_faq(topic)`: Quick policy retrieval.
7. **Comprehensive Guardrails & Security**:
   - Automatic PII masking for emails, credit cards, SSNs, and phone numbers in logs.
   - Prompt injection and harmful request refusal boundaries.
   - Session sliding-window rate limiting.
8. **Admin Telemetry & Analytics Dashboard**:
   - Live KPI overview (Total conversations, escalation rate, tickets, average sentiment).
   - Intent and sentiment distribution visual charts.
   - Ticket management queue (mark tickets In Progress or Resolved).
   - Full conversation transcript inspector.

---

## 🚀 Quick Start Guide

### Prerequisites
- Python 3.11+
- Node.js 18+ & npm
- A Google Gemini API Key from [Google AI Studio](https://aistudio.google.com/)

### 1. Configuration
Copy `.env.example` to `.env` and insert your Gemini API key:
```bash
cp .env.example .env
```
Edit `.env`:
```ini
GEMINI_API_KEY=your_actual_gemini_api_key_here
GEMINI_CHAT_MODEL=gemini-2.5-flash
GEMINI_COMPLEX_MODEL=gemini-2.5-pro
GEMINI_EMBEDDING_MODEL=text-embedding-004
```

### 2. Backend Setup
Create and activate a virtual environment, then install dependencies:
```bash
python -m venv .venv

# On Windows:
.\.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
```

Start the FastAPI backend server:
```bash
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
```
The backend API and WebSocket server will run on `http://localhost:8000`.
- Health check: `http://localhost:8000/health`
- Admin metrics: `http://localhost:8000/api/admin/metrics`

### 3. Frontend Setup
In a separate terminal:
```bash
cd frontend
npm install
npm run dev
```
Open your browser at `http://localhost:5173`.

---

## 🐳 Docker Deployment

Run the entire application in Docker with Docker Compose:
```bash
docker-compose up --build
```
Access the application on `http://localhost:8000`.

---

## 🧪 Running Unit Tests

Run the test suite with `pytest`:
```bash
pytest tests/ -v
```
Included test suites:
- `tests/test_nlp.py`: Sentiment polarity, intent classification, entity extraction.
- `tests/test_guardrails.py`: PII masking (email, phone, card) and prompt injection refusal.
- `tests/test_tools.py`: Order lookup, ticket generation, and mock FAQ retrieval.
- `tests/test_rag.py`: Knowledge base chunking and embedding logic.

---

## 📂 Project Structure

```
Real time chatbot/
├── backend/
│   └── app/
│       ├── main.py              # FastAPI app & WebSocket handler
│       ├── core/                # Config, Guardrails (PII), Rate limiting
│       ├── db/                  # SQLite models and async session
│       ├── nlp/                 # Gemini JSON analysis & fallback heuristics
│       ├── rag/                 # ChromaDB indexing, embedding, and chunking
│       ├── tools/               # Order status, ticket creation, mock database
│       ├── services/            # Gemini client & turn orchestrator
│       └── api/                 # Admin dashboard REST endpoints
├── frontend/
│   ├── src/
│   │   ├── components/Chat/     # Chat UI, streaming text, prompt chips, badges
│   │   ├── components/Admin/    # Admin metrics, charts, ticket resolution
│   │   └── hooks/               # WebSocket streaming hook
├── data/
│   ├── knowledge_base/          # Markdown files for RAG
│   └── chatbot.db               # SQLite database (auto-created)
├── tests/                       # Pytest test suite
├── Dockerfile
├── docker-compose.yml
└── README.md
```
