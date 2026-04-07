[BASELINE RESTORATION LOG]

Date:
2026-04-06

Issue:
Deprecated sentiment pipeline parameter blocked all /talk/ and /text-talk/ requests.

Category:
Baseline Restoration – Compatibility Fix

Severity:
Critical

What was deprecated:
`return_all_scores=True` parameter in the `transformers` pipeline constructor.

Library Causing the Issue:
`transformers==4.36.2`

Root Cause:
This version no longer supports `return_all_scores`, which caused the pipeline to return data in an unexpected structure. As a result, iterating over the output with `x["score"]` raised:
`TypeError: string indices must be integers`

Fix Applied:
Replaced `return_all_scores=True` with `top_k=None`, which is the current equivalent for returning all label scores.

Files Changed:
`backend/sentiment.py` — one parameter change

Behavior Change:
None. The output of `detect_emotion()` remains unchanged because the pipeline still returns the full list of `{ "label": ..., "score": ... }` dictionaries, allowing `max()` to identify the top emotion as before.

Type of Work:
Compatibility / Dependency / Debugging

Time Spent:
< 1 minute

Impact:
Blocked all `/talk/` and `/text-talk/` requests until fixed.

Included in Thesis Scenario Metrics:
NO

Notes:
This fix was required to restore baseline execution and is therefore classified as baseline restoration rather than a formal thesis update scenario.

---

[BASELINE RESTORATION LOG]

Date:
2026-04-06

Issue:
OpenAI API key not loaded — all LLM calls silently failed and returned a fallback response.

Category:
Baseline Restoration – Configuration Fix

Severity:
Critical

Root Cause:
`load_dotenv()` was never called in `main.py`, so the `.env` file containing `OPENAI_API_KEY` was never read. `os.getenv("OPENAI_API_KEY")` returned `None`, causing every call to `openai.ChatCompletion.create()` to raise an authentication error.

Fix Applied:
Added `from dotenv import load_dotenv` and `load_dotenv()` at the top of `main.py`.

Files Changed:
`main.py` — two lines added at the top

Behavior Change:
None. `.env` and `OPENAI_API_KEY` were always intended to be used; the call to load them was simply missing.

Type of Work:
Configuration / Integration / Debugging

Time Spent:
[fill in actual time]

Impact:
All responses fell back to the hardcoded string "I'm here to support you. Could you tell me a bit more?" instead of calling GPT.

Included in Thesis Scenario Metrics:
NO

Notes:
This fix was required to restore baseline execution and is therefore classified as baseline restoration rather than a formal thesis update scenario.