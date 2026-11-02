"""Original neo-soul progressions.

Tempos, lengths, and collections are fixed before the notes. Chord files hold
the upper voices only. Bass guides are separate and are not core. Offsets are 0.
Roots are often omitted from the chord file when the bass guide has them.
"""

from __future__ import annotations

from tools.midi_io import BAR_TICKS_4_4, PPQ, bpm_to_us, effective_bpm

GENERATOR_VERSION = "1.0.0"
PACK_ID = "neo-soul-chord-progressions"
PACK_NAME = "Neo-Soul Chord Progressions"
BAR = BAR_TICKS_4_4


class Part:
    def __init__(self, study, part_id, role, variation, core, channel, slug, mono, poly, lo, hi):
        self.study = study
        self.part_id = part_id
        self.role = role
        self.variation = variation
        self.core = core
        self.channel = channel
        self.file_slug = slug
        self.monophonic = mono
        self.max_poly = poly
        self.lo = lo
        self.hi = hi
        self.container_ticks = study["bars"] * BAR
        self.notes = []

    def add(self, start, duration, pitch, velocity, departure=False):
        end = start + duration
        if start < 0 or duration <= 0 or end > self.container_ticks:
            raise ValueError(f"{self.part_id} boundary {start}+{duration}")
        if not self.lo <= pitch <= self.hi:
            raise ValueError(f"{self.part_id} pitch {pitch}")
        active = 1
        for other in self.notes:
            o0 = other["performed_start"]
            o1 = o0 + other["duration"]
            if start < o1 and o0 < end:
                if other["pitch"] == pitch or self.monophonic:
                    raise ValueError(f"{self.part_id} overlap {pitch}@{start}")
                active += 1
        if active > self.max_poly:
            raise ValueError(f"{self.part_id} poly {active}")
        self.notes.append({
            "nominal_start": start, "offset": 0, "performed_start": start,
            "duration": duration, "pitch": pitch, "velocity": velocity,
            "channel": self.channel, "departure": departure,
        })

    def finish(self):
        ordered = sorted(self.notes, key=lambda n: (n["performed_start"], n["pitch"]))
        if self.core and len(ordered) < 8:
            raise ValueError(f"{self.part_id} too few notes")
        if not ordered:
            raise ValueError(f"{self.part_id} empty")
        for i, note in enumerate(ordered, 1):
            note["id"] = f"{self.part_id}.n{i:04d}"
        return {
            "id": self.part_id, "study_id": self.study["id"], "slug": self.study["slug"],
            "role": self.role, "variation": self.variation, "core": self.core,
            "channel": self.channel, "file_slug": self.file_slug,
            "path": f"midi/{self.study['slug']}/{self.file_slug}.mid",
            "monophonic": self.monophonic, "max_poly": self.max_poly,
            "container_ticks": self.container_ticks, "container_bars": self.study["bars"],
            "bpm": self.study["bpm"], "tempo_us": self.study["tempo_us"], "notes": ordered,
        }


def chords(study, variation):
    return Part(study, f"{study['id']}.chords.{variation}", "chord-progression", variation, True, 0, f"chords-{variation}", False, 4, 48, 84)


def bass(study, variation):
    return Part(study, f"{study['id']}.bass.{variation}", "bass-guide", variation, False, 1, f"bass-guide-{variation}", True, 1, 28, 55)


def bar(n, beats=0):
    return n * BAR + beats * PPQ


def lay(part, events):
    for start, dur, pitches, vel, departure in events:
        if isinstance(pitches, int):
            pitches = [pitches]
        for pitch in pitches:
            part.add(start, dur, pitch, vel, departure=departure)


def studies():
    rows = [
        {"id": "s01", "slug": "s01-suspended-step", "title": "Suspended Step", "bpm": 76, "bars": 8,
         "tonic": "C", "tonal_reference": "C", "collection_name": "C major",
         "pitch_classes": [0, 2, 4, 5, 7, 9, 11], "departures": [], "seed": 7601,
         "identity": "Close voicings move by step: Cmaj9, Dm11, G13sus, Cmaj7. Fifths are omitted. Variation B flips to first-inversion shells and a different soprano.",
         "limitations": "Bass guide A fits variation A. Bass guide B fits variation B. Roots live in the bass file, not the chord file.",
         "voicing": "Right hand, close position around E4 to E5. Root omitted. Left hand is the separate bass guide."},
        {"id": "s02", "slug": "s02-minor-nine", "title": "Minor Nine", "bpm": 84, "bars": 8,
         "tonic": "A", "tonal_reference": "A", "collection_name": "A natural minor",
         "pitch_classes": [9, 11, 0, 2, 4, 5, 7], "departures": ["Variation B bar 6 beat 1 uses D#4, F#4, Bb4, and C#5 (63, 66, 70, 73) for one beat. They resolve to E, A, B, E."],
         "seed": 8402,
         "identity": "One chord per bar, roots omitted: Am9, Dm9, Fmaj7, E7sus, Cmaj7, G7sus, Fmaj7, Em7. Variation B changes every inversion and inserts one chromatic cluster.",
         "limitations": "The chromatic cluster is one beat. The rest of bar 6 is E, A, B, E.",
         "voicing": "Close voicings. The bass guide carries the roots."},
        {"id": "s03", "slug": "s03-gospel-plate", "title": "Gospel Plate", "bpm": 68, "bars": 8,
         "tonic": "F", "tonal_reference": "F", "collection_name": "F major",
         "pitch_classes": [5, 7, 9, 10, 0, 2, 4], "departures": [], "seed": 6803,
         "identity": "A four-bar Fmaj9 plate, then a two-bar Bbmaj9 and a two-bar C11. Variation B breaks the plate into suspensions that resolve inside the bar.",
         "limitations": "Variation A's long hold is the phrase. It is not an unfinished chord.",
         "voicing": "Four-note close voicing. Fifth omitted on the tonic plate."},
        {"id": "s04", "slug": "s04-dim-approach", "title": "Dim Approach", "bpm": 92, "bars": 8,
         "tonic": "D", "tonal_reference": "D", "collection_name": "D major",
         "pitch_classes": [0, 1, 2, 3, 4, 6, 7, 9, 11], "departures": ["D# (3), C (0), and C# (1) are inside the declared set on purpose, so the diminished approach and the A13 color are not flagged."],
         "seed": 9204,
         "identity": "Dmaj9, D#dim7, Em9, A13, then the same roots with a higher soprano. Variation A enters on beat 2. Variation B starts each chord a sixteenth early.",
         "limitations": "The diminished chord is written as notes. It is not a MIDI controller.",
         "voicing": "Close voicing. The bass guide plays the roots in time with variation A."},
        {"id": "s05", "slug": "s05-shells", "title": "Shells", "bpm": 80, "bars": 8,
         "tonic": "G", "tonal_reference": "G", "collection_name": "G major",
         "pitch_classes": [7, 9, 11, 0, 2, 4, 6], "departures": [], "seed": 8005,
         "identity": "Third and seventh only, entering on the second eighth, with a rest after each shell. Variation B fills the bar and adds a diatonic color tone. Bm uses C, the eleventh, because C# is outside G major.",
         "limitations": "Roots are omitted from the chord file. Bass guide A supplies them on the same offbeat.",
         "voicing": "Two-note shells in variation A. Three-note shells in variation B."},
        {"id": "s06", "slug": "s06-flat-cycle", "title": "Flat Cycle", "bpm": 96, "bars": 8,
         "tonic": "Eb", "tonal_reference": "Eb", "collection_name": "Eb major",
         "pitch_classes": [3, 5, 7, 8, 10, 0, 2], "departures": ["Variation B bar 4 beat 2 is A, C#, E, A (69, 73, 76, 81) for one quarter, and bass guide B plays A2 (45) for that same quarter. Both are flagged, then the phrase returns to Ab."],
         "seed": 9606,
         "identity": "Ebmaj9, Cm11, Abmaj7, Bb13, each for two bars, displaced to beat 2. Variation B swaps the Ab for a dominant approach and changes the soprano.",
         "limitations": "Use bass B with variation B. Bass A still outlines Eb, C, Ab, Bb.",
         "voicing": "Close voicings starting on beat 2, so the downbeat is a rest."},
        {"id": "s07", "slug": "s07-unresolved", "title": "Unresolved", "bpm": 72, "bars": 8,
         "tonic": "B", "tonal_reference": "B", "collection_name": "B Dorian",
         "pitch_classes": [11, 1, 2, 4, 6, 8, 9], "departures": ["Variation B bar 6 includes G4 (67) and bass guide B plays G1 (31) for those two bars. The B, D, and F# beside the G stay in B Dorian and are not flagged."], "seed": 7207,
         "identity": "Bm11, E7sus, then a held Amaj9 that never returns to B. Variation B keeps that A for two bars, then moves to G, B, D, F#.",
         "limitations": "The missing return to B is the cadence. It is not a loop error.",
         "voicing": "Close voicing. The last chord is held for four bars in variation A and two bars in variation B."},
        {"id": "s08", "slug": "s08-open-hands", "title": "Open Hands", "bpm": 88, "bars": 8,
         "tonic": "Ab", "tonal_reference": "Ab", "collection_name": "Ab major",
         "pitch_classes": [8, 10, 0, 1, 3, 5, 7], "departures": [], "seed": 8808,
         "identity": "Open voicings a tenth apart, one chord per bar. Variation B closes the same roots into a tight cluster and drops the top voice.",
         "limitations": "The tenth is two notes in one chord file, not a split across hands. The bass guide is still separate.",
         "voicing": "Variation A spans a tenth. Variation B is closed position. Fifths omitted in both."},
    ]
    for row in rows:
        if not 65 <= row["bpm"] <= 100:
            raise ValueError(row["bpm"])
        row["tempo_us"] = bpm_to_us(row["bpm"])
        row["effective_bpm"] = effective_bpm(row["tempo_us"])
        row["meter"] = "4/4"
        row["bar_ticks"] = BAR
        row["ppq"] = PPQ
        row["stochastic_draws"] = 0
    return rows


def _pair(study):
    return chords(study, "a"), chords(study, "b"), bass(study, "a"), bass(study, "b")


def _s01(study):
    ca, cb, ba, bb = _pair(study)
    two = 2 * BAR
    # stepwise: E G B D -> F A C E -> F G C E -> E G B C
    lay(ca, [
        (bar(0), two, [64, 67, 71, 74], 78, False),
        (bar(2), two, [65, 69, 72, 76], 74, False),
        (bar(4), two, [65, 67, 72, 76], 76, False),
        (bar(6), two, [64, 67, 71, 72], 80, False),
    ])
    lay(cb, [
        (bar(0), two, [67, 71, 72, 76], 76, False),
        (bar(2), two, [69, 72, 74, 77], 72, False),
        (bar(4), two, [67, 71, 74, 77], 74, False),
        (bar(6), BAR, [64, 67, 71, 74], 82, False),
        (bar(7), BAR, [60, 64, 67, 71], 70, False),
    ])
    for part, roots in ((ba, (36, 38, 43, 36)), (bb, (48, 41, 43, 36))):
        for i, pitch in enumerate(roots):
            part.add(bar(i * 2), two, pitch, 90 if i == 0 else 78)
    return [ca, cb, ba, bb]


def _s02(study):
    ca, cb, ba, bb = _pair(study)
    # Am9, Dm9, Fmaj7, E7sus, Cmaj7, G7sus, Fmaj7, Em7. Roots omitted.
    upper = [
        [60, 64, 67, 71],
        [65, 69, 72, 76],
        [64, 69, 72, 77],
        [64, 69, 71, 74],
        [64, 67, 71, 72],
        [62, 67, 69, 72],
        [60, 65, 69, 76],
        [59, 64, 67, 74],
    ]
    flipped = [
        [64, 67, 71, 74],
        [65, 69, 74, 77],
        [60, 64, 69, 72],
        [62, 67, 71, 74],
        [65, 69, 72, 77],
        [67, 71, 74, 77],
    ]
    for i, tones in enumerate(upper):
        lay(ca, [(bar(i), BAR, tones, 76, False)])
    for i, tones in enumerate(flipped):
        lay(cb, [(bar(i), BAR, tones, 74, False)])
    lay(cb, [
        (bar(6), PPQ, [63, 66, 70, 73], 84, True),
        (bar(6, 1), BAR - PPQ, [64, 69, 71, 76], 74, False),
        (bar(7), BAR, [59, 64, 67, 72], 70, False),
    ])
    for i, pitch in enumerate((33, 38, 41, 40, 36, 43, 41, 40)):
        ba.add(bar(i), BAR, pitch, 88)
    for i, pitch in enumerate((45, 50, 53, 52, 48, 43, 41, 40)):
        bb.add(bar(i), BAR - PPQ // 2, pitch, 84)
    return [ca, cb, ba, bb]


def _s03(study):
    ca, cb, ba, bb = _pair(study)
    lay(ca, [
        (bar(0), 4 * BAR, [64, 69, 72, 76], 70, False),
        (bar(4), 2 * BAR, [65, 70, 74, 77], 74, False),
        (bar(6), 2 * BAR, [67, 72, 74, 79], 76, False),
    ])
    lay(cb, [
        (bar(0), BAR, [65, 69, 72, 77], 72, False),
        (bar(1), 3 * BAR, [64, 69, 72, 76], 68, False),
        (bar(4), BAR, [70, 74, 77, 82], 74, False),
        (bar(5), BAR, [70, 72, 77, 81], 70, False),
        (bar(6), 2 * BAR, [67, 72, 74, 79], 76, False),
    ])
    ba.add(bar(0), 4 * BAR, 41, 84)
    ba.add(bar(4), 2 * BAR, 46, 80)
    ba.add(bar(6), 2 * BAR, 48, 82)
    bb.add(bar(0), BAR, 41, 86)
    bb.add(bar(1), 3 * BAR, 41, 74)
    bb.add(bar(4), 2 * BAR, 46, 80)
    bb.add(bar(6), 2 * BAR, 43, 82)
    return [ca, cb, ba, bb]


def _s04(study):
    ca, cb, ba, bb = _pair(study)
    # Dmaj9, D#dim7, Em9, A13, then a higher soprano on the same roots.
    cycle = [
        [66, 69, 73, 76],
        [66, 69, 72, 75],
        [67, 71, 74, 78],
        [64, 67, 73, 78],
        [69, 73, 76, 78],
        [69, 72, 75, 78],
        [71, 74, 76, 79],
        [69, 73, 76, 79],
    ]
    for i, tones in enumerate(cycle):
        lay(ca, [(bar(i, 1), PPQ * 3, tones, 78, False)])
        if i == 0:
            lay(cb, [(0, BAR - PPQ // 4, tones, 76, False)])
        else:
            lay(cb, [(bar(i) - PPQ // 4, BAR, tones, 80 if i % 4 == 1 else 74, False)])
    for i, pitch in enumerate((38, 39, 40, 45, 38, 39, 40, 45)):
        ba.add(bar(i, 1), PPQ * 3, pitch, 90)
        if i == 0:
            bb.add(0, BAR - PPQ // 4, pitch, 88)
        else:
            bb.add(bar(i) - PPQ // 4, BAR, pitch, 86)
    return [ca, cb, ba, bb]


def _s05(study):
    ca, cb, ba, bb = _pair(study)
    shells = [[66, 71], [67, 72], [69, 74], [71, 76], [62, 67], [66, 72], [62, 67], [59, 64]]
    colored = [
        [66, 69, 71],
        [67, 71, 72],
        [69, 72, 74],
        [71, 74, 76],
        [62, 66, 71],
        [66, 69, 72],
        [67, 69, 74],
        [64, 71, 74],
    ]
    for i, tones in enumerate(shells):
        lay(ca, [(bar(i) + PPQ // 2, PPQ * 2, tones, 80, False)])
    for i, tones in enumerate(colored):
        lay(cb, [(bar(i), BAR, tones, 74, False)])
    for i, pitch in enumerate((43, 45, 47, 48, 40, 38, 43, 48)):
        ba.add(bar(i) + PPQ // 2, PPQ * 2, pitch, 92)
    for i, pitch in enumerate((31, 33, 35, 36, 40, 38, 31, 36)):
        bb.add(bar(i), BAR, pitch, 84)
    return [ca, cb, ba, bb]


def _s06(study):
    ca, cb, ba, bb = _pair(study)
    lay(ca, [
        (bar(0, 1), 2 * BAR - PPQ, [67, 70, 74, 75], 74, False),
        (bar(2, 1), 2 * BAR - PPQ, [63, 67, 70, 74], 72, False),
        (bar(4, 1), 2 * BAR - PPQ, [68, 72, 75, 80], 76, False),
        (bar(6, 1), 2 * BAR - PPQ, [65, 68, 72, 74], 78, False),
    ])
    lay(cb, [
        (bar(0, 1), 2 * BAR - PPQ, [70, 75, 77, 82], 76, False),
        (bar(2, 1), 2 * BAR - PPQ, [67, 70, 74, 77], 72, False),
        (bar(4, 1), PPQ, [69, 73, 76, 81], 90, True),
        (bar(4, 2), 2 * BAR - 2 * PPQ, [68, 72, 75, 80], 74, False),
        (bar(6, 1), 2 * BAR - PPQ, [70, 74, 77, 82], 78, False),
    ])
    for i, pitch in enumerate((39, 36, 44, 46)):
        ba.add(bar(i * 2, 1), 2 * BAR - PPQ, pitch, 86)
    bb.add(bar(0, 1), 2 * BAR - PPQ, 39, 86)
    bb.add(bar(2, 1), 2 * BAR - PPQ, 36, 84)
    bb.add(bar(4, 1), PPQ, 45, 96, departure=True)
    bb.add(bar(4, 2), 2 * BAR - 2 * PPQ, 44, 82)
    bb.add(bar(6, 1), 2 * BAR - PPQ, 46, 86)
    return [ca, cb, ba, bb]


def _s07(study):
    ca, cb, ba, bb = _pair(study)
    lay(ca, [
        (bar(0), 2 * BAR, [66, 69, 73, 76], 74, False),
        (bar(2), 2 * BAR, [69, 71, 74, 76], 76, False),
        (bar(4), 4 * BAR, [61, 64, 68, 71], 70, False),
    ])
    lay(cb, [
        (bar(0), 2 * BAR, [66, 69, 73, 76], 74, False),
        (bar(2), 2 * BAR, [69, 71, 74, 76], 76, False),
        (bar(4), 2 * BAR, [61, 64, 68, 71], 72, False),
    ])
    for pitch, departure in ((67, True), (71, False), (74, False), (78, False)):
        cb.add(bar(6), 2 * BAR, pitch, 78, departure=departure)
    ba.add(bar(0), 2 * BAR, 35, 88)
    ba.add(bar(2), 2 * BAR, 40, 84)
    ba.add(bar(4), 4 * BAR, 33, 80)
    bb.add(bar(0), 2 * BAR, 35, 88)
    bb.add(bar(2), 2 * BAR, 40, 84)
    bb.add(bar(4), 2 * BAR, 33, 82)
    bb.add(bar(6), 2 * BAR, 31, 86, departure=True)
    return [ca, cb, ba, bb]


def _s08(study):
    ca, cb, ba, bb = _pair(study)
    opens = [
        [56, 68, 72], [58, 70, 75], [60, 72, 75], [61, 73, 77],
        [63, 75, 80], [65, 77, 80], [60, 72, 75], [61, 73, 77],
    ]
    closed = [
        [68, 72, 75], [70, 73, 77], [72, 75, 80], [68, 73, 75],
        [70, 75, 77], [72, 77, 80], [63, 68, 72], [65, 68, 73],
    ]
    for i, tones in enumerate(opens):
        lay(ca, [(bar(i), BAR - PPQ // 2, tones, 76, False)])
    for i, tones in enumerate(closed):
        lay(cb, [(bar(i), PPQ * 3, tones, 80, False)])
    for i, pitch in enumerate((32, 34, 36, 37, 39, 41, 32, 34)):
        ba.add(bar(i), PPQ * 2, pitch, 90)
        bb.add(bar(i), PPQ, pitch, 88)
    return [ca, cb, ba, bb]


BUILDERS = {f"s0{i}": fn for i, fn in enumerate([_s01, _s02, _s03, _s04, _s05, _s06, _s07, _s08], 1)}


def _sig(notes):
    return tuple((n["performed_start"], n["pitch"], n["duration"]) for n in notes)


def assert_collections(catalog_studies, parts):
    allowed = {study["id"]: set(study["pitch_classes"]) for study in catalog_studies}
    for part in parts:
        pool = allowed[part["study_id"]]
        for note in part["notes"]:
            inside = (note["pitch"] % 12) in pool
            if note["departure"] and inside:
                raise ValueError(f"{part['id']} departure {note['pitch']} is inside the collection")
            if not note["departure"] and not inside:
                raise ValueError(f"{part['id']} note {note['pitch']} left the collection")


def assert_identities(parts):
    chords_only = [p for p in parts if p["role"] == "chord-progression"]
    by = {}
    for part in chords_only:
        by.setdefault(part["study_id"], {})[part["variation"]] = part
    rhythms = {}
    report = []
    for study_id, vars_ in by.items():
        if _sig(vars_["a"]["notes"]) == _sig(vars_["b"]["notes"]):
            raise ValueError(f"{study_id} variations match")
        rhythm = tuple(n["performed_start"] for n in vars_["a"]["notes"])
        if rhythm in rhythms:
            raise ValueError(f"{study_id} rhythm repeats {rhythms[rhythm]}")
        rhythms[rhythm] = study_id
        report.append({"study_id": study_id, "a": len(vars_["a"]["notes"]), "b": len(vars_["b"]["notes"])})
    return {"studies": report, "method": "chord variations differ; variation A attack times are not shared"}


def compose():
    catalog_studies = studies()
    parts = []
    for study in catalog_studies:
        for part in BUILDERS[study["id"]](study):
            parts.append(part.finish())
    assert_collections(catalog_studies, parts)
    identity = assert_identities(parts)
    core = [p for p in parts if p["core"]]
    refs = [p for p in parts if not p["core"]]
    if len(core) != 16:
        raise ValueError(len(core))
    arrangement = {
        "id": "arrangement-preview-s01a",
        "path": "midi/arrangement.mid",
        "format": 1,
        "container_ticks": 8 * BAR,
        "bpm": 76,
        "tempo_us": bpm_to_us(76),
        "meter": "4/4",
        "description": "Study 01 variation A chords with bass guide A. The bass is not inside the chord file.",
        "tracks": [
            {"name": "Conductor", "source_part": None, "channel": None},
            {"name": "Chord Progression", "source_part": "s01.chords.a", "channel": 0},
            {"name": "Bass Guide", "source_part": "s01.bass.a", "channel": 1},
        ],
    }
    catalog = {
        "pack_id": PACK_ID, "pack_name": PACK_NAME,
        "catalog_version": GENERATOR_VERSION, "generator_version": GENERATOR_VERSION,
        "ppq": PPQ, "meter": {"numerator": 4, "denominator": 4, "bar_ticks": BAR},
        "pitched_range": [28, 84], "c4": 60,
        "note_policy": "note-only MIDI. Pedal, slides, and Rhodes settings are not encoded.",
        "microtiming": "offset is 0; performed_start = nominal_start",
        "stochastic_draws": 0,
        "seed_meaning": "Seeds identify studies. Nothing is random.",
        "core_part_count": len(core), "reference_part_count": len(refs),
        "hand_distribution": "Chord files are the upper voices. Bass guides are separate monophonic files and are not part of the core count.",
        "studies": [{k: s[k] for k in (
            "id", "slug", "title", "bpm", "tempo_us", "effective_bpm", "bars", "meter", "bar_ticks",
            "tonic", "tonal_reference", "collection_name", "pitch_classes", "departures", "seed",
            "identity", "limitations", "voicing", "stochastic_draws",
        )} for s in catalog_studies],
        "parts": [{
            "id": p["id"], "study_id": p["study_id"], "role": p["role"], "variation": p["variation"],
            "core": p["core"], "channel": p["channel"], "path": p["path"], "notes": len(p["notes"]),
            "container_bars": p["container_bars"], "bpm": p["bpm"], "monophonic": p["monophonic"],
        } for p in parts],
        "arrangement": arrangement,
        "preview_part_ids": ["s01.chords.a", "s01.bass.a"],
        "stack_warning": "Use either the combined arrangement or the separate parts. Do not stack the part files on top of the combined file.",
    }
    score = {
        "pack_id": PACK_ID, "generator_version": GENERATOR_VERSION, "ppq": PPQ,
        "parts": parts, "arrangement": arrangement, "identity_check": identity,
    }
    return {"catalog": catalog, "score": score}
