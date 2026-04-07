from dotenv import load_dotenv
load_dotenv()

import os
import uuid
import time
import glob

from fastapi import FastAPI, UploadFile, File, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydub import AudioSegment

from backend.speech_to_text import transcribe_audio
from backend.sentiment import detect_emotion
from backend.response_gen import generate_response
from backend.text_to_speech import synthesize_speech


#Cleanup old audio files on startup
def clear_audio_folders():
    for folder in ["audio", "audio_samples"]:
        for file_path in glob.glob(f"{folder}/*.wav"):
            try:
                os.remove(file_path)
                print(f"[Startup Cleanup] Deleted: {file_path}")
            except Exception as e:
                print(f"[Error] Could not delete {file_path}: {e}")


app = FastAPI()

# Cleanup audio files at launch
clear_audio_folders()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs("audio", exist_ok=True)
os.makedirs("audio_samples", exist_ok=True)
app.mount("/audio", StaticFiles(directory="audio"), name="audio")

chat_histories = {}

#Voice input endpoint
@app.post("/talk/")
async def talk(request: Request, audio: UploadFile = File(...)):
    session_id = request.client.host
    audio_id = str(uuid.uuid4())

    raw_path = f"audio_samples/{audio_id}_raw.webm"
    input_path = f"audio_samples/{audio_id}_input.wav"
    output_path = f"audio/{audio_id}_reply.wav"

    # Save and convert the uploaded audio
    with open(raw_path, "wb") as f:
        f.write(await audio.read())

    try:
        audio_segment = AudioSegment.from_file(raw_path)
        audio_segment.export(input_path, format="wav")
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": f"Audio conversion failed: {str(e)}"})


    text = transcribe_audio(input_path)
    emotion = detect_emotion(text)
    history = chat_histories.get(session_id, [])
    reply = generate_response(text, emotion, history)
    synthesize_speech(reply, output_path)


    history.append({"user": text, "reply": reply})
    chat_histories[session_id] = history


    for _ in range(50):
        if os.path.exists(output_path):
            break
        time.sleep(0.1)

    return JSONResponse({
        "transcript": text,
        "emotion": emotion,
        "reply_text": reply,
        "reply_audio_url": f"/audio/{audio_id}_reply.wav"
    })


#Text input endpoint
@app.post("/text-talk/")
async def text_talk(request: Request):
    payload = await request.json()
    user_text = payload.get("text", "")
    session_id = request.client.host

    emotion = detect_emotion(user_text)
    history = chat_histories.get(session_id, [])
    reply = generate_response(user_text, emotion, history)

    audio_id = str(uuid.uuid4())
    output_path = f"audio/{audio_id}_reply.wav"
    synthesize_speech(reply, output_path)

    history.append({"user": user_text, "reply": reply})
    chat_histories[session_id] = history

    return JSONResponse({
        "transcript": user_text,
        "emotion": emotion,
        "reply_text": reply,
        "reply_audio_url": f"/audio/{audio_id}_reply.wav"
    })
