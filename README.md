# rag-python-core

## Project structure

| Folder | What it is | Port |
|---|---|---|
| `/` (root) | Python RAG engine (FastAPI) | 8000 |
| `rag-platform/` | Spring Boot backend (auth, workspaces, chats) using MongoDB | 8080 |
| `valora-frontend/` | React + Vite frontend | 5173 |

## Running locally

Start MongoDB on `localhost:27017`, then run each part in its own terminal.

**1. Python RAG engine** (needs `OPENAI_API_KEY` in a `.env` file at the root)

```bash
python -m venv venv
venv/bin/pip install -r requirements.txt fastapi uvicorn python-multipart
venv/bin/python -m uvicorn rag_service:app --host 127.0.0.1 --port 8000
```

**2. Spring Boot backend**

```bash
cd rag-platform
cp secrets.properties.example secrets.properties   # then fill in real values
./mvnw spring-boot:run
```

**3. Frontend**

```bash
cd valora-frontend
npm install
npm run dev
```

Open http://localhost:5173.

## Ragas answer accuracy

This project now supports optional Ragas answer-accuracy scoring on the `/ask`
endpoint.

Install dependencies:

```bash
pip install -r requirements.txt
```

Send a normal question as before, and include `reference_answer` when you want
Ragas to score the generated response against a ground-truth answer:

```json
{
  "workspace_id": "c1",
  "question": "What is the policy renewal date?",
  "chatHistory": "",
  "reference_answer": "The policy renewal date is 31 March 2026."
}
```

When `reference_answer` is present, the response includes:

```json
{
  "answer": "...",
  "ragas_accuracy": 0.87,
  "ragas_metric": "answer_accuracy"
}
```
