[SCENARIO 1 — STRUCTURED LOGGING AND REQUEST TRACING]

Objective:
Add structured logging with per-request UUID tracing and per-stage timing across the full prototype pipeline.

Why This Scenario Was Chosen:
The prototype operates as a multi-stage AI pipeline where user input flows through multiple AI components (speech-to-text, sentiment analysis, LLM, and text-to-speech). Without proper observability:
- Failures are hard to trace
- Performance bottlenecks remain hidden
- Debugging relies on temporary console logs

This scenario aligns directly with the thesis methodology, which includes introducing structured logging with per-stage timestamps as a controlled update scenario.

Scope:
- Generate a unique request_id (UUID) for every API request
- Implement file-based logging (logs/app.log)
- Use rotating logs (5 MB per file, 5 backups)
- Store logs in structured JSON format (one entry per event)
- Add logging to each pipeline stage: api_start, stt (voice only), emotion, llm, tts, api_end
- Track execution time per stage using time.perf_counter()

Logging Format:
JSON Lines — one JSON object per line

Log Fields:
- timestamp   : UTC time in ISO format
- request_id  : Unique ID for request tracing
- stage       : Current pipeline stage
- status      : success, error, or fallback
- duration_ms : Time taken for the stage (ms)
- emotion     : Emotion detected (if available)
- model       : Model used (if applicable)
- error_type  : Error type if failure occurred
- input_type  : Type of request: text or voice

Example Log Entry:
{"timestamp": "2026-04-08T10:15:22.123Z", "request_id": "3f2c9e1a-...", "stage": "llm", "status": "success", "duration_ms": 1240.3, "emotion": "sadness", "model": "gpt-3.5-turbo", "error_type": null, "input_type": "text"}

Request Flow:
Voice : api_start → stt → emotion → llm → tts → api_end
Text  : api_start → emotion → llm → tts → api_end

Work Sessions:
Session 1: ~6–7 minutes — Implement logging system, integrate into pipeline, test logs

Development Approach:
The implementation was carried out using AI-assisted development. The measured time includes:
- prompt formulation
- reviewing generated code at a high level
- testing and validation of runtime behavior

No manual re-implementation without AI assistance was performed.

Total Time:
~6–7 minutes

Iterations:
1

Files Changed:
backend/logger.py          — Created logging utility
main.py                    — Added request tracing + logging calls
docs/scenario_1_logging.md — Created documentation

Implementation Details:
- Python logging module used with RotatingFileHandler for log rotation
- Custom log_event() function ensures consistent structure
- Logger module kept minimal; all log calls centralised in main.py

Issues Faced:
- Passing request_id across multiple components
- Maintaining consistent JSON structure across all stages
- Handling optional fields (emotion, model, error_type)
- Integrating logging without breaking existing flow
- Ensuring logs remain readable and structured

Outcome:
- Every request is traceable using request_id
- Logs persist across sessions in logs/app.log
- Automatic log rotation prevents storage overflow
- Per-stage timing is captured accurately
- Errors are structured and traceable

Observed Findings:
Voice requests execute the full pipeline and are significantly slower due to STT.
Text requests are faster with no STT stage.

Performance Breakdown:
STT     — 10–11 seconds
LLM     — 1.8–2.1 seconds
TTS     — ~2–3.5 seconds
Emotion — < 300 ms

Key Insight:
Speech-to-text is the primary bottleneck in the system.
Total request duration is now directly observable from the api_end stage.

Cleanup Strategy:
RotatingFileHandler (5 MB × 5 files). Logs automatically overwrite oldest files. No manual cleanup required.
Optional future improvements: daily log rotation, archiving old logs, filtering logs by level.

Relevance to Thesis:
1. Makes System Observable — enables tracing across all AI components.
2. Provides Measurable Data — captures timing and performance for analysis.
3. Highlights Integration Complexity — shows that even small features require cross-component changes.
4. Supports Research Questions — helps analyse where complexity lies, effort required for system evolution, and maintainability of multi-modal AI systems.

Included in Thesis Scenario Metrics:
YES

---

[FOLLOW-UP REFINEMENTS]

Category:
Scenario 1 — Follow-up refinement (still part of Scenario 1)

Changes Made:
A small follow-up refinement was made after the initial implementation to improve the analytical quality of the runtime logs.

1. Model names added for all relevant stages
Previously null for stt, emotion, and tts. Now populated as follows:
- stt     : whisper-medium
- emotion : j-hartmann/emotion-english-distilroberta-base
- llm     : gpt-3.5-turbo (unchanged)
- tts     : tts_models/en/vctk/vits

2. Total request duration added to api_end
A t_request_start timer is now set at the very beginning of each request. The api_end entry records total wall-clock duration_ms from that point to final response — not a sum of stage durations. This captures all overhead between stages that individual timers would miss.

3. input_type field added
A new input_type field (text or voice) is included in every log entry, allowing log analysis to distinguish between /talk/ and /text-talk/ requests without cross-referencing request IDs.

Files Changed in This Refinement:
backend/logger.py — Added input_type parameter to log_event()
main.py           — Added model names, t_request_start timer, and input_type to all log_event calls in both endpoints

Additional Observations:
- Voice requests can now be clearly differentiated from text requests in the runtime logs
- Stage-specific model usage is now directly visible in every log line
- Total request latency can now be read directly from api_end without summing stage durations
- The logs now provide a clearer basis for comparing multi-stage execution costs across request types

Development Approach:
This refinement was implemented using AI-assisted development, including prompt formulation, code adjustment, and validation through test runs.

Additional Time Spent:
~3 minutes

Included in Thesis Scenario Metrics:
YES
