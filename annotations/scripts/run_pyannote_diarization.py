import os
import librosa
import soundfile as sf
import torch
from pyannote.audio.pipelines import SpeakerDiarization
from pyannote.audio.pipelines.utils.hook import ProgressHook

# ------------------------------------------------------------------
# 1. Load pretrained diarization model
# ------------------------------------------------------------------
pipeline = SpeakerDiarization.from_pretrained(
    "pyannote/speaker-diarization-3.1",
    use_auth_token="yurtoken"  # <-- replace with your actual token
)

# Send model to GPU if available
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
pipeline.to(device)


def process_audio(input_path, output_path, target_sr=16000):
    """Convert audio to 16kHz mono and save."""
    audio, sr = librosa.load(input_path, sr=target_sr, mono=True)
    sf.write(output_path, audio, target_sr)


def diarize_folder(main_input_folder, main_output_folder):
    """Process subfolders containing .wav files, convert, and diarize."""
    for subfolder in sorted(os.listdir(main_input_folder)):
        subfolder_path = os.path.join(main_input_folder, subfolder)

        # Skip if not a folder or already processed
        if not os.path.isdir(subfolder_path) or subfolder.endswith("_done"):
            print(f"Skipping {subfolder_path} (not a folder or already processed).")
            continue

        print(f"\n=== Processing folder: {subfolder} ===")

        # Find WAV files
        wav_files = [f for f in os.listdir(subfolder_path) if f.lower().endswith(".wav")]
        if not wav_files:
            print(f"No WAV file found in {subfolder}, skipping...")
            continue

        # Create corresponding output subfolder
        output_subfolder = os.path.join(main_output_folder, subfolder)
        os.makedirs(output_subfolder, exist_ok=True)

        for wav_file in wav_files:
            input_wav_path = os.path.join(subfolder_path, wav_file)
            output_wav_path = os.path.join(output_subfolder, wav_file.replace(".wav", "_16k.wav"))
            output_rttm_path = os.path.join(output_subfolder, wav_file.replace(".wav", "_py.rttm"))

            print(f"→ Converting {wav_file} to 16kHz mono...")
            process_audio(input_wav_path, output_wav_path)

            print(f"→ Running diarization on {wav_file}...")
            with ProgressHook() as hook:
                diarization = pipeline(output_wav_path, hook=hook)

            # Save RTTM
            with open(output_rttm_path, "w") as f:
                for turn, _, speaker in diarization.itertracks(yield_label=True):
                    f.write(
                        f"SPEAKER {wav_file} 1 {turn.start:.2f} {turn.duration:.2f} "
                        f"<NA> <NA> {speaker} <NA> <NA>\n"
                    )

            print(f"Saved RTTM → {output_rttm_path}")

        # Rename processed folder to mark as done
        new_subfolder_path = os.path.join(main_input_folder, subfolder + "_done")
        os.rename(subfolder_path, new_subfolder_path)
        print(f"Folder completed: {subfolder} → {subfolder}_done")


# ------------------------------------------------------------------
# Example usage
# ------------------------------------------------------------------
if __name__ == "__main__":
    main_input_folder = "inputfolder"    # Change to your main input directory
    main_output_folder = "outputfolder"  # Change to your main output directory

    diarize_folder(main_input_folder, main_output_folder)
