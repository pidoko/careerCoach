import subprocess
import os

def transcribe_audio(filepath: str) -> str:
    """
    Transcribes an audio file using SoX for preprocessing and Whisper.cpp for transcription.

    This function:
    - Uses SoX to resample and convert the audio file to a standard format.
    - Runs Whisper.cpp's CLI to perform speech-to-text transcription.
    - Returns the transcription result or a detailed error message.

    Parameters
    ----------
    filepath : str
        Path to the input audio file (typically a WAV file).

    Returns
    -------
    str
        Transcription result text, or an error message if processing fails.

    Notes
    -----
    - Expects both `whisper-cli.exe` and `sox.exe` to be present in specified backend folders.
    - Assumes Whisper model file (`small.bin`) is available in the same folder as `whisper-cli.exe`.
    """

    backend_dir = os.path.dirname(__file__)

    # Define external tool paths
    whisper_path = os.path.join(backend_dir, "whisper.cpp-1.7.4", "build", "bin", "Release", "whisper-cli.exe")
    sox_path = os.path.join(backend_dir, "sox-14-4-2", "sox.exe")

    # Validate required files exist
    if not os.path.exists(whisper_path):
        return "Error: whisper-cli.exe not found at expected location."

    if not os.path.exists(sox_path):
        return "Error: sox.exe not found in backend folder."

    if not os.path.exists(filepath):
        return f"Error: Audio file not found - {filepath}"

    # Prepare path for cleaned file (resampled, mono)
    cleaned_filepath = filepath.replace(".wav", "_clean.wav")

    # Run SoX to preprocess the audio (convert to 16k mono WAV)
    try:
        subprocess.run(
            [sox_path, filepath, cleaned_filepath, "rate", "16k", "channels", "1"],
            check=True,
            capture_output=True,
            text=True
        )
    except subprocess.CalledProcessError as e:
        return f"Error: SoX processing failed - {e.stderr.strip() or str(e)}"
    except FileNotFoundError:
        return "Error: SoX executable not found (check path)."

    # Confirm SoX created the output file
    if not os.path.exists(cleaned_filepath):
        return "Error: Cleaned audio file not found after SoX processing."

    # Run Whisper CLI on the cleaned file
    try:
        model_path = os.path.join(backend_dir, "whisper.cpp-1.7.4", "build", "bin", "Release", "small.bin")

        result = subprocess.run(
            [whisper_path, "--model", model_path, "--file", cleaned_filepath],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            return f"Error: Whisper CLI failed - {result.stderr.strip() or 'No error message returned.'}"

        transcription = result.stdout.strip()
        return transcription or "Error: Transcription completed but returned empty text."

    except Exception as e:
        return f"Error: Unexpected exception during transcription - {str(e)}"
