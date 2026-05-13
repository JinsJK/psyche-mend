[SCENARIO 6 — AI DEPENDENCY MODERNIZATION AND COMPATIBILITY STABILIZATION]

Objective:
Modernize selected AI and runtime dependencies of the Psyche Mend prototype while preserving existing system behaviour, CUDA acceleration, and all pipeline functionality.

Why This Scenario Was Chosen:
AI-integrated systems accumulate dependency lag over time. Dependencies pinned during initial development become outdated as ecosystems evolve, creating a growing gap between declared versions and current stable releases. Dependency modernization is a routine but high-risk maintenance activity in AI pipelines because library ecosystems have tight compatibility constraints, especially across NumPy, PyTorch, Whisper, TTS, and transformer-based models. This scenario evaluates the effort, risk management, and compatibility reasoning required when a solo developer partially modernizes a multi-component AI pipeline without disrupting operational behaviour.

Scope:
- Inventory the full dependency state before any changes
- Upgrade selected dependencies in isolated clusters with validation after each
- Identify and document dependencies that cannot be safely upgraded
- Preserve existing architecture, prompts, endpoints, logging schema, and request flow
- Update requirements.txt to reflect the validated stable runtime state

Baseline (Before Change):

Environment:
- Python: 3.10.11, pip: 26.0.1, OS: Windows 11, CUDA: 11.8 available
- Virtual environment: psyche-mend-env

Key dependency versions before upgrade:
- torch: 2.5.1+cu118, torchaudio: 2.5.1+cu118
- transformers: 4.36.2
- openai-whisper: 20231117
- numpy: 1.22.0, scipy: 1.11.4
- openai: 2.36.0, fastapi: 0.95.2, pydantic: 1.10.26, TTS: 0.22.0

AI Model Inventory:
- LLM: gpt-5.4-mini (OpenAI API)
- STT: whisper medium (backend/speech_to_text.py)
- Emotion: j-hartmann/emotion-english-distilroberta-base (backend/sentiment.py)
- TTS: tts_models/en/vctk/vits, speaker p243 (backend/text_to_speech.py)

Changes Implemented:

1. openai-whisper upgraded: 20231117 → 20250625
   All dependencies satisfied. Whisper medium confirmed on cuda:0 after upgrade.

2. numpy upgraded: 1.22.0 → 1.26.4
   TTS 0.22.0 metadata declares numpy==1.22.0 for Python <=3.10 but runtime confirmed TTS works with 1.26.4. Metadata constraint is overly conservative.

3. scipy upgraded: 1.11.4 → 1.13.1
   scipy 1.13.1 requires numpy >=1.22.4, satisfied by 1.26.4. All dependent modules verified.

4. torch / torchaudio kept pinned at 2.5.1+cu118
   torch 2.6.0+cu118 is available but changes torch.load default to weights_only=True. Whisper and TTS both call torch.load without the explicit argument. Upgrading could affect model loading paths and was considered too risky for this controlled scenario.

5. transformers kept pinned at 4.36.2
   transformers 5.x was not upgraded because previous testing (Scenario 2) showed compatibility issues with the current torch version and model-loading path.

6. requirements.txt updated
   - openai-whisper==20231117 → openai-whisper==20250625
   - numpy==1.22.0 → numpy==1.26.4
   - scipy==1.11.4 → scipy==1.13.1

Dependency Versions Before and After:

Package             Before          After           Decision
openai-whisper      20231117        20250625        upgraded
numpy               1.22.0          1.26.4          upgraded
scipy               1.11.4          1.13.1          upgraded
torch               2.5.1+cu118     2.5.1+cu118     pinned (torch.load default risk)
torchaudio          2.5.1+cu118     2.5.1+cu118     pinned (torch dependency)
transformers        4.36.2          4.36.2          pinned (torch/model-loading compatibility)
TTS                 0.22.0          0.22.0          pinned (out of scope)
fastapi             0.95.2          0.95.2          pinned (out of scope)
pydantic            1.10.26         1.10.26         pinned (out of scope)
uvicorn             0.22.0          0.22.0          pinned (out of scope)

Work Sessions:
Session 1: ~2–3 minutes — Environment inventory, pip freeze capture, outdated dependency collection, baseline documentation
Session 2: ~3–4 minutes — Torch cu118 availability check, risk assessment, numpy/scipy upgrade, TTS compatibility verification
Session 3: ~2–3 minutes — openai-whisper upgrade, Whisper model load verification, emotion model verification
Session 4: ~2 minutes — Full backend import validation, requirements.txt update

Development Approach:

The implementation was carried out using AI-assisted development. The measured time represents the workflow from submitting the implementation prompt to final manual validation.

This includes:
- AI generation of the code changes
- high-level review of the generated code
- running the system and executing manual test cases
- validating runtime behavior through logs and outputs

No manual re-implementation without AI assistance was performed. The primary effort was focused on validation, debugging, and ensuring correct system behavior rather than writing code from scratch.

Total Time:
11 minutes 34 seconds

Breakdown:
- Iteration 1 — Dependency modernization and validation: 9 minutes 23 seconds
- Iteration 2 — Deprecated TTS gpu argument removal: 2 minutes 11 seconds

Iterations:
2

Files Changed:
requirements.txt                              — numpy, scipy, openai-whisper version updates
backend/text_to_speech.py                     — deprecated gpu= argument replaced with tts.to(device)
docs/dependency_inventory_before_upgrade.txt  — created: full pip freeze before upgrade
docs/outdated_dependencies_before_upgrade.txt — created: outdated package list before upgrade
docs/scenario_6_dependency_modernization.md   — this document

Issues Faced:
1. Torch upgrade risk — torch 2.6.0+cu118 available but not upgraded; torch.load default change could affect Whisper and TTS model loading
2. Transformers compatibility — transformers 5.x not upgraded; previous testing showed model-loading failures with the current torch version
3. TTS metadata constraint — TTS pins numpy==1.22.0 for Python 3.10 in metadata; runtime confirmed 1.26.4 works; pip warning was non-blocking
4. Selective modernization — determining which dependencies could be safely upgraded was the primary engineering effort

Testing Results:
- Backend started successfully after dependency modernization
- CUDA remained available, Whisper and TTS continued using GPU acceleration
- Voice request path functional — two voice requests validated through structured logs
- Text request path functional — one text request validated through structured logs
- STT, emotion detection, LLM, and TTS all worked correctly after modernization
- Structured logs captured request_id, stage, status, duration_ms, model, emotion, input_type correctly
- Runtime logs showed gpt-5.4-mini for the LLM stage

Runtime Validation Log Entries:

Voice Request 1:
stt: 2015.5 ms | emotion: 1028.2 ms (anger) | llm: 3105.2 ms | tts: 1768.0 ms | api_end: 9019.9 ms

Voice Request 2:
stt: 1079.3 ms | emotion: 23.9 ms (neutral) | llm: 2522.3 ms | tts: 1163.1 ms | api_end: 4885.0 ms

Text Request:
emotion: 19.6 ms (neutral) | llm: 2856.7 ms | tts: 912.6 ms | api_end: 3790.3 ms

Additional Observations:

Scenario 6 showed that dependency modernization in AI-integrated systems should not be treated as a simple update-to-latest task. Although several packages were outdated, only a subset could be safely modernized without destabilizing the runtime environment.

The main engineering effort was not the package installation itself, but the compatibility assessment around tightly coupled dependencies such as torch, torchaudio, transformers, Whisper, NumPy, SciPy, and TTS. This confirms that maintainability work in AI systems often shifts toward dependency coordination, runtime validation, and risk management.

The scenario also showed that package metadata and actual runtime behaviour may differ. Although TTS declared a strict NumPy requirement, runtime validation confirmed that the system still worked with the upgraded NumPy version. Therefore, successful dependency modernization required both dependency analysis and practical runtime testing.

A further distinction emerged between application-level warnings and dependency-level warnings. The deprecated TTS gpu argument was part of the application integration code and could be safely fixed. In contrast, warnings from transformers, huggingface_hub, and torch.load originated inside third-party libraries and were documented as future maintenance risks rather than fixed immediately.

Overall, the scenario demonstrates that selective modernization can be more maintainable than full modernization when the system depends on tightly coupled AI libraries and hardware-accelerated execution.

Maintainability Analysis:
The modernization surface was small — three packages upgraded — but required evaluating dependency graphs, CUDA behaviour, model-loading risks, and runtime compatibility across a multi-component AI pipeline. The fragility of the torch/transformers/TTS cluster was the key finding: a single torch minor version increment could affect multiple independent model loading paths simultaneously, and this coupling is invisible from application code alone. The TTS metadata conflict also illustrates a broader issue: pip resolver warnings may overstate incompatibility, making runtime validation the authoritative test rather than dependency metadata.

Key Insight:
Dependency modernization in multi-model AI systems is not primarily a packaging task — it is a compatibility risk assessment task. The dominant effort is evaluating what cannot be safely upgraded, not performing the upgrades themselves.

Outcome:
Three dependencies upgraded: openai-whisper 20231117 → 20250625, numpy 1.22.0 → 1.26.4, scipy 1.11.4 → 1.13.1. High-risk clusters kept pinned. The backend remained stable, CUDA remained operational, Whisper and TTS continued using GPU acceleration, and both request paths were validated through structured runtime logs.

Observed Findings:
- Selective modernization was safer than bulk upgrading
- torch 2.6.0 available but introduced potential model-loading risk via torch.load default change
- transformers 5.x skipped due to model-loading compatibility with current torch version
- TTS metadata overstated numpy constraint; runtime behaviour was the authoritative test
- Voice Request 1 latency higher than Voice Request 2, consistent with CUDA warm-up
- Text requests consistently faster due to no STT stage
- AI-assisted analysis reduced compatibility assessment time; runtime validation still required manual testing

Relevance to Thesis:
1. Dependency Evolution — shows how dependency updates in AI systems extend beyond simple package installation into compatibility risk management.
2. Integration Complexity — compatibility risks span libraries, runtime environments, model loading, and hardware acceleration simultaneously.
3. Maintainability — solo developer must manage dependency drift, version pinning, and runtime validation as ongoing responsibilities.
4. Complexity Redistribution — AI-assisted development reduces implementation effort but shifts work toward integration, configuration, and stabilization.

Included in Thesis Scenario Metrics:
YES

---

[REFINEMENT — DEPRECATED TTS GPU ARGUMENT REMOVAL]

Category:
Scenario 6 — Follow-up refinement (still part of Scenario 6)

Changes Made:
Backend stdout showed one application-level deprecation warning:
  UserWarning: `gpu` will be deprecated. Please use `tts.to(device)` instead.

In backend/text_to_speech.py:
Before:
  use_gpu = torch.cuda.is_available()
  tts = TTS(model_name="tts_models/en/vctk/vits", progress_bar=False, gpu=use_gpu)
After:
  device = "cuda" if torch.cuda.is_available() else "cpu"
  tts = TTS(model_name="tts_models/en/vctk/vits", progress_bar=False)
  tts.to(device)

TTS model, speaker ID, synthesis function, and pipeline structure unchanged.

Validation:
- deprecated TTS gpu= warning no longer appeared in stdout
- CUDA remained available, TTS confirmed on cuda:0
- text and voice request paths both worked correctly
- structured logs continued to capture all stages correctly

Residual Warnings (documented, not fixed):
- torch.load FutureWarning (weights_only=False) — from transformers and TTS internals; may become breaking when torch is upgraded to newer versions
- torch.utils._pytree._register_pytree_node FutureWarning — from transformers 4.36.2; non-breaking, signals version lag
- resume_download FutureWarning — from huggingface_hub 0.36.2; non-breaking, signals version lag

Decision:
Residual warnings originate from third-party library internals. Fixing them would require upgrading high-risk clusters intentionally kept pinned in the main scenario. The TTS gpu= fix was application-level and safe to apply in isolation; the remaining warnings are dependency-level signals to track as future maintenance risks.

Development Approach:

The implementation was carried out using AI-assisted development. The measured time represents the workflow from submitting the implementation prompt to final manual validation.

This includes:
- AI generation of the code changes
- high-level review of the generated code
- running the system and executing manual test cases
- validating runtime behavior through logs and outputs

No manual re-implementation without AI assistance was performed. The primary effort was focused on validation, debugging, and ensuring correct system behavior rather than writing code from scratch.

Files Changed in This Refinement:
backend/text_to_speech.py — deprecated gpu= argument replaced with tts.to(device)

Additional Time Spent:
2 minutes 11 seconds

Included in Thesis Scenario Metrics:
YES
