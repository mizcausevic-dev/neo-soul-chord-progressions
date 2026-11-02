"""Factual article draft. Not published."""

from __future__ import annotations

from tools.statements import AUDITION, ON_PICTURE, PREVIEW_LINE, PROGRAM, PUBLICATION, WARNING

TITLE = "Neo-Soul Chord Progressions is a note-only MIDI study pack"
SUBTITLE = "Eight studies of extensions and suspensions, a matched byte check, and a simple-synth preview that is not a master"
TAGS = ["midi", "neo-soul", "chords", "music-production", "composition"]
TAG_LINE = "Tags: " + ", ".join(TAGS)

PARAGRAPHS = [
    "DRAFT. " + PUBLICATION,
    TAG_LINE,
    "The pack is eight chord studies in 4/4. Tempos sit between 65 and 100 BPM. Every study is 8 bars, chosen before the notes. Each study has a chord progression with two variations. That is the core: sixteen files. Each study also has two bass guides. Those sixteen files are reference parts. They are not merged into the chord files and they are not part of the core count.",
    "A variation has to change the phrase. Holding the same voicing and only editing velocity does not count. Suspended Step moves Cmaj9, Dm11, G13sus, and Cmaj7 by step, and variation B flips the inversions. Minor Nine stays in A natural minor for a bar each, then variation B inserts one chromatic cluster. Gospel Plate holds an Fmaj9 plate, and variation B breaks it into suspensions. Dim Approach puts D#dim7 and A13 inside the declared set and anticipates each chord in variation B. Shells are thirds and sevenths with a rest, and variation B fills the bar. Flat Cycle sits on beat 2, and variation B replaces Ab with a flagged A major approach for one quarter. Unresolved ends on Amaj9 and never returns to B. Open Hands uses tenths, then closes them.",
    "Chord tones stay between MIDI 48 and 84, with at most four notes sounding. Bass guides stay between 28 and 55 and are monophonic. C4 is 60. The resolution is 960 ticks per quarter note. There is no microtiming offset. Roots are often omitted from the chord file because the bass guide has them. The voicing and the hand split are written on each study.",
    PROGRAM,
    "Rhodes settings, pedal, and slides are not in the files. The preview synth uses a sine plus a quiet triangle for the chords and a sine for the bass guide. That mapping is documented. It is not a program change.",
    "The primary preview is study 01, Suspended Step, variation A, for all 8 bars: the chord file and bass guide A together. The other studies are in the MIDI and are not in that audio file. "
    + PREVIEW_LINE
    + ". The film takes its audio from that preview file and shows the words "
    + ON_PICTURE
    + " on the picture and in the WebVTT captions.",
    AUDITION
    + " The validator reopened the MIDI bytes and compared them with the canonical score. That is a structural check. The sample peak written beside the preview is the peak of the integer mix. It is not LUFS and it is not a true-peak reading. Nothing in this build is claimed as a master.",
    "The stills are procedural illustrations of vertical note stacks on a walnut field, with a separate bass row. They are not photographs of a session or of performers.",
    "When a public URL exists, use either the combined arrangement or the separate parts. " + WARNING,
    "Call to action: the MIDI, the matched report, and the preview belong together. Do not publish this draft to Medium, Instagram, or X from the draft files alone.",
]


def markdown() -> str:
    body = "\n\n".join(PARAGRAPHS)
    return f"# {TITLE}\n\n{SUBTITLE}\n\n{body}\n"


def plain_text() -> str:
    lines = [TITLE, "", SUBTITLE, "", *PARAGRAPHS, ""]
    return "\n".join(lines) + "\n"
