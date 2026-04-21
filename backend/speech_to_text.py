import whisper
import re
import torch

device = "cuda" if torch.cuda.is_available() else "cpu"
model = whisper.load_model("medium", device=device)
print(f"[GPU] Whisper running on: {device}")

# Known Whisper hallucination phrases that appear when audio is silent or unclear
_HALLUCINATION_PHRASES = [
    "thank you for watching",
    "thanks for watching",
    "please subscribe",
    "like and subscribe",
    "see you next time",
    "subtitles by",
    "transcribed by",
    "www.",
    ".com",
]

def is_suspicious(text):
    """Detect unreliable or low-quality transcripts.

    Returns True if the text should be treated as unreliable.
    Checks:
    - empty or near-empty output
    - non-ASCII characters (non-English script)
    - too many unusually long tokens
    - known Whisper hallucination phrases
    - single-character repetition (e.g. "ha ha ha ha ha")
    """
    if not text or not text.strip():
        return True

    stripped = text.strip()

    # Too short to be meaningful
    if len(stripped) < 3:
        return True

    # Excessively long output for a voice therapy input (> 300 chars suggests hallucination)
    if len(stripped) > 300:
        return True

    lower = stripped.lower()

    # Known hallucination phrases Whisper produces on near-silent audio
    if any(phrase in lower for phrase in _HALLUCINATION_PHRASES):
        return True

    words = stripped.split()

    # Non-ASCII characters indicate non-English script
    non_ascii_count = sum(1 for w in words if re.search(r"[^\x00-\x7F]", w))
    if non_ascii_count > len(words) * 0.4:
        return True

    # Unusually long tokens
    long_word_count = sum(1 for w in words if len(w) > 15)
    if long_word_count > len(words) * 0.4:
        return True

    # Repetitive filler: same word repeated more than half the output
    if len(words) >= 4:
        most_common_count = max(words.count(w) for w in set(words))
        if most_common_count > len(words) * 0.6:
            return True

    return False


def transcribe_audio(file_path):
    """Transcribes audio to text using Whisper, forced to English.

    First attempt uses temperature=0 (greedy, most stable).
    If that produces a suspicious result, retries once with temperature=0.2
    to allow slight decoding variation.

    Returns the transcribed text, or None if both attempts are unreliable.
    """
    # Attempt 1: greedy decoding — most stable, least random
    result = model.transcribe(
        file_path,
        language="en",
        task="transcribe",
        temperature=0,
        best_of=1,
    )
    text = result["text"].strip()
    print(f"[STT RAW]: {text}")

    if not is_suspicious(text):
        return text

    print(f"[Warning] Suspicious STT on attempt 1: '{text}' — retrying")

    # Attempt 2: slight temperature to allow variation if greedy output was wrong
    result = model.transcribe(
        file_path,
        language="en",
        task="transcribe",
        temperature=0.2,
        best_of=1,
    )
    text = result["text"].strip()
    print(f"[STT RAW retry]: {text}")

    if not is_suspicious(text):
        return text

    print(f"[Warning] Unreliable STT on attempt 2: '{text}' — triggering fallback")
    return None
