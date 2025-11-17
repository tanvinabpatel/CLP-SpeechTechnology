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
    wav16_root = os.path.join(main_output_folder, "wav_16k")
    rttm_root = os.path.join(main_output_folder, "rttm_py31")

    os.makedirs(wav16_root, exist_ok=True)
    os.makedirs(rttm_root, exist_ok=True)

    for folder in sorted(os.listdir(main_input_folder)):
        folder_path = os.path.join(main_input_folder, folder)

        if not os.path.isdir(folder_path):
            continue

        wav_files = [f for f in os.listdir(folder_path) if f.lower().endswith(".wav")]
        if not wav_files:
            continue

        print(f"\n=== Processing folder: {folder} ===")

        for wav_file in wav_files:
            inp = os.path.join(folder_path, wav_file)

            # Make unified output filenames
            base_name = f"{folder}_{wav_file.replace('.wav', '')}"

            out_wav_16k = os.path.join(wav16_root, base_name + "_16k.wav")
            out_rttm = os.path.join(rttm_root, base_name + "_py.rttm")

            print(f"→ Converting {wav_file} → 16kHz")
            process_audio(inp, out_wav_16k)

            print(f"→ Running diarization on {wav_file}")
            with ProgressHook() as hook:
                diarization = pipeline(out_wav_16k, hook=hook)

            with open(out_rttm, "w") as f:
                for turn, _, speaker in diarization.itertracks(yield_label=True):
                    f.write(
                        f"SPEAKER {base_name} 1 {turn.start:.2f} {turn.duration:.2f} "
                        f"<NA> <NA> {speaker} <NA> <NA>\n"
                    )

            print(f"Saved RTTM → {out_rttm}")

        # Rename processed folder to mark as done
        new_subfolder_path = os.path.join(main_input_folder, folder + "_done")
        os.rename(folder_path, new_subfolder_path)
        print(f"Folder completed: {folder} → {folder}_done")


# ------------------------------------------------------------------
# Example usage
# ------------------------------------------------------------------
if __name__ == "__main__":
    main_input_folder = "inputfolder"    # Change to your main input directory
    main_output_folder = "outputfolder"  # Change to your main output directory

    diarize_folder(main_input_folder, main_output_folder)
