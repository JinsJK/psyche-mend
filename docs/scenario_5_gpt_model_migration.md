[SCENARIO 5 — GPT MODEL MIGRATION AND INTEGRATION ADAPTATION]

Objective:
Migrate the OpenAI integration from gpt-3.5-turbo to gpt-5.4-mini while adapting the system to the OpenAI v1.x SDK API changes and preserving the existing conversational pipeline behaviour.

Why This Scenario Was Chosen:
The prototype depends heavily on external AI services whose APIs, SDK interfaces, and supported models evolve continuously. A model migration represents a realistic maintenance activity in AI-powered systems because even a small update can introduce compatibility issues across dependencies, runtime environments, and integration layers.

This scenario evaluates:
- integration complexity
- maintainability implications
- dependency management effort
- debugging effort during AI service evolution

Scope:
- Replace gpt-3.5-turbo with gpt-5.4-mini
- Upgrade OpenAI SDK from v0.28.1 to v1.x
- Adapt API usage to the v1.x interface
- Preserve existing prompts, request flow, logging, and frontend behaviour
- Keep all other AI pipeline components unchanged

Files Changed:
requirements.txt                              — upgraded openai SDK pin
backend/response_gen.py                       — SDK migration, model constant, API call and response access pattern
main.py                                       — model string updated in both LLM log_event calls
docs/scenario_5_gpt_model_migration.md        — this document

Changes Implemented:

1. OpenAI SDK Migration
   Updated requirements.txt: openai==0.28.1 → openai>=1.0.0
   Replaced legacy SDK usage:
   Before:
   - import openai
   - openai.api_key = ...
   - openai.ChatCompletion.create(...)
   After:
   - from openai import OpenAI
   - client = OpenAI(...)
   - client.chat.completions.create(...)

2. Response Handling Update
   Updated response access pattern:
   Before: response.choices[0].message["content"]
   After:  response.choices[0].message.content

3. Model Migration
   Replaced: gpt-3.5-turbo
   With:     gpt-5.4-mini
   Added MODEL = "gpt-5.4-mini" to centralise the model identifier inside the integration module.

4. Logging Consistency
   Updated model references in main.py log_event() calls so runtime logs reflect the actual model in use.

Work Sessions:
Session 1: ~3–4 minutes — Inspection of OpenAI integration, SDK version identification, migration planning
Session 2: ~4–5 minutes — SDK migration, API pattern update, model identifier change, logging updates
Session 3: ~2–3 minutes — Runtime validation, ImportError diagnosis, virtual environment package upgrade
Session 4: ~3–4 minutes — Maintainability analysis and documentation

Development Approach:

The implementation was carried out using AI-assisted development. The measured time represents the workflow from submitting the implementation prompt to final manual validation.

This includes:
- AI generation of the code changes
- high-level review of the generated code
- running the system and executing manual test cases
- validating runtime behavior through logs and outputs

No manual re-implementation without AI assistance was performed. The primary effort was focused on validation, debugging, and ensuring correct system behavior rather than writing code from scratch.

Total Time:
~7–8 minutes

Iterations:
2

Issues Faced:

1. Legacy SDK API Removal
   openai.ChatCompletion.create() no longer exists in SDK v1.x+.
   Migration required adapting the entire API call structure before the model name could be changed.

2. Response Object Change
   SDK v1.x changed response access from dict-style (message["content"]) to attribute-style (message.content).
   Missing this causes a TypeError with no obvious connection to the SDK version change.

3. Runtime Environment Mismatch
   requirements.txt was updated, but the active virtual environment still contained openai==0.28.1.
   This caused runtime startup failure: ImportError: cannot import name 'OpenAI' from 'openai'
   Resolved by upgrading the installed package inside the virtual environment:
   pip install "openai>=1.0.0"
   Installed version after upgrade: openai 2.36.0

Debugging Steps:

Iteration 1:
- Inspected OpenAI integration structure in backend/response_gen.py
- Identified SDK pin to openai==0.28.1 in requirements.txt
- Migrated client initialisation, API call pattern, response access pattern, and model identifier
- Updated logging references in main.py
- IDE diagnostics identified remaining legacy API reference during migration

Iteration 2:
- Backend startup validation exposed ImportError caused by outdated installed SDK in the virtual environment
- Verified mismatch between dependency declaration and actual runtime package version
- Upgraded installed OpenAI package manually via pip
- Revalidated backend startup successfully

Testing Results:
- Backend starts successfully after dependency synchronisation
- OpenAI client initialises correctly using v1.x SDK
- generate_response() works with client.chat.completions.create(...)
- Runtime logs correctly show gpt-5.4-mini in both voice and text paths
- Prompt structure and response pipeline remain unchanged
- Existing fallback response behaviour remains intact
- No frontend or API contract changes required

Behavioral Observations:
- Existing prompts remained compatible with the newer model
- No structural prompt modifications were required
- Response flow remained stable after migration
- No streaming behaviour was introduced

Maintainability Analysis:
The actual model identifier change was technically simple. Most effort came from SDK migration, dependency compatibility, runtime environment synchronisation, and API surface adaptation. The migration exposed hidden coupling between the SDK version, integration code, and the runtime environment state. The scenario demonstrated that maintainability complexity in AI-integrated systems often arises more from dependency coordination than from implementation logic itself.

Key Insight:
A one-line model update triggered an SDK migration, response handling changes, runtime dependency synchronisation, and cross-file consistency updates. This illustrates how dependency evolution in AI systems creates integration overhead disproportionate to the apparent simplicity of the change.

Outcome:
The OpenAI integration now uses the v1.x SDK with the gpt-5.4-mini model. All legacy API patterns have been removed. The model identifier is centralised within the integration module and kept consistent with the logging layer. The architecture, prompt structure, request flow, and all other pipeline components remain unchanged.

Observed Findings:
- SDK version lag was the primary migration difficulty, not the model name change itself
- Dependency declarations and runtime environments can diverge silently during migrations
- The OpenAI v1.x migration required coordinated changes across imports, client initialisation, API calls, and response access patterns — missing any one causes a runtime failure
- Runtime validation was necessary even after successful code migration
- AI-assisted development significantly reduced migration inspection and debugging time

Relevance to Thesis:
1. Demonstrates hidden integration overhead — a model name update required SDK migration across API patterns, response handling, and logging.
2. Quantifies AI-assisted maintenance effort — the full migration was completed within one AI-assisted session.
3. Highlights architectural risk of version pinning — pinning to a specific legacy version is a maintainability anti-pattern that this scenario surfaced and corrected.
4. Supports thesis research question on integration complexity — complexity arises as much from coordination across dependencies as from implementation work itself.

Included in Thesis Scenario Metrics:
YES
