# Voice Processing HTTP Server

This is a FastAPI-based HTTP server that provides a REST API for voice processing with Voice Activity Detection (VAD). It detects speech in uploaded audio files and processes them accordingly.

## Features

- **Voice Activity Detection (VAD)**: Automatically detect speech in uploaded audio files
- **Audio Processing**: Process audio files with speech normalization, noise reduction, and compression
- **REST API**: Simple HTTP interface for integrating voice processing into any application

## API Endpoints

### POST `/process-audio/`

Processes an uploaded audio file:
- Detects if the file contains speech
- If speech is detected, processes the audio (normalization, filtering, compression)
- If no speech is detected, returns a predefined "no speech detected" response
- Returns the processed audio as a WAV file

**Headers in response**:
- `X-Speech-Detected`: Boolean indicating whether speech was detected

### GET `/health`

Health check endpoint that returns the service status.

## Directory Structure

- `app.py`: Main FastAPI application with endpoint definitions
- `vad.py`: Voice Activity Detection implementation using webrtcvad
- `audio_utils.py`: Audio processing utilities
- `temp/`: Temporary directory for storing uploaded audio files
- `output/`: Directory for storing processed audio files

## Requirements

- Python 3.12+
- FastAPI
- uvicorn
- webrtcvad
- pydub
- numpy
- soundfile

## Installation

1. Install the requirements:

```bash
pip install -r requirements.txt
```

2. Run the server:

```bash
cd http_serve
python app.py
```

The server will start on http://0.0.0.0:8000

## Development

### Environment Setup

It's recommended to use a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Testing the API

You can test the API using curl:

```bash
curl -X POST -F "audio=@/path/to/your/audio.wav" http://localhost:8000/process-audio/ --output processed.wav
```

Or use the Swagger UI at http://localhost:8000/docs

## How It Works

1. When an audio file is uploaded to `/process-audio/`, it's saved to the `temp/` directory
2. The VAD detector analyzes the audio to check for speech
3. If speech is detected, the audio is processed with normalization, filtering, and compression
4. The processed audio is saved to the `output/` directory and returned to the client
5. If no speech is detected, a predefined "no speech detected" response is returned
