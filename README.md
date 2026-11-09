# PawPal+ — RAG Pet-Care Planning Assistant

PawPal+ helps pet owners organize recurring care tasks and ask grounded planning questions about their current routine. It combines a Streamlit task planner with retrieval-augmented generation (RAG): before Gemini responds, PawPal retrieves relevant local care notes and sends them alongside the owner's actual task schedule. This makes the response more useful than a generic chatbot answer while keeping the original scheduler at the center of the experience.

> **Safety note:** PawPal+ is a planning aid, not veterinary medical advice. It does not diagnose conditions, recommend medication doses, or advise treatment changes. Urgent symptoms should be handled by a licensed veterinarian or emergency veterinary service.

## Original project: Module 2 PawPal+ scheduler

This project evolves my Module 2 project, **PawPal+**, a Streamlit app for organizing pet-care tasks. The original application let an owner create pets, add dated one-time or recurring tasks, sort and filter a schedule, detect conflicting time slots, and mark tasks complete. Its goal was to turn a busy owner's basic care list into a clear, manageable routine.

## What changed in the applied-AI version

- **Ask PawPal:** An owner can ask a planning question directly in the app.
- **Integrated RAG:** `ai_service.py` retrieves relevant notes from `knowledge/pet_care_guidance.json` before Gemini generates an answer.
- **Schedule-aware responses:** The model receives the active owner's current tasks, so it can frame the answer around the schedule the user created.
- **Transparent sources:** The app displays the retrieved notes below each response.
- **Safety and resilience:** Urgent symptom terms bypass generation, missing keys and API failures produce useful messages, and the service logs outcomes without logging question text.

## Architecture overview

The [system architecture diagram](diagrams/architecture.mmd) shows the full flow. A pet owner submits a question in Streamlit; PawPal validates it, builds task context, retrieves relevant local care notes, and sends both to Gemini 2.5 Flash. The answer and source notes return to the owner for review. Urgent-care guardrails bypass Gemini, while automated tests check retrieval, guardrails, and missing-key behavior; logs record success or failure without storing the question itself.

## Project structure

```text
.
├── app.py                         # Streamlit interface
├── pawpal_system.py               # Original task scheduling domain logic
├── ai_service.py                  # RAG retrieval, guardrails, logging, Gemini call
├── knowledge/
│   └── pet_care_guidance.json     # Curated retrieval documents
├── diagrams/
│   └── architecture.mmd           # Mermaid system diagram source
├── tests/
│   ├── test_pawpal.py             # Scheduler tests
│   └── test_ai_service.py         # RAG and safety tests
├── .env.example                   # Safe environment-variable template
└── requirements.txt
```

## Setup and run

### 1. Clone the repository

```bash
git clone https://github.com/harshypoo/ai110-applied-ai-system-project.git
cd ai110-applied-ai-system-project
```

### 2. Create and activate a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate
```

On Windows PowerShell, use:

```powershell
.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Gemini

Create a Gemini API key in Google AI Studio. Copy the template, then add the key locally:

```bash
cp .env.example .env
```

Edit `.env` so it contains:

```text
GEMINI_API_KEY=your_key_here
```

`.env` is ignored by Git; never commit or share the key. Without a key, the scheduler and retrieval preview work, but Ask PawPal displays a configuration message instead of calling Gemini.

### 5. Start PawPal+

```bash
streamlit run app.py
```

Create an owner and pet, add one or more care tasks, then use **Ask PawPal** near the bottom of the page.

## Sample interactions

Gemini wording can vary between runs. These examples show the expected behavior and the schedule/source context that PawPal provides.

### 1. Schedule-aware medication reminder

**Input**

```text
How can I organize Mochi's medication reminder with breakfast?
```

**Example result**

```text
If Mochi already has breakfast scheduled, keep the medication reminder at that same routine point only if that matches the veterinarian's instructions. Add a separate, clearly named medication task so it can be marked complete independently. PawPal can help you avoid a duplicate time-slot conflict, but contact the prescribing veterinarian if you missed a dose or need medication guidance.

Sources retrieved: Medication safety; Routine consistency
```

### 2. Enrichment planning question

**Input**

```text
What should I consider before adding an evening enrichment task for Biscuit?
```

**Example result**

```text
Review Biscuit's existing evening tasks first, then choose an activity that matches Biscuit's species, age, mobility, and comfort. Start with a short supervised activity and adjust based on how Biscuit responds. Add it as a separate one-time or recurring task so the plan stays visible.

Source retrieved: Enrichment and observation
```

### 3. Urgent-care guardrail

**Input**

```text
My pet is having trouble breathing. What should I do?
```

**Result**

```text
This may be urgent. Contact an emergency veterinarian or local emergency service now. PawPal cannot diagnose an emergency or replace professional veterinary care.
```

For this input, PawPal does **not** call Gemini; the guardrail takes priority.

## Design decisions and trade-offs

| Decision | Why | Trade-off |
| --- | --- | --- |
| Local JSON knowledge base with keyword retrieval | It is transparent, small, easy to inspect, and ensures the model sees relevant project-provided context. | Keyword matching is less flexible than embedding search and may miss differently worded questions. |
| Gemini 2.5 Flash | It provides a fast, accessible text-generation option for a student project. | A live response requires an API key and depends on provider availability and limits. |
| Guardrails before model generation | Urgent symptoms receive immediate escalation instead of a potentially unsafe generative response. | The term-based detector is intentionally narrow and can miss wording it does not recognize. |
| Source display | It lets the owner inspect the notes that grounded the response. | The local notes are brief and are not a substitute for individualized veterinary advice. |
| Existing deterministic scheduler remains separate | Sorting, conflicts, recurrence, and completion stay testable without an LLM. | PawPal does not let the model autonomously alter the schedule. |

## Testing and reliability summary

Run the complete automated suite with:

```bash
python -m pytest -q
```

The current suite has **25 passing tests**. It covers the original scheduler's sorting, filtering, recurrence, conflict detection, validation, and completion behavior. The AI tests verify that a medication question ranks the medication-safety note first, unrelated questions retrieve no source, blank input is rejected, urgent language triggers the guardrail before a model call, and a missing key returns a safe configuration message.

### Automated evaluation log

| Test case | Reliability criterion | Automated result |
| --- | --- | --- |
| Medication-planning question | The medication-safety document ranks first. | Pass |
| Unrelated question | No local note is falsely presented as a source. | Pass |
| Blank question | The request is rejected before retrieval or model generation. | Pass |
| Urgent symptom language | The veterinary guardrail bypasses Gemini, even without an API key. | Pass |
| Missing `GEMINI_API_KEY` | The app returns a configuration message instead of crashing. | Pass |
| Full test suite | Scheduler and AI reliability checks complete successfully. | 25/25 passed |

The intentionally unautomated portion is the live Gemini request: it requires a personal key, network access, and an active provider account. This is a limitation of the current evaluation approach; a future version should add recorded, human-reviewed test cases for live outputs and measure retrieval quality across a larger question set.

## Brief reflection

This project showed me that useful AI behavior comes from the surrounding system, not just the model call. Giving Gemini relevant schedule and care-note context, keeping deterministic scheduling logic outside the model, and adding explicit failure paths made the result more understandable and safer to use. The detailed responsible-AI reflection, including AI collaboration and system limitations, is documented in [model_card.md](model_card.md).

## License and attribution

This is a student project built as an evolution of the original Module 2 PawPal+ scheduler. The pet-care notes are intentionally short, curated planning guidance and should not be treated as medical sources.
