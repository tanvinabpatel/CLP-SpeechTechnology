import os

def rttm_to_audacity(rttm_file, output_label_file):
    """Convert RTTM file to Audacity label format (start, end, speaker)."""
    with open(rttm_file, "r") as rttm, open(output_label_file, "w") as label:
        for line in rttm:
            parts = line.strip().split()
            # Ensure line is valid and of type SPEAKER
            if len(parts) < 8 or parts[0].upper() != "SPEAKER":
                continue
            start_time = float(parts[3])
            duration = float(parts[4])
            end_time = start_time + duration
            speaker = parts[7]
            label.write(f"{start_time:.2f}\t{end_time:.2f}\t{speaker}\n")


def process_rttm_files(main_output_folder):
    """Process all RTTM files and save Audacity labels in a single folder."""
    audacity_folder = os.path.join(main_output_folder, "audacitylabels")
    os.makedirs(audacity_folder, exist_ok=True)

    rttm_root = os.path.join(main_output_folder, "rttm_py31")

    for rttm_file in sorted(os.listdir(rttm_root)):
        if not rttm_file.lower().endswith("_py.rttm"):
            continue

        rttm_path = os.path.join(rttm_root, rttm_file)
        output_label_path = os.path.join(audacity_folder, rttm_file.replace("_py.rttm", "_py.txt"))

        rttm_to_audacity(rttm_path, output_label_path)
        print(f"Saved Audacity labels → {output_label_path}")


# ------------------------------------------------------------------
# Example usage
# ------------------------------------------------------------------
if __name__ == "__main__":
    main_output_folder = "outputfolder"  # Your diarization output directory
    process_rttm_files(main_output_folder)