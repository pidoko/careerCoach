import sounddevice as sd # sounddevice is a Python library for playing and recording sounds through your computer's microphone and speakers.
import numpy as np # NumPy is a Python library used for working with arrays. It also has functions for working in domain of linear algebra, fourier transform, and matrices.
import threading # The threading module allows you to create threads, pause them, and resume them. It also allows you to pass arguments to the threads.
import os # The OS module in Python provides a way of using operating system dependent functionality. The functions that the OS module provides allows you to interface with the underlying operating system that Python is running on – be that Windows, Mac or Linux.
import scipy.io.wavfile as wav # The scipy.io.wavfile module is used to read and write WAV files using numpy arrays.

# Global state
recording_thread = None # The recording_thread variable is used to store the thread object that is created when the start_recording function is called.
recording_active = False # The recording_active variable is used to store the state of the recording thread. It is set to True when the start_recording function is called and set to False when the stop_recording function is called.
recording_buffer = [] # The recording_buffer variable is used to store the audio data that is recorded by the microphone. A list is used because I expect short recording durations.
samplerate = 16000 # What whisper expects


def audio_callback(indata, frames, time, status):
    """
    Callback function triggered by the sounddevice library when audio data is received from the microphone.

    Parameters:
    -----------
    indata : numpy.ndarray
        A NumPy array containing the incoming audio data for the current buffer.
    frames : int
        The number of frames in the audio buffer.
    time : CData
        Time information provided by the audio stream (start time, current time, etc.).
    status : sounddevice.CallbackFlags
        Status flag indicating if any underruns or overruns occurred during recording.

    Notes:
    ------
    This function appends the captured audio data to a global recording buffer if recording is active.
    """
    global recording_buffer

    if recording_active:
        # Store a copy of the incoming audio data to avoid overwriting during future callbacks
        recording_buffer.append(indata.copy())

def start_recording():
    """
    Starts continuous audio recording on a background thread.

    This function initializes a new recording session by:
    - Checking if a recording is already in progress.
    - Creating a new background thread to capture audio.
    - Using a sounddevice InputStream to continuously capture audio data.
    - Appending incoming audio data to a global recording buffer (for later processing or saving).

    Global Variables:
    -----------------
    recording_thread : threading.Thread
        Thread responsible for capturing audio.
    recording_active : bool
        Flag to control the recording loop.
    recording_buffer : list
        List used to store incoming audio data chunks.

    Notes:
    ------
    - This function supports continuous recording until `recording_active` is set to False.
    - Audio data is collected using the `audio_callback` function, which must be defined elsewhere.
    - Recording happens in 16-bit integer format (`int16`) and mono (`channels=1`).

    """
    global recording_thread, recording_active, recording_buffer

    if recording_thread is not None and recording_thread.is_alive():
        print("Recording is already in progress.")
        return

    print("Starting continuous recording...")

    # Initialize recording state
    recording_active = True
    recording_buffer = []

    def record():
        """Background recording loop running inside a thread."""
        with sd.InputStream(samplerate=samplerate, channels=1, dtype='int16', callback=audio_callback):
            while recording_active:
                sd.sleep(100)  # Keeps the thread alive, prevents busy looping

    # Create and start the background recording thread
    recording_thread = threading.Thread(target=record, daemon=True)
    recording_thread.start()

def stop_recording(filename='output.wav'):
    """
    Stops the active audio recording session and saves the recorded audio to a WAV file.

    This function:
    - Stops the background recording thread.
    - Concatenates all collected audio buffers into a single array.
    - Ensures the output directory exists if a path is provided.
    - Writes the final audio data to the specified WAV file.

    Parameters:
    -----------
    filename : str, optional
        The name (or full path) of the output WAV file. Defaults to 'output.wav'.

    Returns:
    --------
    str or None
        The filename if recording data was saved successfully, or None if no data was recorded.

    Global Variables:
    -----------------
    recording_active : bool
        Flag that controls the recording loop.
    recording_thread : threading.Thread
        The background thread responsible for audio capture.
    recording_buffer : list
        List storing the audio data buffers collected during the session.

    Notes:
    ------
    - If no data was recorded (e.g., the recording was started and stopped too quickly), no file is written.
    - The recording buffer is expected to contain arrays of consistent shape (mono channel).
    """
    global recording_active, recording_thread, recording_buffer, samplerate

    if not recording_active:
        print("No active recording to stop.")
        return None

    print("Stopping recording...")
    recording_active = False

    # Ensure recording thread has fully exited
    if recording_thread:
        recording_thread.join()

    if not recording_buffer:
        print("No audio data was recorded.")
        return None

    # Combine all recorded chunks into a single array
    audio_data = np.concatenate(recording_buffer, axis=0)

    # Ensure the target directory exists if a folder is specified
    folder = os.path.dirname(filename)
    if folder:
        os.makedirs(folder, exist_ok=True)

    # Save the final audio data to disk
    wav.write(filename, samplerate, audio_data)
    print(f"Audio saved to '{filename}'")

    return filename