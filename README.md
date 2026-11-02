# rag-python-core

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
