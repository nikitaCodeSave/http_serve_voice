# Voice Processing HTTP Server

This is a FastAPI-based HTTP server that provides a REST API for voice processing with Voice Activity Detection (VAD). It detects speech in uploaded audio files and processes them accordingly.

## Features

- **Voice Activity Detection (VAD)**: Automatically detects speech in uploaded audio files using the `webrtcvad` library. This helps in identifying segments of audio that contain voice, ignoring silence or noise-only parts.
- **Audio Processing**: Once speech is detected, the audio undergoes several processing steps to enhance its quality:
    - **Normalization**: Adjusts the audio to a standard volume level.
    - **Noise Reduction**: Applies a high-pass filter to reduce low-frequency noise.
    - **Compression**: Compresses the dynamic range of the audio to ensure consistent volume levels.
- **REST API**: Simple HTTP interface for integrating voice processing into any application

## Use Cases

This voice processing server can be a valuable component in various applications, including:

-   **Pre-processing for Transcription Services**: Clean and normalize audio before sending it to a speech-to-text engine to improve transcription accuracy.
-   **Automated Content Archival**: Filter and process large volumes of audio recordings (e.g., meetings, lectures) to store only relevant speech segments, reducing storage costs and improving searchability.
-   **Voice Command Systems**: Detect the presence of voice commands in an audio stream before attempting to interpret the command, making the system more efficient.
-   **Content Moderation**: Quickly identify if audio content contains speech, as a first step in moderating user-generated audio content for platforms.
-   **Interactive Voice Response (IVR) Systems**: Detect when a caller is speaking to improve the responsiveness and accuracy of IVR interactions.
-   **Audio Analytics**: Isolate speech segments for further analysis, such as speaker diarization, emotion detection, or keyword spotting.

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

The audio processing pipeline involves several steps, coordinated by `app.py` and utilizing `vad.py` for voice activity detection and `audio_utils.py` for audio manipulation:

1.  **File Upload and Temporary Storage (`app.py`)**:
    *   When a client sends a POST request to the `/process-audio/` endpoint with an audio file, `app.py` receives the uploaded file.
    *   A unique file ID (UUID) is generated for this request.
    *   The uploaded audio file is saved into the `temp/` directory with a filename incorporating this unique ID (e.g., `temp/<uuid>_input.wav`).

2.  **Voice Activity Detection (`app.py` -> `vad.py`)**:
    *   `app.py` calls the `detect_speech()` function in `vad.py`, passing the path to the temporary input file.
    *   Inside `vad.py`:
        *   The `VoiceActivityDetector` class is instantiated.
        *   The input WAV file is first validated using `validate_wav_file()`.
        *   The audio data is read using `_read_wave()`.
        *   If the audio is not in a format compatible with `webrtcvad` (16kHz mono, 16-bit PCM), it's converted using `_convert_audio()` which leverages the `pydub` library.
        *   The audio is divided into 30ms frames.
        *   The `webrtcvad.Vad` instance checks each frame for speech.
        *   If the percentage of speech frames exceeds a predefined threshold (currently 5%), `detect_from_file()` returns `True`, otherwise `False`.
    *   The result (`has_speech`) is returned to `app.py`.

3.  **Audio Processing or "No Speech" Handling (`app.py` -> `audio_utils.py`)**:
    *   **If `has_speech` is `True`**:
        *   `app.py` calls the `process_audio()` function in `audio_utils.py`, providing the input path (from `temp/`) and a designated output path (e.g., `output/<uuid>_output.wav`).
        *   Inside `audio_utils.py`:
            *   The audio file is loaded using `AudioSegment.from_wav()`.
            *   The following processing steps are applied sequentially:
                1.  `normalize()`: Adjusts volume to a standard level.
                2.  `high_pass_filter(100)`: Removes frequencies below 100Hz for basic noise reduction.
                3.  `compress_dynamic_range()`: Evens out loud and quiet parts.
                4.  `speedup(playback_speed=1.2)`: Increases the playback speed of the audio.
            *   The processed audio is exported to the specified `output_path` in WAV format.
    *   **If `has_speech` is `False`**:
        *   `app.py` calls the `create_no_speech_response()` function.
        *   This function copies a predefined silent WAV file (from `assets/no_speech.wav`) to the designated output path (`output/<uuid>_output.wav`).

4.  **Response Generation (`app.py`)**:
    *   `app.py` uses `FileResponse` to send the audio file located at `output_path` back to the client.
    *   A custom header `X-Speech-Detected` is included in the response, indicating the outcome of the VAD process.

5.  **File Management**:
    *   Uploaded files are temporarily stored in the `temp/` directory. These files are the raw input.
    *   Processed audio files (either the result of `audio_utils.py` or the "no speech" audio) are saved in the `output/` directory.
    *   Currently, there is no explicit cleanup mechanism for files in `temp/` or `output/` mentioned in the provided code. In a production system, a cleanup strategy for these directories would be important.
