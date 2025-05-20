import os
import uuid
import shutil
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import FileResponse
from typing import Optional
import uvicorn
from vad import detect_speech
from audio_utils import process_audio

app = FastAPI(title="Voice Processing API")
TEMP_DIR = "temp"
OUTPUT_DIR = "output"

# Ensure temp and output directories exist
os.makedirs(TEMP_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

@app.post("/process-audio/")
async def process_audio_endpoint(audio: UploadFile = File(...)):
    """
    Process uploaded audio file with Voice Activity Detection
    """
    # Generate unique filename
    file_id = str(uuid.uuid4())
    input_path = os.path.join(TEMP_DIR, f"{file_id}_input.wav")
    output_path = os.path.join(OUTPUT_DIR, f"{file_id}_output.wav")
    
    # Save uploaded file
    with open(input_path, "wb") as buffer:
        shutil.copyfileobj(audio.file, buffer)
    
    # Perform Voice Activity Detection
    has_speech = detect_speech(input_path)
    
    if has_speech:
        # Process audio file (could include transcription, analysis, etc.)
        process_audio(input_path, output_path)
    else:
        # No speech detected, return silent response or prompt
        create_no_speech_response(output_path)
    
    # Return processed audio file
    return FileResponse(
        output_path, 
        media_type="audio/wav",
        headers={"X-Speech-Detected": str(has_speech)}
    )

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "audio-processing"}

def create_no_speech_response(output_path):
    """Create response for when no speech is detected"""
    # In a real system, this might be a pre-recorded prompt like
    # "I didn't hear anything, please try again"
    silent_response = os.path.join(os.path.dirname(__file__), "assets", "no_speech.wav")
    shutil.copy(silent_response, output_path)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)