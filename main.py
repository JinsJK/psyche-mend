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
from backend.logger import log_event


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
    request_id = str(uuid.uuid4())

    raw_path = f"audio_samples/{audio_id}_raw.webm"
    input_path = f"audio_samples/{audio_id}_input.wav"
    output_path = f"audio/{audio_id}_reply.wav"

    t_request_start = time.perf_counter()
    log_event(request_id, "api_start", "success", input_type="voice")

    # Save and convert the uploaded audio
    with open(raw_path, "wb") as f:
        f.write(await audio.read())

    try:
        audio_segment = AudioSegment.from_file(raw_path)
        audio_segment.export(input_path, format="wav")
    except Exception as e:
        log_event(request_id, "api_start", "error", error_type="AudioConversionError", input_type="voice")
        return JSONResponse(status_code=500, content={"error": f"Audio conversion failed: {str(e)}"})

    t0 = time.perf_counter()
    text = transcribe_audio(input_path)
    log_event(request_id, "stt", "success", duration_ms=(time.perf_counter() - t0) * 1000, model="whisper-medium", input_type="voice")

    t0 = time.perf_counter()
    emotion = detect_emotion(text)
    log_event(request_id, "emotion", "success", duration_ms=(time.perf_counter() - t0) * 1000, emotion=emotion, model="j-hartmann/emotion-english-distilroberta-base", input_type="voice")

    history = chat_histories.get(session_id, [])

    t0 = time.perf_counter()
    reply = generate_response(text, emotion, history)
    log_event(request_id, "llm", "success", duration_ms=(time.perf_counter() - t0) * 1000, emotion=emotion, model="gpt-3.5-turbo", input_type="voice")

    t0 = time.perf_counter()
    tts_result = synthesize_speech(reply, output_path)
    if tts_result is None:
        log_event(request_id, "tts", "error", duration_ms=(time.perf_counter() - t0) * 1000, error_type="TTSError", model="tts_models/en/vctk/vits", input_type="voice")
    else:
        log_event(request_id, "tts", "success", duration_ms=(time.perf_counter() - t0) * 1000, model="tts_models/en/vctk/vits", input_type="voice")

    history.append({"user": text, "reply": reply})
    chat_histories[session_id] = history

    for _ in range(50):
        if os.path.exists(output_path):
            break
        time.sleep(0.1)

    log_event(request_id, "api_end", "success", duration_ms=(time.perf_counter() - t_request_start) * 1000, input_type="voice")
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
    request_id = str(uuid.uuid4())

    t_request_start = time.perf_counter()
    log_event(request_id, "api_start", "success", input_type="text")

    t0 = time.perf_counter()
    emotion = detect_emotion(user_text)
    log_event(request_id, "emotion", "success", duration_ms=(time.perf_counter() - t0) * 1000, emotion=emotion, model="j-hartmann/emotion-english-distilroberta-base", input_type="text")

    history = chat_histories.get(session_id, [])

    t0 = time.perf_counter()
    reply = generate_response(user_text, emotion, history)
    log_event(request_id, "llm", "success", duration_ms=(time.perf_counter() - t0) * 1000, emotion=emotion, model="gpt-3.5-turbo", input_type="text")

    audio_id = str(uuid.uuid4())
    output_path = f"audio/{audio_id}_reply.wav"

    t0 = time.perf_counter()
    tts_result = synthesize_speech(reply, output_path)
    if tts_result is None:
        log_event(request_id, "tts", "error", duration_ms=(time.perf_counter() - t0) * 1000, error_type="TTSError", model="tts_models/en/vctk/vits", input_type="text")
    else:
        log_event(request_id, "tts", "success", duration_ms=(time.perf_counter() - t0) * 1000, model="tts_models/en/vctk/vits", input_type="text")

    history.append({"user": user_text, "reply": reply})
    chat_histories[session_id] = history

    log_event(request_id, "api_end", "success", duration_ms=(time.perf_counter() - t_request_start) * 1000, input_type="text")
    return JSONResponse({
        "transcript": user_text,
        "emotion": emotion,
        "reply_text": reply,
        "reply_audio_url": f"/audio/{audio_id}_reply.wav"
    })
