from dotenv import load_dotenv
load_dotenv()

import torch
print(f"[GPU] CUDA available: {torch.cuda.is_available()}")
print(f"[GPU] Device: {'cuda' if torch.cuda.is_available() else 'cpu'}")

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
from backend.config import OPENAI_MODEL, WHISPER_LOG_MODEL_NAME, EMOTION_MODEL_NAME, TTS_MODEL_NAME


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
    stt_duration_ms = (time.perf_counter() - t0) * 1000

    if text is None:
        log_event(request_id, "stt", "error", duration_ms=stt_duration_ms, model=WHISPER_LOG_MODEL_NAME, error_type="UnreliableSTT", input_type="voice")
        fallback_text = "I'm having trouble understanding the audio. Could you please try again?"
        t0 = time.perf_counter()
        tts_result = synthesize_speech(fallback_text, output_path)
        if tts_result is None:
            log_event(request_id, "tts", "error", duration_ms=(time.perf_counter() - t0) * 1000, error_type="TTSError", model=TTS_MODEL_NAME, input_type="voice")
        else:
            log_event(request_id, "tts", "success", duration_ms=(time.perf_counter() - t0) * 1000, model=TTS_MODEL_NAME, input_type="voice")
        for _ in range(50):
            if os.path.exists(output_path):
                break
            time.sleep(0.1)
        log_event(request_id, "api_end", "success", duration_ms=(time.perf_counter() - t_request_start) * 1000, input_type="voice")
        return JSONResponse({
            "transcript": "",
            "emotion": "unknown",
            "reply_text": fallback_text,
            "reply_audio_url": f"/audio/{audio_id}_reply.wav"
        })

    log_event(request_id, "stt", "success", duration_ms=stt_duration_ms, model=WHISPER_LOG_MODEL_NAME, input_type="voice")

    t0 = time.perf_counter()
    emotion = detect_emotion(text)
    log_event(request_id, "emotion", "success", duration_ms=(time.perf_counter() - t0) * 1000, emotion=emotion, model=EMOTION_MODEL_NAME, input_type="voice")

    history = chat_histories.get(session_id, [])

    t0 = time.perf_counter()
    reply, retry_count, fallback_used, attempt_errors = generate_response(text, emotion, history)
    llm_duration = (time.perf_counter() - t0) * 1000
    for i, err in enumerate(attempt_errors):
        log_event(request_id, "llm", "error", emotion=emotion, model=OPENAI_MODEL, input_type="voice", retry_count=i, fallback_used=False, error_type=err)
    if fallback_used:
        log_event(request_id, "llm", "fallback", duration_ms=llm_duration, emotion=emotion, model=OPENAI_MODEL, input_type="voice", retry_count=retry_count, fallback_used=True, error_type="LLMFailure")
    else:
        log_event(request_id, "llm", "success", duration_ms=llm_duration, emotion=emotion, model=OPENAI_MODEL, input_type="voice", retry_count=retry_count, fallback_used=False)

    t0 = time.perf_counter()
    tts_result = synthesize_speech(reply, output_path)
    if tts_result is None:
        log_event(request_id, "tts", "error", duration_ms=(time.perf_counter() - t0) * 1000, error_type="TTSError", model=TTS_MODEL_NAME, input_type="voice")
    else:
        log_event(request_id, "tts", "success", duration_ms=(time.perf_counter() - t0) * 1000, model=TTS_MODEL_NAME, input_type="voice")

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
    log_event(request_id, "emotion", "success", duration_ms=(time.perf_counter() - t0) * 1000, emotion=emotion, model=EMOTION_MODEL_NAME, input_type="text")

    history = chat_histories.get(session_id, [])

    t0 = time.perf_counter()
    reply, retry_count, fallback_used, attempt_errors = generate_response(user_text, emotion, history)
    llm_duration = (time.perf_counter() - t0) * 1000
    for i, err in enumerate(attempt_errors):
        log_event(request_id, "llm", "error", emotion=emotion, model=OPENAI_MODEL, input_type="text", retry_count=i, fallback_used=False, error_type=err)
    if fallback_used:
        log_event(request_id, "llm", "fallback", duration_ms=llm_duration, emotion=emotion, model=OPENAI_MODEL, input_type="text", retry_count=retry_count, fallback_used=True, error_type="LLMFailure")
    else:
        log_event(request_id, "llm", "success", duration_ms=llm_duration, emotion=emotion, model=OPENAI_MODEL, input_type="text", retry_count=retry_count, fallback_used=False)

    audio_id = str(uuid.uuid4())
    output_path = f"audio/{audio_id}_reply.wav"

    t0 = time.perf_counter()
    tts_result = synthesize_speech(reply, output_path)
    if tts_result is None:
        log_event(request_id, "tts", "error", duration_ms=(time.perf_counter() - t0) * 1000, error_type="TTSError", model=TTS_MODEL_NAME, input_type="text")
    else:
        log_event(request_id, "tts", "success", duration_ms=(time.perf_counter() - t0) * 1000, model=TTS_MODEL_NAME, input_type="text")

    history.append({"user": user_text, "reply": reply})
    chat_histories[session_id] = history

    log_event(request_id, "api_end", "success", duration_ms=(time.perf_counter() - t_request_start) * 1000, input_type="text")
    return JSONResponse({
        "transcript": user_text,
        "emotion": emotion,
        "reply_text": reply,
        "reply_audio_url": f"/audio/{audio_id}_reply.wav"
    })
