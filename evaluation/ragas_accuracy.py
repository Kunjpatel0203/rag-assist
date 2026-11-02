from __future__ import annotations


class RagasAccuracyError(RuntimeError):
    """Raised when answer-accuracy scoring cannot be completed."""


def score_answer_accuracy(question: str, answer: str, reference: str) -> float:
    """
    Score a generated answer against a reference using Ragas Answer Accuracy.

    This metric requires a user question, the model response, and a ground-truth
    reference answer. Imports are intentionally lazy so the main application can
    still run even if `ragas` has not been installed yet.
    """

    if not question or not question.strip():
        raise ValueError("question is required for ragas accuracy")
    if not answer or not answer.strip():
        raise ValueError("answer is required for ragas accuracy")
    if not reference or not reference.strip():
        raise ValueError("reference is required for ragas accuracy")

    try:
        from openai import AsyncOpenAI
        from ragas.llms import llm_factory
        from ragas.metrics.collections import AnswerAccuracy
    except ImportError as exc:
        raise RagasAccuracyError(
            "ragas is not installed. Install the dependencies in requirements.txt "
            "to enable ragas answer accuracy scoring."
        ) from exc

    try:
        client = AsyncOpenAI()
        llm = llm_factory("gpt-4o-mini", client=client)
        scorer = AnswerAccuracy(llm=llm)
        result = scorer.score(
            user_input=question,
            response=answer,
            reference=reference,
        )
    except Exception as exc:
        raise RagasAccuracyError(f"failed to score answer accuracy: {exc}") from exc

    value = getattr(result, "value", result)
    return float(value)
