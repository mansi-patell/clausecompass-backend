# ClauseCompass — Backend

AI-powered contract review API. Upload a lease, NDA, or freelance agreement and get clause-level risk analysis in plain English, plus a chat interface to ask grounded questions about the document.

**Live API:** https://clausecompass-backend.onrender.com/docs

**Frontend repo:** https://github.com/mansi-patell/clausecompass-frontend

## What it does

- Extracts text from uploaded PDF or DOCX contracts
- Sends the text to Claude with a structured prompt that returns clause-level risk flags (low/medium/high), explanations in plain English, and a list of standard protections missing from the document
- Supports follow-up questions via a chat endpoint, grounded in the actual contract text, with session-based conversation memory

## Why it's built this way

The core design decision is forcing the LLM to return structured JSON (rather than a free-text summary) so the risk analysis can be rendered as an actual UI — color-coded cards, categorized clauses — instead of a wall of text the user has to read through. This also makes the output testable and consistent across different contract types.

For the chat feature, the full contract text is passed as context on every turn instead of using a vector database. At the scale of a single contract (a few pages), this is simpler and more reliable than chunking and retrieval. For much longer documents, a real RAG pipeline (chunking + embeddings + retrieval) would be the next step — noted as a known scaling limitation.

## Tech stack

- **FastAPI** — web framework
- **Claude API** (Anthropic) — risk analysis + chat, using `claude-haiku-4-5` for cost efficiency
- **pypdf / python-docx** — text extraction

## API Endpoints

- `POST /upload` — accepts a PDF or DOCX file, returns a session ID and full risk analysis
- `POST /chat/{session_id}` — accepts a question, returns a grounded answer referencing the uploaded contract

## Running locally

```bash
python -m venv venv
venv\Scripts\activate       # Windows
pip install -r requirements.txt
```

Create a `.env` file:

ANTHROPIC_API_KEY=your_key_here

Run the server:
```bash
uvicorn main:app --reload
```

Visit `http://127.0.0.1:8000/docs` for interactive API docs.

## Known limitations / next steps

- In-memory session storage (resets on server restart) — would move to Firebase/Supabase for production use
- Full-document-in-context chat works well for short contracts; longer documents would need real RAG (chunking + embeddings)
- No redline/rewrite suggestions yet — currently flags risk but doesn't suggest fairer alternative language