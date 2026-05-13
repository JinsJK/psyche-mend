[SCENARIO 8 — CONFIGURATION CENTRALIZATION AND ENVIRONMENT REPRODUCIBILITY]

Objective:
Improve maintainability and environment reproducibility by moving hardcoded runtime configuration values into a centralized configuration module, without changing system behaviour.

Why This Scenario Was Chosen:
The Psyche Mend prototype had runtime configuration values — model names, timeout values, log settings, and speaker IDs — scattered across multiple backend modules. Each value was duplicated independently in the file where it was used, with no single source of truth. This pattern creates a maintenance risk: updating a model name or timeout requires locating and editing every occurrence across multiple files. This scenario evaluates the effort required to retrofit centralized configuration into an existing multi-component AI pipeline without disrupting runtime behaviour.

Scope:
- Identify all hardcoded configuration values across backend modules
- Create a centralized backend/config.py module
- Replace hardcoded values with imports from config across all affected files
- Preserve all model names, timeout values, logging schema, and runtime behaviour
- Validate with normal text and voice requests

Baseline (Before Change):

backend/response_gen.py    — MODEL = "gpt-5.4-mini" hardcoded; timeout=10 hardcoded inline
backend/speech_to_text.py  — whisper.load_model("medium") hardcoded
backend/sentiment.py       — model="j-hartmann/emotion-english-distilroberta-base" hardcoded
backend/text_to_speech.py  — TTS(model_name="tts_models/en/vctk/vits") and default_speaker = "p243" hardcoded
backend/logger.py          — "logs/app.log", 5*1024*1024, backupCount=5 hardcoded
main.py                    — "gpt-5.4-mini", "whisper-medium", "j-hartmann/emotion-english-distilroberta-base", "tts_models/en/vctk/vits" all hardcoded in log_event() calls

Configuration Values Identified:

OPENAI_MODEL               = "gpt-5.4-mini"
LLM_TIMEOUT_SECONDS        = 10
LLM_MAX_RETRIES            = 1
WHISPER_MODEL_NAME         = "medium"
WHISPER_LOG_MODEL_NAME     = "whisper-medium"
EMOTION_MODEL_NAME         = "j-hartmann/emotion-english-distilroberta-base"
TTS_MODEL_NAME             = "tts_models/en/vctk/vits"
TTS_SPEAKER_ID             = "p243"
LOG_FILE_PATH              = "logs/app.log"
LOG_MAX_BYTES              = 5 * 1024 * 1024
LOG_BACKUP_COUNT           = 5

Changes Implemented:

1. backend/config.py
   Created as the single source of truth for all runtime configuration. Contains 11 named constants covering the LLM, STT, emotion, TTS, and logging configuration.

2. backend/response_gen.py
   Removed module-level MODEL constant and inline timeout=10. Imported OPENAI_MODEL and LLM_TIMEOUT_SECONDS from backend.config.

3. backend/speech_to_text.py
   Replaced hardcoded "medium" with WHISPER_MODEL_NAME imported from backend.config.

4. backend/sentiment.py
   Replaced hardcoded model string with EMOTION_MODEL_NAME imported from backend.config.

5. backend/text_to_speech.py
   Replaced hardcoded TTS model name and speaker ID with TTS_MODEL_NAME and TTS_SPEAKER_ID imported from backend.config.

6. backend/logger.py
   Replaced hardcoded log file path and rotation settings with LOG_FILE_PATH, LOG_MAX_BYTES, and LOG_BACKUP_COUNT imported from backend.config.

7. main.py
   Replaced all hardcoded model name strings in log_event() calls with OPENAI_MODEL, WHISPER_LOG_MODEL_NAME, EMOTION_MODEL_NAME, and TTS_MODEL_NAME imported from backend.config.

Work Sessions:
Session 1: ~3 minutes — Baseline inspection across all backend modules, creation of backend/config.py, replacement of hardcoded values in 6 files, backend startup and runtime validation

Development Approach:

The implementation was carried out using AI-assisted development. The measured time represents the workflow from submitting the implementation prompt to final manual validation.

This includes:
- AI generation of the code changes
- high-level review of the generated code
- running the system and executing manual test cases
- validating runtime behavior through logs and outputs

No manual re-implementation without AI assistance was performed. The primary effort was focused on validation, debugging, and ensuring correct system behavior rather than writing code from scratch.

Total Time:
3 minutes 7 seconds

Iterations:
1

Files Changed:
backend/config.py          — created: centralized configuration module
backend/response_gen.py    — OPENAI_MODEL, LLM_TIMEOUT_SECONDS
backend/speech_to_text.py  — WHISPER_MODEL_NAME
backend/sentiment.py       — EMOTION_MODEL_NAME
backend/text_to_speech.py  — TTS_MODEL_NAME, TTS_SPEAKER_ID
backend/logger.py          — LOG_FILE_PATH, LOG_MAX_BYTES, LOG_BACKUP_COUNT
main.py                    — OPENAI_MODEL, WHISPER_LOG_MODEL_NAME, EMOTION_MODEL_NAME, TTS_MODEL_NAME
docs/scenario_8_configuration_centralization.md — this document

Issues Faced:
1. Dual Whisper name distinction — Whisper loads using "medium" (the model size identifier) but logs as "whisper-medium" (the descriptive log name). These serve different purposes and required two separate constants: WHISPER_MODEL_NAME and WHISPER_LOG_MODEL_NAME.

Testing Results:
- Backend started successfully after centralization
- CUDA remained available; Whisper and TTS continued loading on GPU
- Text request path functional — all stages success, model names correct in logs
- Voice request path functional — all stages success, model names correct in logs
- No relevant hardcoded runtime model identifiers were found outside backend/config.py during validation
- Scenario 7 logging fields were preserved in normal requests — retry_count=0 and fallback_used=false remained visible in structured logs

Runtime Validation Log Entries:

Text Request:
emotion: 771.7 ms (anger) | llm: 2792.8 ms | tts: 1247.1 ms | api_end: 4813.0 ms
llm log: status=success, retry_count=0, fallback_used=false

Voice Request:
stt: 1532.2 ms | emotion: 26.8 ms (sadness) | llm: 1439.2 ms | tts: 997.5 ms | api_end: 4088.4 ms
llm log: status=success, retry_count=0, fallback_used=false

Log Model Names Verified:
stt: whisper-medium | emotion: j-hartmann/emotion-english-distilroberta-base | llm: gpt-5.4-mini | tts: tts_models/en/vctk/vits

Additional Observations:
The main engineering effort was identifying which values were configuration and which were logic. Device selection (cuda/cpu) was left in each module rather than centralized, as it involves a runtime check rather than a configurable constant and is already derived consistently using the same torch.cuda.is_available() call. The LLM_MAX_RETRIES constant was added to config for completeness even though the retry count is currently implicit in the nested try/except structure in response_gen.py.

Maintainability Analysis:
Before centralization, a model name change required editing every file that referenced it — both for the actual API call and for the corresponding log_event() call. These two uses are easy to miss independently. Centralization reduces a multi-file search-and-replace to a single-line edit in backend/config.py. The scenario also surfaced a naming asymmetry in the Whisper integration: the model is loaded by size name ("medium") but logged by descriptive name ("whisper-medium"), requiring explicit documentation of the distinction in the config module.

Key Insight:
Configuration scattering in multi-component AI systems is not always visible until a change is required. Every hardcoded model name is a silent coupling between the code and the external model, and each duplicate instance is an independent point of drift. Centralization makes the full configuration surface of the system visible in one place.

Outcome:
backend/config.py created with 11 constants. Hardcoded configuration values removed from 6 files. All model names, timeout values, log settings, and speaker ID now sourced from a single module. Backend behaviour, logging schema, and runtime model names unchanged. Both request paths validated through structured logs.

Observed Findings:
- 11 configuration constants identified and centralized
- 6 backend files updated with config imports
- No relevant hardcoded runtime model identifiers found outside backend/config.py during validation
- Whisper requires two distinct name constants: one for model loading, one for logging
- Device selection left in-place as a runtime-derived value, not a static config constant
- Log model names verified correct in both text and voice request paths
- No latency, behaviour, or schema changes observed after centralization

Relevance to Thesis:
1. Maintainability — centralized configuration reduces the surface area for drift when models or settings change
2. Integration Complexity — configuration scattering across a multi-component pipeline is a structural maintainability risk invisible at runtime
3. Complexity Redistribution — AI-assisted development reduced implementation effort; main effort shifted to identifying which values were configuration versus logic
4. Environment Reproducibility — a single config module makes the full runtime configuration of the system visible and auditable in one place

Included in Thesis Scenario Metrics:
YES
