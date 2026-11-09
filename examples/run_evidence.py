"""Run three documented PawPal+ interactions for reproducible final evidence."""

from ai_service import ask_pawpal
from pawpal_system import Owner, Pet, Scheduler, Task


def build_demo_owner() -> Owner:
    """Create the same small schedule used in the README evidence."""
    owner = Owner("Jordan")
    mochi = Pet("Mochi", "cat", 3)
    mochi.add_task(Task("Breakfast", "08:00", "daily"))
    mochi.add_task(Task("Medication reminder", "08:00", "daily"))
    owner.add_pet(mochi)
    return owner


def main() -> None:
    """Print two RAG responses and one emergency-guardrail response."""
    owner = build_demo_owner()
    scheduler = Scheduler()
    cases = [
        ("MEDICATION", "How can I organize Mochi's medication reminder with breakfast?"),
        ("ENRICHMENT", "What should I consider before adding an evening enrichment task for Mochi?"),
        ("URGENT", "My pet is having trouble breathing. What should I do?"),
    ]

    for label, question in cases:
        response = ask_pawpal(question, owner, scheduler)
        print(f"[{label}] status={response.status}")
        print(response.answer)
        print("sources=" + ", ".join(source.title for source in response.sources))
        print()


if __name__ == "__main__":
    main()
