#  **Guidelines for Manual Annotation for Speaker Diarization.**

Annotating medical dialogues, such as doctor-patient interactions, for
speaker diarization tasks requires manual annotation to accurately mark
speaker segments and assign correct labels. Given an audio file, one
must listen to the recording, identify start and end times of timestamps
of the speech segments, and assign speaker labels. This can be done
using a simple audio player or a specialized tool (e.g. Audacity is a
good open-source software for audio processing that comes with a marker
track feature that allows one to easily select and label audio segments
and then export markers as a CSV-like file).

## **Brief steps for manual speaker diarization annotation in Audacity:**

1.  **Load the Audio File into Audacity:**
    
    1.  Open Audacity.
    
    2.  Navigate to File \> Open and select your audio file (e.g.,
        filename.wav).

2.  **Add a Label Track:**
    
    3.  Go to Tracks \> Add New \> Label Track. This action adds an
        empty label track below your audio waveform.

3.  **Annotate Speech Segments:**
    
    4.  Click and drag on the waveform to select a segment corresponding
        to a single speaker's utterance.
    
    5.  Press Ctrl + B (or Cmd + B on Mac) to create a label at the
        selected region.

<!-- end list -->

  - In the label box that appears, enter the speaker's identifier/label

  - Repeat this process for each speech segment.

<!-- end list -->

4.  **Export Annotations:**
    
    1.  After completing the labeling, navigate to File \> Export \>
        Export Labels.
    
    2.  Save the labels as a text file (e.g., filename\_labels.txt).

This saves the annotation in .txt format with start times, end times,
and labels. To utilize these annotations in speaker diarization tasks,
we need to convert this information into the RTTM (Rich Transcription
Time Marked) format. The RTTM format looks like this:

<table>
<tbody>
<tr class="odd">
<td><p>SPEAKER my_audio 1 12.34 2.50 &lt;NA&gt; &lt;NA&gt; Speaker_A &lt;NA&gt; &lt;NA&gt;</p>
<p>SPEAKER my_audio 1 15.00 3.00 &lt;NA&gt; &lt;NA&gt; Speaker_B &lt;NA&gt; &lt;NA&gt;</p></td>
</tr>
</tbody>
</table>

There are various open-source toolkits for speaker diarization, many of
which leverage machine learning frameworks and provide state-of-the-art
pretrained models and pipelines. A basic **speaker diarization (SD)
system** consists of the following components:

1.  **Voice Activity Detection (VAD):** Identify & segment speech
    regions from non-speech.

2.  **Feature Extraction and Speaker Embedding:** Converts raw audio
    into meaningful representations of speakers' voices to distinguish
    between different speakers.

3.  **Clustering:** Groups similar speaker embeddings together to assign
    segments to unique speakers.

Fig. 1 Illustration of Speaker Diarization pipeline

While these models may perform well on some data, the performance
decreases if the test data differs significantly from the training data
(in terms of domain-specific challenges—such as overlapping speech,
noise, or varying speaker accents). Fine-tuning models on target data
can significantly improve diarization performance; however, this
requires annotated audio recordings. To reduce the effort of manual
annotation and streamline the process, we will automate parts of the
annotation pipeline.

To achieve this, we use an available open-source toolkit like ‘pyannote’
to generate initial speech segmentations and speaker labels. Since these
automatically generated annotations may not be fully accurate, we import
them into Audacity for manual correction. This allows us to refine both
segment boundaries and speaker labels where necessary. The advantage of
this approach is that it significantly reduces the time and effort
needed for full manual annotation while ensuring high-quality,
human-verified labels. By combining automatic diarization with
human-in-the-loop corrections, we create a more efficient annotation
workflow.

## **Steps for Using Pyannote for SD Annotation with Manual Correction in Audacity:**

1.  **Run Pyannote Diarization:**
    
    1.  Use **pyannote-audio** to process the audio and generate an
        **RTTM** file with speaker segments and labels.

Audacity does not support RTTM files, but we can convert RTTM to an
Audacity-compatible label file and then load it. Here’s how:

2.  **Convert RTTM to Audacity Label Format**

RTTM format looks like this:

<table>
<tbody>
<tr class="odd">
<td><p>SPEAKER my_audio 1 12.34 2.50 &lt;NA&gt; &lt;NA&gt; Speaker_A &lt;NA&gt; &lt;NA&gt;</p>
<p>SPEAKER my_audio 1 15.00 3.00 &lt;NA&gt; &lt;NA&gt; Speaker_B &lt;NA&gt; &lt;NA&gt;</p></td>
</tr>
</tbody>
</table>

Audacity’s label text format looks like this:

<table>
<tbody>
<tr class="odd">
<td><p>12.34 14.84 Speaker_A</p>
<p>15.00 18.00 Speaker_B</p></td>
</tr>
</tbody>
</table>

Use this **Python script** (rttm\_to\_audacity.py) to convert RTTM to
Audacity labels:

3.  **Load Audio in Audacity:**
    
    1.  Open the audio file in Audacity File \> Open and select your
        audio file (e.g., filename.wav).

4.  **Load the Labels in Audacity**

<!-- end list -->

  - Open Audacity and load your audio file.

  - Go to File → Import → Labels and select the ‘filename.txt’ file.

  - The speaker labels will appear in a **label track** under the
    waveform.

<!-- end list -->

5.  **Edit the Speaker Labels**

<!-- end list -->

  - Adjust timestamps and speaker names manually where needed.

  - Add or delete segments as needed.

<!-- end list -->

6.  **Export the Edited Labels**
    
    1.  Save the final annotations (File \> Export \> Export Labels).
    
    2.  Convert back to **RTTM format**

This hybrid approach ensures efficient yet accurate speaker diarization
annotations.

## **Guidelines: **

When using Pyannote-generated RTTM files (converted to Audacity format),
speech segments are pre-marked, and speakers are pre-tagged. However,
for our annotation of conversations between 5-year-old and SLP the
following changes need to be made:

**1. Identify & Adjust Speech Segments**

  - **Play and listen** to each pre-marked audio segment in Audacity.

  - **Verify start and end times:**
    
      - If a speaker starts or ends outside the given markers, adjust
        the segment boundaries to match the actual speech. Make sure
        that the speech segment starts and ends correctly.
    
      - If the boundary of the segment starts before the speaker, adjust
        when:
        
          - A non-speaking sound has been included (e.g. a door closing)
        
          - There is a silence longer than 0,5 seconds.
        
          - The segments overlap, but there is no overlapping speech
    
      - The same applies for a segment which continues after the speaker
        is finished.
    
      - Include the full noises the speaker makes to start and finish
        their words. Such as elongated s or k sounds. These are often
        audible in children's speech.
        
          - 
      - If adjusting the segment boundary, to include the elongated
        sound, makes the segment connect to the next segment of the same
        speaker, you can fuse the two segments into one segment.

> This image shows two segments of the slp. However in between (the
> light blue selection) the slp is still speaking. Thus you can fuse
> these segments, see image below.

  - 
**2. Tag Speech Segments**

  - **Speech Segment Duration**
    
      - For the segment duration and when to cut a segment. You should
        follow the tagged speech segments of Pyannote.
        
          - If Pyannote has cut the segment in the middle of a word. You
            can connect the segments until the next natural pause of the
            speaker.
        
          - Noises such as *shush,* *uh*, *uhuh*, *uhm* or *hmm*, are
            viewed as part of speech.
            
              - If these noises have been left out by Pyannote, connect
                them to the following segment or construct a separate
                segment. This depends on the pause in between the *uh*
                and speaking. You can connect when the pause is \<0,2
                seconds, approximately.
    
      - How to handle a pause of the same speaker:
        
          - Foremost follow the Pyannote segments
            
              - Make sure all speech is labelled.
            
              - If the pause is about \>0,5 seconds and the speaker
                starts the word again from the beginning, you can leave
                it as two segments if Pyannote has cut it.
            
              - 
              - This image shows the child is sounding out the word
                “geel”. But they are saying “ggg…” … “gggeeel”.
                Because they start the word again, you can leave it as
                two separate segments.
                
                  - However, you do not have to cut it if Pyannote
                    didn’t.

  - **Speaker Sounds**
    
      - What to do with speaker sounds, e.g. clacking with tongue,
        inhaling before speaking, coughing and laughing:
        
          - These are not included into the segment if it happens before
            or after the speech segment.
        
          - However, you do not have to cut it out of the segment if it
            happens while the speaker is speaking.
            
              - For example, you do not have to cut out a small giggle
                while speaking. Do cut out if the sentence ends in
                solely laughing. You can cut off the laughing part.
        
          - Do not make an overlapping segment when another speaker
            laughs/coughs during someone else’s speech
        
          - This also applies for any other random sounds a speaker
            makes.

<!-- end list -->

  - **Speaker Labels**
    
      - Pyannote **assigns generic speaker labels** (e.g., SPEAKER\_00,
        SPEAKER\_01), but these do not always match actual roles (i.e.,
        the 00 and 01 tag does not always correspond to the SLP or the
        child). Therefore, we need to know who spoke (for downstream
        tasks). Therefore, assign correct labels as follows:
        
          - **Child:** SPEAKER\_ch or SPEAKER\_ch2 (sometimes a sibling
            is present)
        
          - **SLP :** SPEAKER\_slp
        
          - **Parent:** SPEAKER\_P1 or SPEAKER\_P2 (depending on which
            parent is speaking, parent 1 or parent 2)

  - **Handling overlap Speech**
    
      - If another speaker **interrupts or overlaps** with the main
        speaker:
        
          - If Pyannote has marked the overlap, understand the
            structure.
        
          - If Pyannote did not, add new overlapping segments of the
            second speaker while keeping the main segment intact.
        
          - Ensure the overlap duration is correctly marked.
        
          - If the main speaker is overlapped by the second speaker and
            stops speaking until the second speaker is finished. Start a
            new segment for the main speaker when they start to speak
            again.
            
              - E.g. *slp* is speaking and *ch* overlaps them. You will
                have a SPEAKER\_slp segment which will be overlapped by
                a SPEAKER\_ch segment. Then *slp* will stay quiet until
                *ch* is finished. When the *slp* speaks again, and a new
                SPEAKER\_slp segment. See image below.
        
          - If the main speaker keeps talking while another speaker
            overlaps, mark it as one segment with an overlapping
            segment. Do not cut the segments of the main speaker.
        
          - 
**4. Record Additional Metadata**

  - Maintain an **Excel sheet** to log extra observations. The sheet can
    include:  
    Filename, which speaker starts first, 00 or 01 assignments, Comments
    (e.g., unusual audio conditions, unclear speech, annotation issues,
    etc.)
