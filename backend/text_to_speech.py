from TTS.api import TTS
import torch

use_gpu = torch.cuda.is_available()
tts = TTS(model_name="tts_models/en/vctk/vits", progress_bar=False, gpu=use_gpu)
print(f"[GPU] TTS running on: {'cuda' if use_gpu else 'cpu'}")
default_speaker = "p243"

def synthesize_speech(text, output_path="reply.wav"):
    """Generate speech from text and save as audio."""
    try:
        tts.tts_to_file(text=text, file_path=output_path, speaker=default_speaker)
        return output_path
    except Exception as e:
        print(f"[TTS Error] Failed to generate audio: {e}")
        return None
