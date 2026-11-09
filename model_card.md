# PawPal+ Model Card and Responsible-AI Reflection

## System purpose and scope

PawPal+ is a pet-care planning assistant built on top of the original deterministic PawPal+ scheduler. Its Ask PawPal feature retrieves short, curated local care notes and combines them with the owner's current task schedule before sending a planning question to Gemini 3.5 Flash-Lite. It is designed to help an owner organize routine care; it is not designed to diagnose illness, prescribe medication, or replace professional veterinary care.

## Limitations and potential biases

- **Small knowledge base:** The retrieval corpus contains only a few short, general pet-care notes. It cannot represent the full range of species, breeds, ages, disabilities, medical histories, or veterinary guidance.
- **Keyword retrieval bias:** Retrieval uses keyword overlap rather than semantic embeddings. A differently worded question may fail to retrieve a useful note, while a question sharing a word with a note may retrieve only loosely related context.
- **Model variability:** Gemini can phrase equivalent answers differently from run to run and can still produce an unsupported statement despite the prompt and retrieved sources.
- **Simplified user context:** PawPal+ knows task names, dates, times, frequency, pet name, species, and age; it does not know a pet's medical history, veterinarian instructions, allergies, behavior history, or household context.
- **Unequal applicability:** General routine and enrichment guidance may be less applicable to pets with mobility limitations, chronic conditions, unusual schedules, or limited access to veterinary care. The system should not treat a generic answer as individualized advice.
- **Availability limits:** Live model use depends on a valid Gemini key, network access, and provider availability or rate limits.

## Misuse risks and mitigations

The largest misuse risk is treating PawPal+ like a veterinary authority—for example, asking it to diagnose symptoms, choose a medication dose, or decide whether an emergency can wait. The system reduces that risk by using an explicit safety statement, instructing the model not to give diagnoses or dose/treatment-change advice, displaying the retrieved source notes, and routing recognized urgent symptoms such as trouble breathing, collapse, seizures, bleeding, or suspected poisoning to emergency veterinary help before a model request is made.

The guardrail is intentionally conservative but incomplete: it is term-based and cannot recognize every dangerous phrasing or situation. Owners must still use professional judgment and contact a licensed veterinarian for health concerns. PawPal+ also avoids logging the question text; it logs only event outcomes and source counts to reduce unnecessary retention of personal details.

## Reliability observations

The project currently has 25 passing automated tests. They cover the original deterministic scheduling logic as well as retrieval ranking, absent context, blank input, urgent-care escalation, and missing-key behavior. The tests showed that reliability improves when the AI feature is separated into small deterministic steps: retrieve notes first, validate safety conditions before generating, and return a clear configuration or error message instead of crashing.

One surprise was that a medication question can reasonably retrieve both the medication-safety note and the routine-consistency note. An early test expected exactly one result and failed, even though the medication note correctly ranked first. I revised the test to check the important behavior—correct ranking—rather than enforcing an unnecessarily narrow result set. Live Gemini output remains the least-tested part because it depends on an external API and can vary; a future version should add structured human review of a larger set of live responses.

## Collaboration with AI

I used an AI coding assistant to help examine the existing PawPal+ codebase, plan the applied-AI extension, draft implementation changes, and generate tests and documentation. I accepted the suggestion to use a retrieval-augmented approach: keeping a small local knowledge base separate from the model made source display, testing, and safety boundaries easier to understand than a generic chatbot implementation.

I did not keep the first provider suggestion as written. The initial plan used an OpenAI API integration, but I changed the implementation to Gemini 2.5 Flash because the project needed a free-tier-friendly option. I also kept retrieval as a simple local keyword matcher instead of adding embeddings or an autonomous agent. That choice is less sophisticated, but it is easier to inspect, test, and explain for this project's scope.

## Future improvements

- Expand the curated knowledge base with veterinarian-reviewed, cited material.
- Replace keyword matching with evaluated semantic retrieval while retaining transparent source display.
- Add a structured human-evaluation set for live Gemini answers, including safety and groundedness criteria.
- Let owners correct or rate answers without storing sensitive question text by default.
- Add configurable safety policies for species-specific and medication-related questions.
