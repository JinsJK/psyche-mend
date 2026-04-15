import whisper
import re
import torch

device = "cuda" if torch.cuda.is_available() else "cpu"
model = whisper.load_model("medium", device=device)
print(f"[GPU] Whisper running on: {device}")

def is_gibberish(text):
    """Detect gibberish or low-quality transcripts."""
    if not text.strip():
        return True
    gibberish_score = sum(
        1 for w in text.split() if len(w) > 15 or re.search(r"[^a-zA-Z0-9\s,.?!']", w)
    )
    return gibberish_score > len(text.split()) * 0.4

def transcribe_audio(file_path):
    """Transcribes audio to text using Whisper."""
    for attempt in range(2):
        result = model.transcribe(file_path)
        text = result["text"].strip()
        if not is_gibberish(text):
            return text
        print(f"[Warning] Gibberish on attempt {attempt + 1}: '{text}'")
    return text
