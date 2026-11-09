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

The [system architecture diagram](diagrams/architecture.mmd) shows the full flow. A pet owner submits a question in Streamlit; PawPal validates it, builds task context, retrieves relevant local care notes, and sends both to Gemini 3.5 Flash-Lite. The answer and source notes return to the owner for review. Urgent-care guardrails bypass Gemini, while automated tests check retrieval, guardrails, and missing-key behavior; logs record success or failure without storing the question itself.

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

## Reproducible execution evidence

Install dependencies, configure a local Gemini key as described above, then run the documented end-to-end cases:

```bash
python examples/run_evidence.py
```

The complete captured output is stored in [evidence/final_execution.md](evidence/final_execution.md). Gemini wording can vary between runs, but the response status, retrieved-source labels, and guardrail behavior should remain consistent.

## Observed sample interactions

The following two live RAG outputs and guardrail output were captured with the documented demo schedule.

### 1. Schedule-aware medication reminder

**Input**

```text
How can I organize Mochi's medication reminder with breakfast?
```

**Observed output**

```text
Hello! As PawPal, I can help you organize Mochi’s routine.

Since both Mochi's breakfast and medication reminder are already scheduled for 08:00 daily, keeping them tied to the same time maintains a predictable schedule for everyday consistency.

The retrieved notes do not support medical advice. I cannot recommend specific dosages, substitute medications, or treatment changes. Use medications as directed by Mochi's veterinarian.

Sources retrieved: Medication safety; Routine consistency
```

### 2. Enrichment planning question

**Input**

```text
What should I consider before adding an evening enrichment task for Mochi?
```

**Observed output**

```text
Before adding an evening enrichment task for Mochi, choose an activity that fits Mochi's species, age, mobility, and observed comfort level. Introduce unfamiliar activities gradually, supervise Mochi, and stop if Mochi appears distressed. Make the change observable and note how Mochi responds.

Source retrieved: Enrichment and observation
```

### 3. Urgent-care guardrail

**Input**

```text
My pet is having trouble breathing. What should I do?
```

**Observed output**

```text
This may be urgent. Contact an emergency veterinarian or local emergency service now. PawPal cannot diagnose an emergency or replace professional veterinary care.
```

For this input, PawPal does **not** call Gemini; the guardrail takes priority.

## Design decisions and trade-offs

| Decision | Why | Trade-off |
| --- | --- | --- |
| Local JSON knowledge base with keyword retrieval | It is transparent, small, easy to inspect, and ensures the model sees relevant project-provided context. | Keyword matching is less flexible than embedding search and may miss differently worded questions. |
| Gemini 3.5 Flash-Lite | It provides a low-latency, accessible text-generation option for a student project. | A live response requires an API key and depends on provider availability and limits. |
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

The live Gemini workflow was manually exercised for the two planning cases in the execution log. It remains intentionally outside the automated suite because it requires a personal key, network access, and an active provider account. A future version should add a structured, human-reviewed set of live outputs and measure retrieval quality across a larger question set.

## Portfolio artifact

- **Code:** [github.com/harshypoo/ai110-applied-ai-system-project](https://github.com/harshypoo/ai110-applied-ai-system-project)
- **What this project says about me as an AI engineer:** I build AI features as part of complete systems rather than treating a model call as the finished product. PawPal+ shows that I can extend an existing application, choose an inspectable RAG design, test deterministic behavior, handle failures safely, and communicate clear boundaries when an AI system should defer to a professional.

## Presentation

See [presentation_outline.md](presentation_outline.md) for a timed 5–7 minute presentation and live-demo script. A Loom walkthrough can be added here later for human reviewers; grading evidence is included in this README and the linked execution log.

## Brief reflection

This project showed me that useful AI behavior comes from the surrounding system, not just the model call. Giving Gemini relevant schedule and care-note context, keeping deterministic scheduling logic outside the model, and adding explicit failure paths made the result more understandable and safer to use. The detailed responsible-AI reflection, including AI collaboration and system limitations, is documented in [model_card.md](model_card.md).

## License and attribution

This is a student project built as an evolution of the original Module 2 PawPal+ scheduler. The pet-care notes are intentionally short, curated planning guidance and should not be treated as medical sources.
