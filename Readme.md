# CLP Speech Technology

This repository supports research on automatic velopharyngeal competence (VPC) classification from clinical recordings of children with cleft lip and/or palate. It provides a semi-automatic speaker-annotation pipeline based on Pyannote speaker diarization: recordings are diarized, the resulting RTTM output is converted into Audacity label tracks, and annotators manually correct segment boundaries and speaker labels. Paper: [link to follow]

## Annotation pipeline

1. Run Pyannote speaker diarization on clinical recordings.
2. Convert the generated `_py.rttm` files into Audacity label text files.
3. Import the label tracks into Audacity, correct segment boundaries and speaker labels, and save the reviewed result as `_gt.txt`.
4. Convert the corrected `_gt.txt` files into `_gt.rttm` format for evaluation.

## Repository contents

- `annotations/` — annotation scripts and Pyannote-to-Audacity conversion utilities
- `protocol/` — the [manual annotation guidelines PDF](protocol/SpeakerDiarization%20Annotation%20Guidelines.pdf), the [Markdown guide](protocol/ANNOTATION_GUIDELINES.md), and supporting figures

## Requirements

The tools in `annotations/` require a Python environment and the scientific/audio packages used by the scripts. Pyannote model access also requires a Hugging Face account, acceptance of the relevant model terms, and an access token.

Run Python scripts from the repository as needed, using placeholder paths for local datasets and outputs:

```bash
python annotations/scripts/run_pyannote_diarization.py
python annotations/scripts/rttm_to_audacity.py
python annotations/scripts/convert_gt_txt_to_gt_rttm.py
```

Additional package installation and script-specific instructions are provided in [`annotations/scripts/README.md`](annotations/scripts/README.md).

## Annotation protocol

Use the following speaker labels:

- `SPEAKER_ch` — primary child participant
- `SPEAKER_ch2` — additional child participant
- `SPEAKER_slp` — speech-language pathologist
- `SPEAKER_P1` — first additional participant
- `SPEAKER_P2` — second additional participant

Overlapping speech should remain represented by overlapping label intervals, rather than merging multiple speakers into one label. Annotators should refine boundaries to the approximate onset and offset of each speaker's speech and complete a review pass for uncertain boundaries and speaker assignments.

## Clinical data

No clinical recordings or clinical annotations are included in this repository. Session and participant mappings should remain outside the public repository.

## Citation

Placeholder citation — to be added after publication:

```text
[Authors]. Automatic velopharyngeal competence classification from clinical
recordings of children with cleft lip and/or palate. [Venue], [Year].
```

## License

License details have not yet been specified. A `LICENSE` file and confirmed institutional terms should be added before public distribution.

