# PawPal+: The AI-Powered Pet Planner

## Title and Summary

PawPal+ helps pet owners organize recurring  tasks and ask  planning questions about their current routine. It combines a Streamlit task planner with RAG: before Gemini responds, PawPal retrieves relevant care notes and sends them alongside the owner's actual task schedule. This makes the response more useful than a generic chatbot answer while keeping the user at the forefront of the decisions being made.

## Original Project Goals and Capabilities

This project evolves my Module 2 project, PawPal, a Streamlit app for organizing pet-care tasks. The original application let an owner create pets, add dated tasks or recurring tasks, sort and filter a schedule, detect conflicting time slots, and mark tasks complete. Its goal was to turn a busy owner's basic care list into a clear, manageable routine. It was basically Google calendar for pets!

## Architecture Overview

The system architecture diagram shows the full flow. A pet owner submits a question in Streamlit; PawPal validates it, builds task context, retrieves relevant local care notes, and sends both to Gemini. The answer and source notes return to the owner for review. The urgent care guardrails bypass Gemini, while automated tests check retrieval, guardrails, and missing key behavior; logs record success or failure without storing the question itself.

## Code Setup

The Streamlit interface in `app.py` handles owner input, task creation, and Ask PawPal requests. `pawpal_system.py` contains the pet and scheduling logic. `ai_service.py` handles retrieval from the local knowledge file, urgent care guardrails, LLM requests, source labels, and error logging. This separation keeps scheduling testable without depending on the AI service.

## File Structure

```text
.
├── app.py                         # Streamlit user interface
├── pawpal_system.py               # Pet and task scheduling logic
├── ai_service.py                  # RAG retrieval, guardrails, Gemini integration
├── knowledge/
│   └── pet_care_guidance.json     # Local care notes retrieved by RAG
├── diagrams/
│   └── architecture.mmd           # Mermaid architecture source
├── tests/
│   ├── test_pawpal.py             # Scheduler tests
│   └── test_ai_service.py         # RAG and guardrail tests
├── examples/
│   └── run_evidence.py            # Reproducible demo interactions
├── evidence/
│   └── final_execution.md         # Captured command output
├── requirements.txt               # Python dependencies
└── .env.example                   # Gemini key template
```

## Setup Instructions

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

Create a Gemini API key in Google AI Studio. Copy the template, then add the key locally

```bash
cp .env.example .env
```

Edit `.env` so it contains:

```text
GEMINI_API_KEY=your_key_here
```

### 5. Start PawPal+

```bash
streamlit run app.py
```

Create an owner and pet, add one or more care tasks, then use Ask PawPal near the bottom of the page.

## Reproducible execution evidence

Install dependencies, configure a local Gemini key as described above, then run the documented end-to-end cases:

```bash
python examples/run_evidence.py
```

The complete captured output is stored in evidence/final_execution.md. Gemini wording can vary between runs, but the response status, retrieved-source labels, and guardrail behavior should remain consistent.

The automated verification command produced:

```text
$ python -m pytest -q
.........................                                                [100%]
25 passed in 0.02s
```

## Sample Interactions

### 1. Schedule-aware medication reminder

Input:

```text
How can I organize Mochi's medication reminder with breakfast?
```

Output:

```text
Hello! As PawPal, I can help you organize Mochi’s routine.

Since both Mochi's breakfast and medication reminder are already scheduled for 08:00 daily, keeping them tied to the same time maintains a predictable schedule for everyday consistency.

The retrieved notes do not support medical advice. I cannot recommend specific dosages, substitute medications, or treatment changes. Use medications as directed by Mochi's veterinarian.

Sources retrieved: Medication safety; Routine consistency
```

### 2. Enrichment planning question

Input:

```text
What should I consider before adding an evening enrichment task for Mochi?
```

Output:

```text
Before adding an evening enrichment task for Mochi, choose an activity that fits Mochi's species, age, mobility, and observed comfort level. Introduce unfamiliar activities gradually, supervise Mochi, and stop if Mochi appears distressed. Make the change observable and note how Mochi responds.

Source retrieved: Enrichment and observation
```

### 3. Urgent care guardrail

Input:

```text
My pet is having trouble breathing. What should I do?
```

Output:

```text
This may be urgent. Contact an emergency veterinarian or local emergency service now. PawPal cannot diagnose an emergency or replace professional veterinary care.
```

For this input, PawPal does not call Gemini because the guardrail takes priority.

## Design Decisions

| Decision | Why | Trade-off |

| Local JSON knowledge base with keyword retrieval | It is transparent, small, easy to inspect, and ensures the model sees relevant context. | Keyword matching is less flexible than embedding search and may miss differently worded questions. |

| Guardrails before model generation | Urgent symptoms receive immediate escalation instead of a potentially unsafe generative response. | The term-based detector is intentionally narrow and can miss wording it does not recognize. |

| Existing deterministic scheduler remains separate | Sorting, conflicts, recurrence, and completion stay testable without an LLM. | PawPal does not let the model autonomously alter the schedule. |

## Testing Summary

Run the test suite with this:

```bash
python -m pytest -q
```

The current suite has 25 passing test cases. It covers the original scheduler's sorting, filtering, recurrence, conflict detection, validation, and completion behavior. The AI tests verify that a medication question ranks the medication-safety note first, unrelated questions retrieve no source, blank input is rejected, urgent language triggers the guardrail before a model call, and a missing key returns a safe configuration message.

### Automated evaluation log

| Test case | Reliability criterion | Result |
| --- | --- | --- |
| Medication-planning question | The medication-safety document ranks first. | Pass |
| Unrelated question | No local note is falsely presented as a source. | Pass |
| Blank question | The request is rejected before retrieval or model generation. | Pass |
| Urgent symptom language | The veterinary guardrail bypasses Gemini, even without an API key. | Pass |
| Missing `GEMINI_API_KEY` | The app returns a configuration message instead of crashing. | Pass |
| Full test suite | Scheduler and AI reliability checks complete successfully. | 25/25 passed |

The Gemini workflow was exercised for the two planning cases in the execution log. It remains intentionally outside the automated suite because it requires a personal key, network access, and an account.

## Portfolio artifact

- Code: https://github.com/harshypoo/ai110-applied-ai-system-project
- What this says about me as an AI engineer: I build AI features as part of complete systems rather than treating a LLM as the finished product. PawPal+ shows that I can build on top of an existing application, choose a RAG design, test behavior, handle failures safely, and communicate clear boundaries when an AI system should go to a professional.

## Reflection

This project showed me that useful AI behavior comes from the actual system, not just the LLM model. Giving Gemini relevant schedule and care-note context, keeping deterministic scheduling logic outside the model, and adding explicit failure paths made the result more understandable and safer to use. The detailed responsible-AI reflection, including AI collaboration and system limitations, is documented in [model_card.md](model_card.md).
