[SCENARIO 4 — PROMPT ENGINEERING FOR RESPONSE QUALITY]

Objective:
Improve response quality, naturalness, and emotional alignment of the LLM output using prompt engineering only, without modifying models, pipeline structure, or any other component.

Why This Scenario Was Chosen:
By Scenario 4, the pipeline was functioning correctly end-to-end: audio was transcribed accurately in English, emotions were detected reliably, and responses were being generated and spoken back. However, the LLM responses were consistently generic, repetitive, and lacking depth. Phrases like "How does that make you feel?" appeared across multiple turns regardless of context. The system was technically correct but qualitatively weak. Since the input quality was now reliable, the natural next intervention was to improve what the LLM was instructed to do with that input — through prompt engineering alone.

Scope:
- replace system prompt with a more structured and behaviorally specific version
- improve user message formatting passed to the LLM
- iterative refinement of prompt behavior
- no changes to STT, emotion detection, TTS, pipeline structure, or model selection

Baseline (Before Change):
- system prompt framed the assistant as a "licensed therapist" with no behavioral constraints
- user message format: "The user sounds {emotion}. They said: '{user_text}'"
- responses were repetitive and generic
- frequent use of clichés such as "How does that make you feel?"
- no control over response length, tone variation, or question usage

Changes Implemented:

Iteration 1 — Initial Prompt Improvement:
- replaced system prompt with structured behavioral guidelines
- introduced response length control (2–4 sentences)
- added emotion acknowledgment requirement
- reduced repetitive phrasing
- updated message format to:
  Emotion: {emotion}
  User message: {user_text}

Iteration 2 — Naturalness and Tone Refinement:
- removed therapist-style emotional generalizations
- eliminated instructional tone (no advice unless asked)
- reduced rigid response pattern (acknowledge → explain → question)
- enforced grounding to user's actual message
- reduced question frequency

Iteration 3 — Grounding and Interpretation Control:
- prevented positive reinterpretation of negative states
- reduced assumptions beyond user input
- enforced closer alignment to user wording
- restricted repetitive openers ("It sounds like…")
- added grounding instruction to user message:
  Respond based strictly on what the user said. Do not add assumptions or reinterpret their situation.

Iteration 4 — Parroting Issue Fix:
- identified over-restriction causing response parroting
- introduced rule: do not repeat user sentence verbatim; add a small meaningful response
- adjusted balance between grounding and expressiveness

Iteration 5 — Cliché and Constraint Saturation:
- attempted to eliminate generic emotional clichés
- explicitly banned phrases like "it's okay to feel…" and "you're not alone…"
- observed degradation: incorrect emotion interpretation, unstable responses, fallback to generic templates

Measurement Method:
- manual testing using consistent voice inputs
- qualitative comparison across iterations
- evaluation criteria: repetition, naturalness, emotional alignment, specificity, correctness

Work Sessions:
Session 1: ~16 minutes — full prompt design, iterative refinement across 5 iterations, and manual testing

Development Approach:

The implementation was carried out using AI-assisted development. The measured time represents the workflow from submitting the implementation prompt to final manual validation.

This includes:
- AI generation of the code changes
- high-level review of the generated code
- running the system and executing manual test cases
- validating runtime behavior through logs and outputs

No manual re-implementation without AI assistance was performed. The primary effort was focused on validation, debugging, and ensuring correct system behavior rather than writing code from scratch.

Total Time:
~16 minutes

Iterations:
5

Files Changed:
backend/response_gen.py         — updated system prompt and message formatting
docs/scenario_4_prompt_engineering.md — updated and appended

Issues Faced:
- repetitive and generic responses in baseline
- therapist-style phrasing persisted after initial improvement
- over-constraining prompt caused response parroting and reduced expressiveness
- model fell back to emotional clichés under heavy constraints
- incorrect emotional interpretation under excessive restrictions
- instability in response behavior across iterations

Outcome:
Prompt engineering improved response quality compared to the baseline by reducing repetition and improving tone. However, further refinement revealed diminishing returns. Excessive constraints degraded response quality, leading to unstable behavior, incorrect emotional interpretation, and fallback to generic templates.

Observed Findings:
- Prompt engineering significantly improves output quality initially
- Explicit constraints are required to reduce repetition and clichés
- Over-constraining the model leads to parroting, reduced reasoning, and incorrect emotional responses
- Models tend to revert to generic emotional templates when constrained heavily
- There is a trade-off between grounding (accuracy) and flexibility (naturalness)
- Optimal prompt design requires balancing these factors

Key Insight:
Prompt refinement demonstrated that too little guidance results in generic and repetitive responses, moderate guidance improves quality and naturalness, and excessive constraints degrade performance and stability. This indicates that prompt engineering has diminishing returns and cannot fully compensate for limitations of the underlying model.

Relevance to Thesis:
1. Output Quality Without Model Change — demonstrates that prompt design is a first-class engineering lever capable of meaningfully improving output without infrastructure changes
2. Diminishing Returns of Prompt Refinement — highlights that excessive constraints degrade model performance, establishing a practical ceiling for prompt-only improvement
3. AI-Assisted Iteration Process — the developer's role shifted to specifying behavioral requirements and validating outputs rather than writing model instructions from scratch
4. Establishes Need for Model-Level Improvement — results indicate that further quality gains require changes beyond prompt optimization

Included in Thesis Scenario Metrics:
YES
