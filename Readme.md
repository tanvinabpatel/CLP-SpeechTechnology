# CLP Speech Technology

This project supports research on automatic velopharyngeal competence (VPC) classification from Dutch clinical recordings of children with cleft lip and/or palate.

This repository provides:

1) a protocol with guidelines for manually annotating the clinical recordings, i.e., marking speech segments, assigning speaker labels and handling overlapping speech, to extract the child's speech;

2) a semi-automatic speaker-annotation pipeline based on Pyannote speaker diarization: recordings are diarized, the resulting RTTM output is converted into Audacity label tracks, and annotators manually correct segment boundaries and speaker labels.

The corrected annotations are used to extract the child's speech for VPC classification.

## Repository contents

- `protocol/` — the [manual annotation guidelines PDF](protocol/SpeakerDiarization%20Annotation%20Guidelines.pdf), the [Markdown guide](protocol/ANNOTATION_GUIDELINES.md), and supporting figures
- `annotations/` — annotation scripts and Pyannote-to-Audacity conversion utilities

## Annotation pipeline

1. Convert the audio recordings to mono and resample them to 16 kHz (required by Pyannote).
2. Run Pyannote speaker diarization (version 3.1) on the recordings.
3. Convert the generated `_py.rttm` files into Audacity label text files.
4. Import the label tracks into Audacity and correct segment boundaries and speaker labels following the annotation guidelines in protocol/.
5. Save the reviewed result as `_gt.txt`.
6. Convert the corrected `_gt.txt` files into `_gt.rttm` format for evaluation.

## Requirements

- Python 3.10
- `pyannote.audio` 3.1
- Dependencies listed in [`requirements.txt`](requirements.txt)

Install the dependencies with:

```bash
python -m pip install -r requirements.txt
```

Pyannote model access also requires a Hugging Face account, acceptance of the relevant model terms, and an access token.

## Clinical data

No clinical recordings or clinical annotations are included in this repository. Session and participant mappings should remain outside the public repository.

## License

This project is licensed under the MIT License (see LICENSE).

