from transformers import pipeline
from backend.config import EMOTION_MODEL_NAME

emotion_classifier = pipeline(
    "text-classification",
    model=EMOTION_MODEL_NAME,
    top_k=None
)

def detect_emotion(text):
    """Detect the primary emotion from input text."""
    result = emotion_classifier(text)[0]
    top = max(result, key=lambda x: x["score"])
    return top["label"].lower()
