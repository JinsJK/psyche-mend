[SCENARIO 7 — FAILURE OBSERVABILITY AND GRACEFUL DEGRADATION]

Objective:
Add structured failure visibility to the LLM stage by introducing a 10-second API timeout, one retry attempt, and differentiated log status for fallback responses. The change ensures LLM failures are observable in structured logs and distinguishable from successful responses.

Why This Scenario Was Chosen:
The existing LLM integration had a single bare except block that printed to stdout and returned a hardcoded fallback string. The caller in main.py always logged status=success regardless of outcome, making LLM failures invisible in the structured log file. This scenario evaluates the effort to retrofit observability into a pipeline component without disrupting request flow, TTS continuation, or frontend behaviour.

Scope:
- Add a 10-second timeout to the LLM API call
- Add one retry attempt on first failure
- Add retry_count and fallback_used fields to log_event()
- Log status=fallback with error_type=LLMFailure when fallback is triggered
- Log status=success with retry_count and fallback_used=false on normal responses
- Preserve existing pipeline behaviour, TTS continuation, and frontend API contract
- Validate with normal requests, simulated LLM failure, retry success, timeout fallback, and recovery

Baseline (Before Change):

backend/response_gen.py — single except catch, hardcoded fallback string, no timeout, no retry, return type: str
backend/logger.py — log_event() had no retry_count or fallback_used fields
main.py — always logged status=success regardless of LLM outcome; fallback indistinguishable from real response

Changes Implemented:

1. backend/logger.py
   Added retry_count: int = None and fallback_used: bool = None to log_event(). Both default to None so all existing call sites continued to work without modification.

2. backend/response_gen.py
   Added FALLBACK_RESPONSE constant to centralise the fallback string. Added timeout=10. Added retry on first failure.
   Return type changed from str to tuple(str, int, bool): reply, retry_count, fallback_used.
   - First success: (reply_text, 0, False)
   - Retry success: (reply_text, 1, False)
   - Full failure: (FALLBACK_RESPONSE, 1, True)
   - BLOCKED_PHRASES path: (reply_text, 0, False)

3. main.py
   Both /talk/ and /text-talk/ endpoints updated to unpack 3-tuple. If fallback_used=True: log status=fallback, error_type=LLMFailure. Otherwise: log status=success. TTS call and response format unchanged.

Work Sessions:
Session 1: ~2–3 minutes — Baseline review, identifying call sites and return type dependencies
Session 2: ~3–4 minutes — Implementation: timeout, retry, fallback metadata, logger fields, conditional logging
Session 3: ~2–3 minutes — Normal request, invalid-model failure, recovery validation
Session 4: ~3–4 minutes — Extended testing: retry success simulation, timeout fallback, final recovery

Development Approach:

The implementation was carried out using AI-assisted development. The measured time represents the workflow from submitting the implementation prompt to final manual validation.

This includes:
- AI generation of the code changes
- high-level review of the generated code
- running the system and executing manual test cases
- validating runtime behavior through logs and outputs

No manual re-implementation without AI assistance was performed. The primary effort was focused on validation, debugging, and ensuring correct system behavior rather than writing code from scratch.

Total Time:
22 minutes 24 seconds

Breakdown:
- Iteration 1 — Initial failure observability and graceful degradation: 14 minutes
- Iteration 2 — Per-attempt LLM failure logging refinement: 8 minutes 24 seconds

Iterations:
2

Files Changed:
backend/response_gen.py  — timeout, retry logic, FALLBACK_RESPONSE constant, tuple return type
backend/logger.py        — retry_count and fallback_used added to log_event()
main.py                  — tuple unpacking, conditional final LLM logging, and per-attempt error logging after refinement
docs/scenario_7_failure_observability.md — this document

Issues Faced:
1. Return type propagation — changing generate_response() from str to tuple required updating BLOCKED_PHRASES path and both call sites; missing any one would cause a runtime unpack error
2. Log schema coordination — adding retry_count and fallback_used required aligned changes across logger.py, response_gen.py, and main.py
3. TTS continuation — fallback response still needed to pass through TTS; worked without pipeline changes because reply is unpacked before the TTS call

Testing Results:
- Normal voice and text requests: status=success, retry_count=0, fallback_used=false
- Invalid model failure (text + voice): status=fallback, retry_count=1, fallback_used=true, error_type=LLMFailure; TTS and api_end succeeded
- Retry success (SIMULATE_FIRST_LLM_FAILURE flag, removed after test): status=success, retry_count=1, fallback_used=false
- Timeout fallback (timeout=0.001, removed after test): status=fallback, retry_count=1, fallback_used=true
- Recovery: status=success, retry_count=0, fallback_used=false restored on all paths
- Backend did not crash or return HTTP errors in any simulated failure case

Runtime Validation Log Entries:

Normal Voice Request:
stt: 1280.7 ms | emotion: 1029.0 ms (anger) | llm: 2674.3 ms | tts: 1182.8 ms | api_end: 6254.1 ms
llm log: status=success, retry_count=0, fallback_used=false

Fallback Text Request — Invalid Model:
emotion: 813.8 ms (anger) | llm: 2272.6 ms | tts: 1372.7 ms | api_end: 4460.5 ms
llm log: status=fallback, retry_count=1, fallback_used=true, error_type=LLMFailure

Recovery Text Request:
emotion: 775.3 ms (anger) | llm: 2595.0 ms | tts: 1457.4 ms | api_end: 4829.3 ms
llm log: status=success, retry_count=0, fallback_used=false

---

[REFINEMENT — PER-ATTEMPT LLM FAILURE LOGGING]

Why Refinement Was Needed:
The initial implementation logged the final LLM outcome using retry_count and fallback_used. This made fallback activation visible, but individual failed LLM attempts were not logged as separate structured events. The logs showed that fallback happened after retry, but did not show the failure sequence that led to it.

Changes Made:
- Added attempt_errors list in backend/response_gen.py
- Captured the exception class name for each failed LLM attempt using type(e).__name__
- Updated generate_response() return type to 4-tuple: (reply, retry_count, fallback_used, attempt_errors)
- Updated both /talk/ and /text-talk/ endpoints in main.py to unpack the 4-tuple
- Added per-attempt error logging loop before the final success/fallback log

Design decision: attempt error metadata is returned from generate_response() and logged in main.py, keeping all logging in the routing layer and avoiding a logging import in response_gen.py.

Log Pattern After Refinement:

Normal success:
stage=llm | status=success | retry_count=0 | fallback_used=false

Retry success:
stage=llm | status=error   | retry_count=0 | fallback_used=false | error_type=<ExceptionClass>
stage=llm | status=success | retry_count=1 | fallback_used=false

Full failure:
stage=llm | status=error   | retry_count=0 | fallback_used=false | error_type=<ExceptionClass>
stage=llm | status=error   | retry_count=1 | fallback_used=false | error_type=<ExceptionClass>
stage=llm | status=fallback| retry_count=1 | fallback_used=true  | error_type=LLMFailure

Validation:

Normal text request:
emotion: 799.5 ms (anger) | llm: 2618.7 ms | tts: 1354.2 ms | api_end: 4773.9 ms
llm log: status=success, retry_count=0, fallback_used=false — no attempt error entries

Invalid model failure — text:
emotion: 794.4 ms (neutral)
llm log 1: status=error, retry_count=0, fallback_used=false, error_type=NotFoundError
llm log 2: status=error, retry_count=1, fallback_used=false, error_type=NotFoundError
llm log 3: status=fallback, duration_ms=1546.2, retry_count=1, fallback_used=true, error_type=LLMFailure
tts: 1330.1 ms | api_end: 3672.6 ms

Invalid model failure — voice:
stt: 1068.1 ms | emotion: 23.2 ms (sadness)
llm log 1: status=error, retry_count=0, fallback_used=false, error_type=NotFoundError
llm log 2: status=error, retry_count=1, fallback_used=false, error_type=NotFoundError
llm log 3: status=fallback, duration_ms=928.0, retry_count=1, fallback_used=true, error_type=LLMFailure
tts: 316.7 ms | api_end: 2421.1 ms

Recovery:
emotion: 816.6 ms (anger) | llm: 2299.7 ms | tts: 1419.1 ms | api_end: 4536.8 ms
llm log: status=success, retry_count=0, fallback_used=false — no attempt error entries

Development Approach:

The implementation was carried out using AI-assisted development. The measured time represents the workflow from submitting the implementation prompt to final manual validation.

This includes:
- AI generation of the code changes
- high-level review of the generated code
- running the system and executing manual test cases
- validating runtime behavior through logs and outputs

No manual re-implementation without AI assistance was performed. The primary effort was focused on validation, debugging, and ensuring correct system behavior rather than writing code from scratch.

Files Changed in This Refinement:
backend/response_gen.py — attempt_errors list, type(e).__name__ capture, 4-tuple return type
main.py                 — 4-tuple unpack, per-attempt error logging loop in both endpoints

Additional Time Spent:
8 minutes 24 seconds

Included in Thesis Scenario Metrics:
YES

Refinement Outcome:
The refinement improved failure observability from final-outcome logging to attempt-level logging. The structured logs now show the complete LLM failure sequence: first attempt failure, retry failure, and final fallback activation. The actual SDK exception class (e.g. NotFoundError) is captured per attempt, making logs actionable without requiring stdout inspection.

---

Final Maintainability Analysis:
Observability in a multi-stage pipeline is not local to any single component. The failure originates in response_gen.py, the schema lives in logger.py, and the routing decision belongs to main.py. Each layer must agree on what data to produce, carry, and record. The refinement improved diagnostic value by surfacing per-attempt exception class names in structured logs rather than relying on stdout output.

Key Insight:
Silent fallbacks reduce crash risk but harm maintainability because they hide operational failures from structured logs. Retrofitting observability into an existing pipeline required coordinated changes across three layers — none of which could provide full visibility in isolation.

Final Outcome:
LLM failures are now visible in structured logs. Per-attempt error logs capture the actual exception class for each failed attempt. A 10-second timeout and one retry are in place for both endpoints. Fallback responses are distinguishable from real LLM responses. TTS and frontend behaviour are preserved in all paths. Across the initial implementation and refinement, all test cases — normal flow, full failure, retry success, timeout fallback, and recovery — were validated through structured logs.

Observed Findings:
- Normal success: single status=success entry, retry_count=0, fallback_used=false
- Retry success: status=error retry_count=0, then status=success retry_count=1, fallback_used=false
- Full failure: two status=error entries (one per attempt) followed by status=fallback, error_type=LLMFailure
- SDK exception class names (e.g. NotFoundError) appear directly in per-attempt error logs
- TTS continuation on fallback path required no additional branching
- Both /talk/ and /text-talk/ validated across all test states
- Artificial failure triggers removed after validation

Relevance to Thesis:
1. Observability as a Maintenance Requirement — silent fallbacks are indistinguishable from successes without intentional log design
2. Integration Complexity — adding observability to one stage required coordinated changes across three layers
3. Complexity Redistribution — AI-assisted development reduced implementation effort; main effort shifted to return type propagation, schema alignment, and validation
4. Graceful Degradation — fallback responses can preserve frontend consistency without structural pipeline changes when failure is isolated to the LLM stage

Included in Thesis Scenario Metrics:
YES
