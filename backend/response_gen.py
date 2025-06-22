import os
import openai

openai.api_key = os.getenv("OPENAI_API_KEY")

BLOCKED_PHRASES = [
    "who is", "who was", "what is", "define", "tell me about",
    "capital of", "history of"
]

def generate_response(user_text, emotion, chat_history=None):
    """Generates a therapeutic AI response using OpenAI."""
    if any(phrase in user_text.lower() for phrase in BLOCKED_PHRASES):
        return (
            "I'm here to support your emotional and mental well-being. "
            "Let's talk about how you're feeling today instead."
        )

    messages = [{
        "role": "system",
        "content": (
            "You are a licensed therapist. Only provide emotional and psychological support. "
            "Do not suggest any external or professional support. "
            "Gently guide the conversation back to the user's emotional state."
        )
    }]

    chat_history = chat_history or []
    for turn in chat_history[-5:]:
        messages.append({"role": "user", "content": turn["user"]})
        messages.append({"role": "assistant", "content": turn["reply"]})

    messages.append({
        "role": "user",
        "content": f"The user sounds {emotion}. They said: '{user_text}'"
    })

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages
        )
        return response.choices[0].message["content"]
    except Exception as e:
        print(f"[OpenAI Error] {e}")
        return "I'm here to support you. Could you tell me a bit more?"
