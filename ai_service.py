"""Retrieval, guardrails, and Gemini integration for Ask PawPal."""

from __future__ import annotations

from dataclasses import dataclass
import json
import logging
import os
from pathlib import Path
import re

from dotenv import load_dotenv

from pawpal_system import Owner, Scheduler


LOGGER = logging.getLogger("pawpal.ai")
KNOWLEDGE_PATH = Path(__file__).with_name("knowledge") / "pet_care_guidance.json"
MODEL_NAME = "gemini-3.5-flash-lite"
URGENT_TERMS = {
    "bleeding",
    "collapse",
    "collapsed",
    "difficulty breathing",
    "poison",
    "poisoning",
    "seizure",
    "seizures",
    "trouble breathing",
    "unconscious",
}


@dataclass(frozen=True)
class KnowledgeDocument:
    """A small, local document used as grounded context for the model."""

    document_id: str
    title: str
    content: str


@dataclass(frozen=True)
class AIResponse:
    """A safe response plus transparent retrieval metadata for the UI."""

    answer: str
    sources: list[KnowledgeDocument]
    status: str


def load_knowledge_base(path: Path = KNOWLEDGE_PATH) -> list[KnowledgeDocument]:
    """Load the curated local knowledge base used by the RAG workflow."""
    with path.open(encoding="utf-8") as file:
        records = json.load(file)
    return [
        KnowledgeDocument(record["id"], record["title"], record["content"])
        for record in records
    ]


def tokenize(text: str) -> set[str]:
    """Return lowercase words suitable for lightweight local retrieval."""
    return set(re.findall(r"[a-z]{2,}", text.casefold()))


def retrieve_knowledge(
    question: str, documents: list[KnowledgeDocument], limit: int = 3
) -> list[KnowledgeDocument]:
    """Return the most relevant local documents before calling the model."""
    query_terms = tokenize(question)
    ranked = [
        (len(query_terms & tokenize(f"{document.title} {document.content}")), document)
        for document in documents
    ]
    return [document for score, document in sorted(ranked, reverse=True, key=lambda item: item[0]) if score][:limit]


def requires_urgent_veterinary_help(question: str) -> bool:
    """Detect a small set of urgent symptoms that should bypass model output."""
    normalized_question = question.casefold()
    return any(term in normalized_question for term in URGENT_TERMS)


def build_task_context(owner: Owner, scheduler: Scheduler) -> str:
    """Build concise, non-sensitive schedule context for an Ask PawPal request."""
    tasks = scheduler.sort_by_time(scheduler.retrieve_tasks(owner))[:20]
    if not tasks:
        return "No care tasks have been added yet."
    return "\n".join(
        f"- {task.scheduled_date.isoformat()} {task.time}: {task.pet_name} — "
        f"{task.description} ({task.frequency}; "
        f"{'complete' if task.completed else 'incomplete'})"
        for task in tasks
    )


def ask_pawpal(question: str, owner: Owner, scheduler: Scheduler) -> AIResponse:
    """Retrieve relevant notes, apply guardrails, then ask Gemini for a grounded answer."""
    cleaned_question = question.strip()
    if not cleaned_question:
        return AIResponse("Enter a pet-care planning question first.", [], "invalid_input")

    if requires_urgent_veterinary_help(cleaned_question):
        LOGGER.warning("ask_pawpal_guardrail outcome=urgent_query_length=%d", len(cleaned_question))
        return AIResponse(
            "This may be urgent. Contact an emergency veterinarian or local emergency service now. "
            "PawPal cannot diagnose an emergency or replace professional veterinary care.",
            [],
            "guardrail",
        )

    sources = retrieve_knowledge(cleaned_question, load_knowledge_base())
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        LOGGER.info("ask_pawpal_configuration_needed source_count=%d", len(sources))
        return AIResponse(
            "Ask PawPal is ready, but Gemini is not configured. Add GEMINI_API_KEY to a local "
            ".env file, then restart Streamlit.",
            sources,
            "configuration_needed",
        )

    source_text = "\n\n".join(
        f"Source: {source.title}\n{source.content}" for source in sources
    ) or "No relevant local source was retrieved."
    prompt = f"""User question: {cleaned_question}

Current PawPal schedule:
{build_task_context(owner, scheduler)}

Retrieved care notes:
{source_text}

Answer as PawPal, a pet-care planning assistant. Use the schedule and retrieved notes, and say when the notes do not support an answer. Do not diagnose, recommend medication doses, or advise changing prescribed treatment. Encourage a veterinarian for medical concerns. Give a concise, practical response."""

    try:
        from google import genai
        from google.genai import types

        client = genai.Client(
            api_key=api_key,
            http_options=types.HttpOptions(timeout=20_000),
        )
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
            config=types.GenerateContentConfig(temperature=0.2, max_output_tokens=350),
        )
        answer = (response.text or "Gemini returned no text. Please try again.").strip()
        LOGGER.info("ask_pawpal_success source_count=%d", len(sources))
        return AIResponse(answer, sources, "ok")
    except Exception:
        LOGGER.exception("ask_pawpal_model_error source_count=%d", len(sources))
        return AIResponse(
            "Ask PawPal could not reach Gemini right now. Check your API key, connection, and "
            "Gemini usage limits, then try again.",
            sources,
            "model_error",
        )


load_dotenv()
