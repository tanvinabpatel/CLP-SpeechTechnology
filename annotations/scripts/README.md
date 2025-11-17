# Annotations Pipeline

This folder contains scripts and workflow for speaker diarization annotation.

## Step 1 – Auto Diarization
- Script: `run_pyannote_diarization.py`
- Input: WAV files in session subfolders
- Output: 16kHz WAV + `_py.rttm` files
- Purpose: Convert audio and run pyannote speaker diarization
- **Usage:**
```bash
python run_pyannote_diarization.py
```

## Step 2 – Convert to Audacity Labels
- Script: rttm_to_audacity.py
- Input: _py.rttm
- Output: _py.txt for Audacity
- Purpose: Prepare auto-diarization labels for manual correction
- **Usage:**

```
python rttm_to_audacity.py
```

## Step 3 – Manual Annotation
- Human annotators open _py.txt in Audacity
- Correct labels following guidelines
- Save corrected file as _gt.txt in the same folder

-Verification stage pending

## Step 4 – Convert Manual Annotations to RTTM
- Script: `convert_gt_txt_to_rttm.py`
- Input: `_gt.txt` files in each session folder
- Output: `_gt.rttm` in the same session folder
- Purpose: Convert human-corrected Audacity labels to RTTM format, mapping speakers to numeric IDs
- Notes: Use `speaker_mapping.csv` to define session-specific speaker-to-ID assignments
- **Usage:**
```bash
python convert_gt_txt_to_rttm_inplace.py
```