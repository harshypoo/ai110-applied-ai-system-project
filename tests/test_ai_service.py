"""Reliability tests for PawPal's retrieval and safety guardrails."""

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from ai_service import (
    KnowledgeDocument,
    ask_pawpal,
    requires_urgent_veterinary_help,
    retrieve_knowledge,
)
from pawpal_system import Owner, Scheduler


def test_retrieval_selects_medication_safety_note() -> None:
    """Medication questions should retrieve the specifically relevant care note."""
    documents = [
        KnowledgeDocument("walks", "Walks", "Plan short dog walks."),
        KnowledgeDocument("meds", "Medication safety", "Follow veterinarian medication directions."),
    ]

    results = retrieve_knowledge("Can I change my pet medication dose?", documents)

    assert [document.document_id for document in results] == ["meds"]


def test_urgent_terms_trigger_a_veterinary_guardrail() -> None:
    """Urgent symptoms must be handled before a model request is attempted."""
    assert requires_urgent_veterinary_help("My dog has trouble breathing") is True
    assert requires_urgent_veterinary_help("When should I schedule a walk?") is False


def test_missing_key_returns_configuration_message(monkeypatch) -> None:
    """The app fails safely and still shows retrieved context before key setup."""
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)

    response = ask_pawpal("How should I handle a missed medication task?", Owner("Jordan"), Scheduler())

    assert response.status == "configuration_needed"
    assert "GEMINI_API_KEY" in response.answer
    assert response.sources[0].document_id == "medication-safety"
