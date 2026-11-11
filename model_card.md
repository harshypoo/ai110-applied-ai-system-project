# PawPal+ Model Card and Responsible-AI Reflection

## What are the limitations or biases in your system?

- Small knowledge base: The retrieval system contains only a few short, general notes. It cannot represent the full range of questions that may be asked.
- Keyword retrieval bias: Retrieval uses keyword overlap rather than semantic embeddings. A differently worded question may not be answered the same way as the original question.
- Model changes: Gemini can phrase equivalent answers differently from run to run and can still produce an unsupported statement despite the prompt and retrieved sources.
- Unequal applicability: General routine and enrichment guidance may be less applicable to pets with mobility limitations, chronic conditions, unusual schedules, or such. The system should not treat a generic answer as personalized advice.
- Model limits: Live model use depends on a valid Gemini key, network access, rate limits, and more.

## Could your AI be misused, and how would you prevent that?

The largest misuse is treating PawPal+ like a doctor; for example, asking it to diagnose symptoms, choose a medication dose, or decide whether an emergency can wait. The system reduces that risk by using an explicit safety statement, instructing the model not to give diagnoses or doseage/treatment advice, displaying the retrieved source notes, and routing recognized urgent symptoms such as trouble breathing, collapse, seizures, bleeding, or suspected poisoning to emergency veterinary help before a model request is made.

The guardrail is conservative but incomplete: it is term-based and cannot recognize every dangerous phrasing or situation. It's up to the user to make the professional decision. PawPal+ also avoids logging the question text; it logs only event outcomes and source counts to reduce unnecessary retention of personal details.

## What surprised you while testing your AI's reliability?

The project currently has 25 passing automated tests. They cover the original scheduling logic as well as retrieval ranking, absent context, blank input, urgent care escalation, and missing key behavior. The tests showed that reliability improves when the AI feature is separated into small deterministic steps: retrieve notes first, validate safety conditions before generating, and return a clear configuration or error message instead of crashing.

One surprise was that a medication question can retrieve both the medication safety note and the routine consistency note. An early test expected exactly one result and failed, even though the medication note correctly ranked first. I revised the test to check the important behavior-correct ranking rather than enforcing a narrow result set. Gemini output remains the least tested part because it depends on an API key and can vary.

## Describe your collaboration with AI during this project. Identify one suggestion you accepted and one you did not accept as written, and say why you rejected or changed it.

I used an AI coding assistant to help examine the existing PawPal+ codebase, plan the applied-AI extension, draft implementation changes, and generate tests and documentation.

### One suggestion I accepted

I accepted the suggestion to use a RAG approach. Keeping a small local knowledge base separate from the model made source display, testing, and safety boundaries easier to understand than a generic chatbot implementation.

### One suggestion I rejected or revised

I did not keep the first provider suggestion as written. The initial plan used an OpenAI API integration, but I revised the implementation to use Gemini because the project needed a free tier option. I also kept retrieval as a simple local keyword matcher instead of adding embeddings or an autonomous agent. That choice is easier to understand, and it is easier to inspect, test, and explain for this project.

## Future Improvements

- Expand the local knowledge base with more information to answer questions
- Compare semantic retrieval with the current keyword retrieval while keeping displayed sources transparent
- Add human review for Gemini responses, including safety criteria

