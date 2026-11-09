# PawPal+ Final Presentation

Use this seven-slide outline for a 5–7 minute presentation. The live demo should show the Streamlit interface and Ask PawPal section; do not show the API key or `.env` file.

## Slide 1 — PawPal+ RAG Pet-Care Planning Assistant (0:40)

PawPal+ helps pet owners manage recurring tasks and ask schedule-aware planning questions. The project extends my Module 2 PawPal+ scheduler with retrieval-augmented generation and safety guardrails.

## Slide 2 — The original project and the problem (0:45)

The original PawPal+ app let an owner create pets, schedule one-time or recurring care tasks, mark tasks complete, filter schedules, and detect time conflicts. The missing capability was help interpreting the schedule in the context of care guidance.

## Slide 3 — System architecture (0:55)

Show `diagrams/architecture.mmd`. Explain the flow: owner question, validation, schedule-context building, local-note retrieval, Gemini response, and source display. Point out that urgent questions exit through the guardrail rather than the model.

## Slide 4 — Live demo: source-grounded planning (1:20)

Create Mochi, then add Breakfast and Medication reminder at 08:00. Ask: “How can I organize Mochi's medication reminder with breakfast?” Show the response and the retrieved Medication safety and Routine consistency notes. Explain that the model receives both the schedule and retrieved notes.

## Slide 5 — Live demo: safety behavior (0:50)

Ask: “My pet is having trouble breathing. What should I do?” Show the urgent-care message. Explain that PawPal+ bypasses Gemini here so it does not generate a diagnosis or a medication recommendation.

## Slide 6 — Reliability evidence and limitations (0:55)

Show the README evaluation table and `evidence/final_execution.md`. State that 25 automated tests pass. Mention the checks for relevant retrieval, absent context, blank input, urgent symptoms, and missing API keys. Explain that keyword retrieval and a small local corpus remain limitations.

## Slide 7 — What I learned (0:45)

The model call is only one component of the system. The project became more dependable by retrieving inspectable context, separating deterministic scheduling logic from generation, and defining a clear boundary for medical questions. Close with the GitHub repository: https://github.com/harshypoo/ai110-applied-ai-system-project
