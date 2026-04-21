[SCENARIO 3 — STT RELIABILITY IMPROVEMENT]

Objective:
Improve the reliability of speech-to-text transcription for English voice input by forcing English transcription and adding safer handling of failed or unreliable STT results.

Why This Scenario Was Chosen:
A real failure was observed where clearly spoken English was transcribed incorrectly or in another language. Because Whisper defaults to auto-detecting the input language, ambient noise or brief utterances could trigger a non-English detection path.

The resulting incorrect transcript was passed unchanged to emotion detection and the LLM, producing wrong emotion labels and contextually irrelevant responses. This makes STT reliability a correctness issue, not only a performance issue.

A failure at the STT stage silently propagates through every downstream stage — emotion detection, response generation, and text-to-speech — producing a response that appears valid but is entirely incorrect.

Scope:
- Force English-only transcription using Whisper parameters
- Improve detection of unreliable or gibberish STT output
- Add a fallback gate to prevent unreliable STT from reaching downstream stages
- Add debug visibility for raw transcription output
- Keep emotion, LLM, and TTS stages unchanged
- Validate improvements using manual testing and existing logs

Baseline (Before Change):
- Whisper used default auto language detection
- English speech was occasionally transcribed as another language
- Incorrect STT output was passed directly to emotion detection and LLM
- No mechanism existed to block unreliable STT output
- No visibility into raw STT output for debugging
- Issue occurred despite good microphone quality

Changes Implemented:

backend/speech_to_text.py:
- Added language="en" and task="transcribe" to force English transcription
- Introduced improved reliability checks:
  - near-empty output detection
  - non-ASCII detection
  - long token detection
- Added [STT RAW]: debug print for transcription visibility
- Updated transcription function to return None if output is unreliable after retry

main.py:
- Added gate after STT:
  - if transcription is None → do not proceed to emotion or LLM
  - return fallback response instead
- Added structured logging for failure cases:
  - stage=stt
  - status=error
  - error_type=UnreliableSTT
- Ensured TTS still runs for fallback response to maintain frontend consistency

Fallback Response:
"I'm having trouble understanding the audio. Could you please try again?"

Measurement Method:
- Manual testing of English speech inputs before and after changes
- Inspection of [STT RAW] console output
- Verification of downstream behavior (emotion + response correctness)
- Structured logs used to confirm:
  - successful vs failed STT
  - fallback triggering behavior

Work Sessions:
Session 1: ~5 minutes — Implementation: English enforcement, STT gating, fallback handling, debug logging, documentation
Session 2: ~3 minutes — Refinement: improved decoding stability, sanity checks, retry logic, validation

Development Approach:

The implementation was carried out using AI-assisted development. The measured time represents the workflow from submitting the implementation prompt to final manual validation.

This includes:
- AI generation of the code changes
- high-level review of the generated code
- running the system and executing manual test cases
- validating runtime behavior through logs and outputs

No manual re-implementation without AI assistance was performed. The primary effort was focused on validation, debugging, and ensuring correct system behavior rather than writing code from scratch.

Total Time:
~8 minutes

Iterations:
2

Files Changed:
backend/speech_to_text.py
main.py
docs/scenario_3_stt_reliability.md

Issues Faced:
- Whisper mis-transcription even for clear English speech
- Lack of reliability indicators in default Whisper output
- Need to distinguish between “successful” and “correct” STT output
- Balancing fallback sensitivity without over-triggering

Outcome:
The STT stage now enforces English transcription and blocks unreliable outputs from entering the pipeline. When transcription cannot be trusted, a safe fallback response is returned instead of propagating incorrect input. Downstream stages now receive significantly cleaner input.
This change improved system correctness without modifying downstream models or response generation logic.

Observed Findings:
- Incorrect language outputs (e.g., Hindi) were eliminated
- Transcription became more consistent for English input
- Downstream responses became more relevant due to improved input quality
- STT is significantly more stable but still not perfectly accurate for short or ambiguous phrases
- The system now avoids producing misleading responses based on incorrect input

Key Insight:
Improving input correctness reduces error propagation across the entire AI pipeline. Even without changes to the LLM, overall response quality improved due to better STT reliability.

Relevance to Thesis:
1. Correctness and Reliability — demonstrates how small configuration changes can significantly improve system correctness
2. Error Propagation — shows how early-stage errors affect all downstream AI components
3. Effort Distribution — highlights that most effort lies in validation and debugging rather than implementation
4. System Behavior — confirms that AI pipelines are sensitive to input quality and remain probabilistic

Included in Thesis Scenario Metrics:
YES

---

[REFINEMENT — IMPROVED TRANSCRIPTION STABILITY]

Changes Made:
- Reduced decoding randomness using temperature=0 (greedy decoding)
- Added retry with slight variation (temperature=0.2)
- Introduced expanded sanity checks:
  - long output detection
  - repetition detection
  - hallucination phrase filtering (e.g., "thank you for watching")
- Improved retry handling and debug visibility ([STT RAW retry])

Observations:
- Transcription became more consistent across repeated runs
- Fewer semantically incorrect phrases were observed
- Common Whisper hallucination cases were reduced
- Fallback triggered only when truly necessary

Additional Insight:
Even after refinement, STT remains probabilistic and cannot guarantee perfect transcription. However, reliability improvements significantly reduce incorrect downstream behavior.