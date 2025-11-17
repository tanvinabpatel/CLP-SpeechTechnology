import os
import csv

# -----------------------------
# User settings
# -----------------------------
input_folder = "/path/inputfolder"  # contains session subfolders
mapping_csv = "/path/speaker_mapping.csv"

# -----------------------------
# Load mapping CSV
# -----------------------------
mapping = {}
with open(mapping_csv, "r") as f:
    reader = csv.DictReader(f)
    for row in reader:
        session = row["session_id"]
        mapping[session] = {
            "slp": f"SPEAKER_{row['slp']}",
            "ch": f"SPEAKER_{row['ch']}",
            "P1": f"SPEAKER_{row['P1']}",
            "P2": f"SPEAKER_{row['P2']}"
        }



# -----------------------------
# Conversion function
# -----------------------------
def txt_to_rttm(txt_file, rttm_file, speaker_map):
    """Convert a single Audacity GT TXT file to RTTM using speaker_map."""
    with open(txt_file, "r") as f_in, open(rttm_file, "w") as f_out:
        for line in f_in:
            line = line.strip()
            if not line or line.startswith("<"):
                continue

            parts = line.split()
            if len(parts) < 3:
                print(f"Skipping malformed line: {line}")
                continue

            start_time = float(parts[0])
            end_time = float(parts[1])
            duration = end_time - start_time
            label = parts[2]

            # Map human label to RTTM numeric ID
            if label.lower() == "speaker_slp":
                speaker_id = speaker_map["slp"]
            elif label.lower() == "speaker_ch":
                speaker_id = speaker_map["ch"]
            elif label.lower() == "speaker_p1":
                speaker_id = speaker_map["P1"]
            elif label.lower() == "speaker_p2":
                speaker_id = speaker_map["P2"]
            else:
                print(f"Unknown label {label} in file {txt_file}, skipping line")
                continue

            audio_name = os.path.basename(rttm_file).replace("_gt.rttm", "")
            f_out.write(
                f"SPEAKER audio_{audio_name} 1 {start_time:.2f} {duration:.2f} "
                f"<NA> <NA> {speaker_id} <NA> <NA>\n"
            )

# -----------------------------
# Batch processing in session folders
# -----------------------------
session_folders = [f for f in os.listdir(input_folder) if os.path.isdir(os.path.join(input_folder, f))]

for session in session_folders:
    session_path = os.path.join(input_folder, session)
    if session not in mapping:
        print(f"No speaker mapping for session {session}, skipping...")
        continue

    txt_files = [f for f in os.listdir(session_path) if f.endswith("_gt.txt")]
    if not txt_files:
        print(f"No _gt.txt files in {session}, skipping...")
        continue

    for txt_file in txt_files:
        txt_path = os.path.join(session_path, txt_file)
        rttm_path = os.path.join(session_path, txt_file.replace("_gt.txt", "_gt.rttm"))

        txt_to_rttm(txt_path, rttm_path, mapping[session])
        print(f"Converted {txt_file} → {os.path.basename(rttm_path)}")
