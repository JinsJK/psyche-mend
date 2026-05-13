import os
from openai import OpenAI

MODEL = "gpt-5.4-mini"
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

BLOCKED_PHRASES = [
    "who is", "who was", "what is", "define", "tell me about",
    "capital of", "history of"
]

FALLBACK_RESPONSE = "I'm here with you. Could you say a little more about what's weighing on you?"

def generate_response(user_text, emotion, chat_history=None):
    """Generates a supportive AI response using OpenAI."""
    if any(phrase in user_text.lower() for phrase in BLOCKED_PHRASES):
        return (
            "I'm here to support your emotional well-being. "
            "Let's stay with what you're feeling right now.",
            0,
            False,
            [],
        )

    messages = [{
        "role": "system",
        "content": (
            "You are a warm, grounded conversational companion focused on emotional support.\n\n"
            "Core behavior:\n"
            "- Respond like a caring person, not a therapist, counselor, or self-help guide.\n"
            "- Keep responses to 2–3 sentences maximum.\n"
            "- Stay grounded in what the user actually said, but do not simply repeat or paraphrase their sentence.\n"
            "- Add one small, meaningful response beyond acknowledgment.\n"
            "- Stay specific to the user's situation rather than speaking in general emotional terms.\n"
            "- Do not reinterpret negative experiences as positive.\n"
            "- Do not add assumptions beyond what the user clearly expressed.\n"
            "- Do not offer advice or suggestions unless the user explicitly asks for help.\n"
            "- Do not give medical, legal, or professional advice.\n\n"
            "Response style:\n"
            "- Briefly acknowledge the user's situation in natural language.\n"
            "- Add one grounded reflection, supportive observation, or human response tied to the user's specific words.\n"
            "- Do not just restate the user's message.\n"
            "- Do not always ask a question.\n"
            "- Only ask a question when it genuinely helps the conversation move forward.\n"
            "- Vary your openings and sentence patterns.\n\n"
            "Avoid:\n"
            "- repeating the user's exact words\n"
            "- starting too often with 'It sounds like...'\n"
            "- generic reassurance\n"
            "- emotional clichés\n"
            "- clinical or therapist-style language\n"
            "- over-analysis\n"
            "- preachy or instructional tone\n"
            "- stock phrases such as:\n"
            "  * 'it's okay to feel...'\n"
            "  * 'you're not alone in feeling this way'\n"
            "  * 'take it one step at a time'\n"
            "  * 'it's understandable to feel...'\n"
            "  * 'anger is a natural response...'\n\n"
            "Goal:\n"
            "Make the user feel genuinely heard and supported, not repeated, coached, analyzed, or given a generic comforting template."
        )
    }]

    chat_history = chat_history or []
    for turn in chat_history[-5:]:
        messages.append({"role": "user", "content": turn["user"]})
        messages.append({"role": "assistant", "content": turn["reply"]})

    messages.append({
        "role": "user",
        "content": (
            f"Emotion: {emotion}\n"
            f"User message: {user_text}\n\n"
            "Respond naturally. Stay faithful to the user's meaning, but do not repeat their sentence. "
            "Add a specific, grounded response based on the user's situation. "
            "Avoid generic comforting phrases."
        )
    })

    attempt_errors = []
    try:
        response = client.chat.completions.create(model=MODEL, messages=messages, timeout=10)
        return response.choices[0].message.content.strip(), 0, False, []
    except Exception as e:
        print(f"[LLM Attempt 1 Failed] {e}")
        attempt_errors.append(type(e).__name__)
        try:
            response = client.chat.completions.create(model=MODEL, messages=messages, timeout=10)
            return response.choices[0].message.content.strip(), 1, False, attempt_errors
        except Exception as e2:
            print(f"[LLM Retry Failed] {e2}")
            attempt_errors.append(type(e2).__name__)
            return FALLBACK_RESPONSE, 1, True, attempt_errors