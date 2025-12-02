#!/usr/bin/env python3
"""
standard_diarization_eval.py

Compute standard diarization metrics (DER + confusion matrix) across multiple sessions using pyannote.
Saves summary tables and plots (bar chart of DER per session, confusion-matrix heatmap per session).
"""

import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pyannote.metrics.diarization import DiarizationErrorRate
from pyannote.database.util import load_rttm

# ------------------------------
# CONFIG — Edit these
# ------------------------------

GT_RTTM_DIR = "/home/tanvina/Documents/Erasmus-TUD/UNISPEECH-CLP/data/A1_68files/gt_rttm_py31"                    # folder containing *_gt.rttm
HYP_RTTM_DIR = "/home/tanvina/Documents/Erasmus-TUD/UNISPEECH-CLP/data/A1_68files/rttm_py31"                    # folder containing *_py.rttm

OUTPUT_DIR = "pyannote_results"
COLLAR = 0.0
FIGSIZE_DER = (10, 6)
FIGSIZE_CM = (8, 6)

os.makedirs(OUTPUT_DIR, exist_ok=True)


# ----------------------
# HELPERS
# ----------------------
def load_annotation(rttm_path):
    annos = load_rttm(rttm_path)
    if not annos:
        raise FileNotFoundError(f"No annotation found in {rttm_path}")
    return list(annos.values())[0]

def evaluate_session(session_id, gt_dir, hyp_dir, collar=0.0):
    """Compute DER only (v3.2.1)"""
    gt_path = os.path.join(gt_dir, f"{session_id}_gt.rttm")
    hyp_path = os.path.join(hyp_dir, f"{session_id}_py.rttm")
    ref = load_annotation(gt_path)
    hyp = load_annotation(hyp_path)
    der_metric = DiarizationErrorRate(collar=collar)
    der = der_metric(ref, hyp)
    return {"session": session_id, "DER": der}

def build_confusion_matrix(ref, hyp):
    """Per-speaker confusion matrix (seconds of overlap)"""
    ref_spks = sorted(ref.labels())
    hyp_spks = sorted(hyp.labels())
    mat = pd.DataFrame(0.0, index=ref_spks, columns=hyp_spks)

    for r in ref_spks:
        for rseg in ref.label_timeline(r):  # Timeline is iterable directly
            overlapping = hyp.crop(rseg, mode="intersection")
            for h in overlapping.labels():
                for hseg in overlapping.label_timeline(h):
                    overlap_time = max(0.0, min(rseg.end, hseg.end) - max(rseg.start, hseg.start))
                    mat.at[r, h] += overlap_time
    return mat

def plot_der_summary(df_summary, savepath=None):
    plt.figure(figsize=FIGSIZE_DER)
    sns.barplot(data=df_summary, x="session", y="DER")
    plt.xticks(rotation=45, ha="right")
    plt.ylabel("DER")
    plt.title("Diarization Error Rate per session")
    plt.tight_layout()
    if savepath:
        plt.savefig(savepath)
    plt.show()

def plot_confusion_heatmap(confusion_df, session_id, savepath=None):
    plt.figure(figsize=FIGSIZE_CM)
    sns.heatmap(confusion_df, annot=True, fmt=".2f", cmap="Reds")
    plt.xlabel("Hypothesis speaker")
    plt.ylabel("Reference speaker")
    plt.title(f"Speaker Confusion Matrix — {session_id}")
    plt.tight_layout()
    if savepath:
        plt.savefig(savepath)
    plt.show()

# ----------------------
# MAIN
# ----------------------
def main():
    gt_files = [f for f in os.listdir(GT_RTTM_DIR) if f.endswith("_gt.rttm")]
    session_ids = [f.replace("_gt.rttm", "") for f in gt_files]

    results = []
    all_confusion = {}

    for sid in session_ids:
        try:
            res = evaluate_session(sid, GT_RTTM_DIR, HYP_RTTM_DIR, COLLAR)
        except Exception as e:
            print(f"Skipping {sid} due to error: {e}")
            continue

        results.append(res)

        # build confusion matrix
        ref = load_annotation(os.path.join(GT_RTTM_DIR, f"{sid}_gt.rttm"))
        hyp = load_annotation(os.path.join(HYP_RTTM_DIR, f"{sid}_py.rttm"))
        cm = build_confusion_matrix(ref, hyp)
        all_confusion[sid] = cm

        # plot/save per-session confusion
        #plot_confusion_heatmap(cm, sid, savepath=os.path.join(OUTPUT_DIR, f"{sid}_confusion.png"))

    # Save DER summary
    df_summary = pd.DataFrame(results)
    df_summary.to_csv(os.path.join(OUTPUT_DIR, "all_sessions_summary.csv"), index=False)
    plot_der_summary(df_summary, savepath=os.path.join(OUTPUT_DIR, "der_summary.png"))

    # Print average DER
    print("Average DER:", df_summary["DER"].mean())

    # Save all confusion matrices in Excel
    with pd.ExcelWriter(os.path.join(OUTPUT_DIR, "speaker_confusions_all_sessions.xlsx")) as writer:
        for sid, df_cm in all_confusion.items():
            sheet = sid[:31]
            df_cm.to_excel(writer, sheet_name=sheet)

    print("Evaluation complete. Results saved to", OUTPUT_DIR)

if __name__ == "__main__":
    main()