import os
import csv

# -----------------------------
# User settings
# -----------------------------
groundlabels_folder = "data/A1_68files/gt_10Oct"  # folder containing all _gt.txt files
mapping_csv = "data/A1_68files/session_mapping_py31.csv"                # CSV mapping sessions to speaker IDs
output_rttm_folder = "data/A1_68files/gt_rttm_py31"    # where RTTM files will be saved

os.makedirs(output_rttm_folder, exist_ok=True)

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
            "P2": f"SPEAKER_{row['P2']}",
            "ch2": f"SPEAKER_{row['ch2']}"

        }

# -----------------------------
# Conversion function
# -----------------------------
def txt_to_rttm(txt_file, rttm_file, speaker_map):
    #print(txt_file,rttm_file, speaker_map)
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
                speaker_id = speaker_map["ch"]      # main child
            elif label.lower() == "speaker_ch2":
                speaker_id = speaker_map["ch2"]     # new child
            elif label.lower() == "speaker_p1":
                speaker_id = speaker_map["P1"]
            elif label.lower() == "speaker_p2":
                speaker_id = speaker_map["P2"]
            else:
                print(f"Unknown label {label} in file {txt_file}, skipping line")
                continue

            audio_name = os.path.basename(rttm_file).replace("_gt.rttm", "")
            f_out.write(
                f"SPEAKER {audio_name} 1 {start_time:.2f} {duration:.2f} "
                f"<NA> <NA> {speaker_id} <NA> <NA>\n"
            )

# -----------------------------
# Batch processing of all _gt.txt in groundlabels_folder
# -----------------------------
txt_files = [f for f in os.listdir(groundlabels_folder) if f.endswith("_gt.txt")]

for txt_file in txt_files:
    txt_path = os.path.join(groundlabels_folder, txt_file)

    # Extract session from filename (assumes filename starts with session id)
    session_name = "_".join(txt_file.split("_")[:3])  # e.g., 'audio_10129759_2'
    #print(txt_file,mapping)
    if session_name not in mapping:
        print(f"No speaker mapping for session {session_name}, skipping {txt_file}...")
        continue

    rttm_filename = txt_file.replace("_gt.txt", "_gt.rttm")
    rttm_path = os.path.join(output_rttm_folder, rttm_filename)
    #print("oooo")
    txt_to_rttm(txt_path, rttm_path, mapping[session_name])
    print(f"Converted {txt_file} → {rttm_path}")
