from transformers import pipeline

# Load sentiment/emotion model once
emotion_classifier = pipeline(
    "text-classification",
    model="j-hartmann/emotion-english-distilroberta-base",
    return_all_scores=True
)

def detect_emotion(text):
    """Detect the primary emotion from input text."""
    result = emotion_classifier(text)[0]
    top = max(result, key=lambda x: x["score"])
    return top["label"].lower()
