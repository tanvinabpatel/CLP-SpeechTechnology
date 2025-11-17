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
    """Process all RTTM files in subfolders and create .txt label files for Audacity."""
    for subfolder in sorted(os.listdir(main_output_folder)):
        subfolder_path = os.path.join(main_output_folder, subfolder)

        if not os.path.isdir(subfolder_path):
            continue

        print(f"\n=== Processing folder: {subfolder} ===")

        # Find .rttm files
        rttm_files = [f for f in os.listdir(subfolder_path) if f.lower().endswith("_py.rttm")]
        if not rttm_files:
            print(f"No RTTM files found in {subfolder}, skipping...")
            continue

        for rttm_file in rttm_files:
            rttm_path = os.path.join(subfolder_path, rttm_file)
            output_label_path = os.path.join(subfolder_path, rttm_file.replace("_py.rttm", "_py.txt"))

            rttm_to_audacity(rttm_path, output_label_path)
            print(f"Saved: {output_label_path}")


# ------------------------------------------------------------------
# Example usage
# ------------------------------------------------------------------
if __name__ == "__main__":
    main_output_folder = "outputfolder"  # Change to your diarization output directory
    process_rttm_files(main_output_folder)
