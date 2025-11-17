import os
import json
import pandas as pd
from collections import defaultdict
from pyannote.metrics.diarization import DiarizationErrorRate
from pyannote.database.util import load_rttm
import seaborn as sns
import matplotlib.pyplot as plt

# --- CONFIG ---
base_dir = "/home/tanvina/Documents/Erasmus-TUD/Interns/Nina/Test_UNIspeech_orig"          # Folder containing session subfolders
mapping_path = "session_mapping.csv"      # Your mapping file
output_dir = "results_diarization"
collar = 0.0

os.makedirs(output_dir, exist_ok=True)

## --- LOAD SPEAKER MAPPING ---
map_df = pd.read_csv(mapping_path, dtype=str)  # read all as strings

# Convert CSV to {session_id: {pyannote_speaker_id: role}}
session_mappings = {}
for _, row in map_df.iterrows():
    session_id = row["session_id"].strip()  # remove spaces
    mapping = {}
    for role in ["slp", "ch", "P1", "P2"]:
        val = str(row[role]).strip()  # ensure string and remove spaces
        if val and val.lower() != "nan":
            mapping[f"SPEAKER_{val.zfill(2)}"] = role  # pad to 2 digits
    session_mappings[session_id] = mapping

# --- Helper to map pyannote speaker IDs to human-readable labels ---
def map_speaker(pyn_id, mapping):
    """
    pyn_id: string like 'SPEAKER_00', 'SPEAKER_01'
    mapping: dict { 'SPEAKER_00':'slp', 'SPEAKER_01':'ch', ... }
    """
    return mapping.get(pyn_id, "UNK")  # extra speakers -> UNK

# === COMPUTE DETAILED METRICS ===
def compute_detailed_metrics(ref, hyp, collar=0.0):
    der_metric = DiarizationErrorRate(collar=collar)
    der_value = der_metric(ref, hyp)

    miss, fa = defaultdict(float), defaultdict(float)
    confusion = defaultdict(lambda: defaultdict(float))

    ref_speakers = ref.labels()
    hyp_speakers = hyp.labels()

    # MISS
    for spk in ref_speakers:
        for seg in ref.label_timeline(spk):
            hyp_overlap = hyp.crop(seg, mode="intersection")
            overlap = sum(s.duration for s in hyp_overlap.itersegments())
            miss[spk] += seg.duration - overlap

    # FA
    for spk in hyp_speakers:
        for seg in hyp.label_timeline(spk):
            ref_overlap = ref.crop(seg, mode="intersection")
            overlap = sum(s.duration for s in ref_overlap.itersegments())
            fa[spk] += seg.duration - overlap

    # CONFUSION
    for r_spk in ref_speakers:
        for h_spk in hyp_speakers:
            overlap = 0.0
            for rseg in ref.label_timeline(r_spk):
                for hseg in hyp.label_timeline(h_spk):
                    start, end = max(rseg.start, hseg.start), min(rseg.end, hseg.end)
                    if start < end:
                        overlap += end - start
            confusion[r_spk][h_spk] += overlap

    all_conf = [v for d in confusion.values() for v in d.values()]
    avg_confusion = sum(all_conf) / len(all_conf) if all_conf else 0.0

    return {
        "DER": der_value,
        "MISS_total": sum(miss.values()),
        "FA_total": sum(fa.values()),
        "MISS_detail": miss,
        "FA_detail": fa,
        "CONFUSION_avg": avg_confusion,
        "CONFUSION_detail": confusion
    }

# === MAIN LOOP ===
rows_summary, confusion_rows, missfa_rows = [], [], []
aggregate_confusion = defaultdict(lambda: defaultdict(float))

for session in sorted(os.listdir(base_dir)):
    session_path = os.path.join(base_dir, session)
    if not os.path.isdir(session_path):
        continue

    gt_rttm = [f for f in os.listdir(session_path) if f.endswith("_gt.rttm")]
    py_rttm = [f for f in os.listdir(session_path) if f.endswith("_py.rttm")]
    if not gt_rttm or not py_rttm:
        continue

    ref = list(load_rttm(os.path.join(session_path, gt_rttm[0])).values())[0]
    hyp = list(load_rttm(os.path.join(session_path, py_rttm[0])).values())[0]

    metrics = compute_detailed_metrics(ref, hyp, collar=collar)
    mapping = session_mappings.get(session, {})

    # --- DEBUG PRINTS ---
    print(f"\n--- SESSION: {session} ---")
    print("Ref speakers from RTTM:", ref.labels())
    print("Hyp speakers from RTTM:", hyp.labels())
    print("Mapping dict:", mapping)
    for spk in ref.labels() + hyp.labels():
        print(f"Mapping {spk} -> {map_speaker(spk, mapping)}")

    # --- Remap dictionaries to human-readable labels ---
    def remap_dict(d):
        return {map_speaker(k, mapping): v for k, v in d.items()}

    def remap_nested_dict(d):
        return {
            map_speaker(k, mapping): {map_speaker(kk, mapping): vv for kk, vv in inner.items()}
            for k, inner in d.items()
        }

    metrics["MISS_detail"] = remap_dict(metrics["MISS_detail"])
    metrics["FA_detail"] = remap_dict(metrics["FA_detail"])
    metrics["CONFUSION_detail"] = remap_nested_dict(metrics["CONFUSION_detail"])

    # --- Session summary ---
    rows_summary.append({
        "session": session,
        "DER": round(metrics["DER"], 4),
        "MISS_total": round(metrics["MISS_total"], 2),
        "FA_total": round(metrics["FA_total"], 2),
        "CONFUSION_avg": round(metrics["CONFUSION_avg"], 2)
    })

    # --- Detailed confusion per session ---
    for ref_spk, hyp_dict in metrics["CONFUSION_detail"].items():
        for hyp_spk, dur in hyp_dict.items():
            confusion_rows.append({
                "session": session,
                "ref_speaker": ref_spk,
                "hyp_speaker": hyp_spk,
                "overlap_duration": round(dur, 3)
            })
            aggregate_confusion[ref_spk][hyp_spk] += dur

    # --- MISS / FA per speaker ---
    for spk, val in metrics["MISS_detail"].items():
        missfa_rows.append({
            "session": session,
            "speaker": spk,
            "metric": "MISS",
            "duration": round(val, 3)
        })
    for spk, val in metrics["FA_detail"].items():
        missfa_rows.append({
            "session": session,
            "speaker": spk,
            "metric": "FA",
            "duration": round(val, 3)
        })

# --- Convert to DataFrames ---
df_summary = pd.DataFrame(rows_summary)
df_conf = pd.DataFrame(confusion_rows)
df_missfa = pd.DataFrame(missfa_rows)
agg_df = pd.DataFrame(aggregate_confusion).fillna(0).round(2)

# --- Save paths ---
summary_tsv = os.path.join(output_dir, "session_metrics_summary.tsv")
conf_tsv = os.path.join(output_dir, "session_confusion_detailed.tsv")
missfa_tsv = os.path.join(output_dir, "session_miss_fa_detailed.tsv")
agg_tsv = os.path.join(output_dir, "speaker_confusion_aggregate.tsv")
excel_path = os.path.join(output_dir, "all_metrics.xlsx")

# --- Save TSV ---
df_summary.to_csv(summary_tsv, sep="\t", index=False)
df_conf.to_csv(conf_tsv, sep="\t", index=False)
df_missfa.to_csv(missfa_tsv, sep="\t", index=False)
agg_df.to_csv(agg_tsv, sep="\t")

# --- Save Excel ---
with pd.ExcelWriter(excel_path) as writer:
    df_summary.to_excel(writer, sheet_name="Session Summary", index=False)
    df_conf.to_excel(writer, sheet_name="Confusion Details", index=False)
    df_missfa.to_excel(writer, sheet_name="Miss_FA Details", index=False)
    agg_df.to_excel(writer, sheet_name="Speaker Confusion", index=True)

print("✅ Saved all detailed results inside 'results_diarization/'")
print(f"   - {summary_tsv}")
print(f"   - {conf_tsv}")
print(f"   - {missfa_tsv}")
print(f"   - {agg_tsv}")
print(f"   - Excel summary: {excel_path}")
print(f"\n📊 Average DER across sessions: {df_summary['DER'].mean():.4f}")

# --- Compute per-speaker accuracy and child confusion ---
# Load aggregate confusion from existing Excel
agg_df = pd.read_excel("results_diarization/all_metrics.xlsx", sheet_name="Speaker Confusion", index_col=0)

# --- 1. Per-speaker accuracy ---
per_speaker_accuracy = {spk: agg_df.loc[spk, spk]/agg_df.loc[spk].sum() for spk in agg_df.index}
accuracy_df = pd.DataFrame(list(per_speaker_accuracy.items()), columns=["speaker", "accuracy"])
accuracy_df["accuracy_percent"] = (accuracy_df["accuracy"] * 100).round(2)

# --- 2. Child confusion rate ---
if "ch" in agg_df.index:
    child_row = agg_df.loc["ch"]
    child_total = child_row.sum()
    child_offdiag = child_total - child_row.get("ch", 0)
    child_conf_rate = child_offdiag / child_total if child_total>0 else None
else:
    child_conf_rate = None
child_conf_df = pd.DataFrame([{"Child Confusion Rate (%)": child_conf_rate*100 if child_conf_rate is not None else None}])

# --- Append sheets to existing workbook ---
with pd.ExcelWriter("results_diarization/all_metrics.xlsx", mode="a", engine="openpyxl") as writer:
    accuracy_df.to_excel(writer, sheet_name="Per-Speaker Accuracy", index=False)
    child_conf_df.to_excel(writer, sheet_name="Child Confusion Rate", index=False)

print("✅ Added Per-Speaker Accuracy and Child Confusion Rate to all_metrics.xlsx")

"""
% --- Per-Speaker Accuracy ---
\begin{equation}
\text{Accuracy}_s = \frac{D_{s \to s}}{\sum_{t \in \text{Speakers}} D_{s \to t}}
\end{equation}
where $D_{s \to s}$ is the duration of reference speaker $s$ correctly labeled, and $\sum_{t} D_{s \to t}$ is the total reference speech duration for speaker $s$.

% --- Speaker Confusion Rate ---
\begin{equation}
\text{ConfusionRate}_s = \frac{\sum_{t \neq s} D_{s \to t}}{\sum_{t} D_{s \to t}}
\end{equation}
This is the fraction of reference speech from speaker $s$ misattributed to other speakers. For the child speaker, this is the Child Confusion Rate (CCR).

% --- Diarization Error Rate (DER) ---
\begin{equation}
\text{DER} = \frac{\text{FA} + \text{MISS} + \text{CONF}}{\text{Total reference speech duration}}
\end{equation}
where FA = false alarm duration, MISS = missed speech duration, CONF = confusion duration.

\begin{equation}
\text{CONF} = \sum_{s} \sum_{t \neq s} D_{s \to t}
\end{equation}

% --- Percentage Confusion Matrix ---
\begin{equation}
C_{s,t} (\%) = \frac{D_{s \to t}}{\sum_{t} D_{s \to t}} \times 100
\end{equation}
Each row sums to 100\%; diagonal = accuracy, off-diagonal = misattribution.

5. Reference for papers

Anguera, Xavier, et al. "Speaker diarization: A review of recent research." IEEE Transactions on Audio, Speech, and Language Processing 20.2 (2012): 356-370.
Pyannote.metrics library for evaluation: https://pyannote.github.io/pyannote-metrics/

"""