"""Catalog page. Chord columns are measured from the MIDI files."""

from __future__ import annotations

import json
from pathlib import Path

from tools.statements import AUDITION, ON_PICTURE, PREVIEW_LINE, PROGRAM, PUBLICATION, WARNING


def write_page(path: Path, catalog: dict, report: dict, preview: dict, film: dict) -> None:
    path.write_text(render_page(catalog, report, preview, film), encoding="utf-8")
    path.with_name("media.html").write_text(_media_html(), encoding="utf-8")


def render_page(catalog: dict, report: dict, preview: dict, film: dict) -> str:
    rows = []
    for part in catalog["parts"]:
        kind = "core" if part["core"] else "bass guide"
        rows.append(
            "<tr>"
            f"<td><a href=\"{part['path']}\">{part['id']}</a></td>"
            f"<td>{part['role']}</td>"
            f"<td>{part['variation']}</td>"
            f"<td>{kind}</td>"
            f"<td>{part['bpm']}</td>"
            f"<td>{part['notes']}</td>"
            "</tr>"
        )
    payload = {
        "studies": [
            {
                "id": study["id"],
                "title": study["title"],
                "bpm": study["bpm"],
                "bars": study["bars"],
                "collection": study["collection_name"],
                "tonic": study["tonal_reference"],
                "identity": study["identity"],
                "limitations": study["limitations"],
                "voicing": study["voicing"],
                "departures": study["departures"],
                "tempo_us": study["tempo_us"],
            }
            for study in catalog["studies"]
        ],
        "parts": [
            {
                "id": part["id"],
                "study_id": part["study_id"],
                "role": part["role"],
                "variation": part["variation"],
                "path": part["path"],
            }
            for part in catalog["parts"]
        ],
    }
    data = json.dumps(payload, ensure_ascii=False).replace("<", "\\u003c")
    seconds = f"{preview['seconds_encoded']:.2f}"
    film_seconds = f"{film['duration_seconds']:.2f}"
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Neo-Soul Chord Progressions</title>
  <style>
    :root {{
      --paper: #f4ead7;
      --cream: #fbf6ec;
      --ink: #2a1c14;
      --muted: #6d5648;
      --walnut: #3c241c;
      --amber: #c97a2a;
      --line: rgba(42, 28, 20, .16);
    }}
    * {{ box-sizing: border-box; }}
    html {{ scroll-behavior: smooth; }}
    body {{
      margin: 0;
      background:
        radial-gradient(900px 320px at 100% -10%, rgba(201, 122, 42, .18), transparent 60%),
        var(--paper);
      color: var(--ink);
      font-family: Georgia, "Iowan Old Style", Palatino, serif;
      line-height: 1.45;
      padding-bottom: 84px;
    }}
    a {{ color: #8a4b12; }}
    button, .transport {{ font-family: ui-monospace, Menlo, Consolas, monospace; }}
    .top {{
      position: sticky; top: 0; z-index: 5;
      display: flex; justify-content: space-between; gap: 16px; align-items: center;
      padding: 12px 22px;
      background: rgba(251, 246, 236, .92);
      border-bottom: 1px solid var(--line);
      backdrop-filter: blur(8px);
    }}
    .brand {{ font-family: ui-monospace, Menlo, Consolas, monospace; letter-spacing: .14em; text-transform: uppercase; font-size: .72rem; }}
    .top nav {{ display: flex; gap: 14px; font-family: ui-monospace, Menlo, Consolas, monospace; font-size: .78rem; }}
    main {{ width: min(1180px, calc(100% - 2rem)); margin: 0 auto; }}
    .stage > div {{ min-width: 0; }}
    .stage {{
      display: grid;
      grid-template-columns: minmax(0, .82fr) minmax(0, 1.18fr);
      gap: 28px;
      align-items: start;
      padding: 28px 0 8px;
    }}
    h1 {{ font-weight: 500; font-size: clamp(2.4rem, 6vw, 4.6rem); line-height: .92; margin: 8px 0 12px; letter-spacing: -.03em; }}
    .kicker {{ font-family: ui-monospace, Menlo, Consolas, monospace; letter-spacing: .16em; text-transform: uppercase; color: var(--amber); font-size: .75rem; margin: 0; }}
    .lede {{ font-size: 1.15rem; max-width: 38rem; }}
    .meta {{ color: var(--muted); font-family: ui-monospace, Menlo, Consolas, monospace; font-size: .82rem; }}
    .rail {{ display: flex; gap: 8px; overflow-x: auto; padding: 8px 0 14px; }}
    .rail button, .switch button, .transport button {{
      border: 1px solid var(--line);
      background: var(--cream);
      color: var(--ink);
      border-radius: 999px;
      padding: 8px 12px;
      cursor: pointer;
    }}
    .rail button[aria-pressed="true"], .switch button[aria-pressed="true"], .transport button[aria-pressed="true"] {{
      background: var(--walnut);
      color: var(--cream);
      border-color: var(--walnut);
    }}
    .switch {{ display: flex; gap: 8px; align-items: center; margin: 0 0 10px; }}
    .chart {{
      position: relative;
      background: var(--cream);
      border-radius: 22px;
      min-height: 320px;
      padding: 16px 14px 18px;
      box-shadow: 0 18px 40px rgba(60, 36, 28, .08);
    }}
    .columns {{ position: relative; height: 250px; display: flex; gap: 6px; z-index: 1; }}
    .col {{ position: relative; flex: 1; min-width: 0; }}
    .col.now {{ background: rgba(201, 122, 42, .12); border-radius: 10px; }}
    .tone {{
      position: absolute; left: 2px; right: 2px; height: 22px;
      display: flex; align-items: center; justify-content: center;
      background: var(--amber); color: #2a1c14; border-radius: 999px;
      font-family: ui-monospace, Menlo, Consolas, monospace; font-size: 11px;
    }}
    #leads {{ position: absolute; inset: 16px 14px 18px; width: calc(100% - 28px); height: calc(100% - 34px); z-index: 0; }}
    .basslane {{
      margin-top: 10px; background: var(--walnut); color: var(--cream);
      border-radius: 16px; min-height: 74px; position: relative; padding: 28px 14px 12px;
    }}
    .basslane[hidden] {{ display: none; }}
    .basslane p {{ position: absolute; top: 8px; left: 14px; margin: 0; font-family: ui-monospace, Menlo, Consolas, monospace; font-size: .72rem; letter-spacing: .12em; text-transform: uppercase; color: #e7c49a; }}
    .bnote {{
      position: absolute; top: 34px; transform: translateX(-50%);
      background: #f3ead7; color: var(--ink); border-radius: 999px;
      padding: 4px 8px; font-family: ui-monospace, Menlo, Consolas, monospace; font-size: 11px;
    }}
    .status {{ min-height: 1.2em; color: var(--muted); font-family: ui-monospace, Menlo, Consolas, monospace; font-size: .8rem; }}
    .table-scroll {{ overflow-x: auto; max-width: 100%; }}
    .files {{ width: 100%; border-collapse: collapse; font-family: ui-monospace, Menlo, Consolas, monospace; font-size: .82rem; }}
    .files th, .files td {{ text-align: left; padding: 8px 6px; border-bottom: 1px solid var(--line); }}
    .note, .warn {{ color: var(--muted); }}
    .play {{ border-top: 1px solid var(--line); margin-top: 28px; padding-top: 18px; }}
    audio, video {{ display: block; width: 100%; height: auto; margin: 10px 0 16px; background: #1c120e; }}
    .transport {{
      position: fixed; left: 0; right: 0; bottom: 0; z-index: 6;
      display: flex; gap: 10px; align-items: center; flex-wrap: wrap;
      padding: 10px 16px;
      background: var(--walnut); color: var(--cream);
    }}
    .transport button {{ background: transparent; color: var(--cream); border-color: rgba(251, 246, 236, .35); }}
    .transport button[aria-pressed="true"] {{ background: var(--amber); color: var(--ink); border-color: var(--amber); }}
    .transport span {{ font-size: .78rem; }}
    @media (max-width: 860px) {{
      .stage {{ grid-template-columns: 1fr; }}
      .top nav {{ display: none; }}
      h1 {{ font-size: 2.6rem; }}
    }}
  </style>
</head>
<body>
  <header class="top">
    <a class="brand" href="index.html">Neo-Soul Chord Progressions</a>
    <nav>
      <a href="#chart">Chart</a>
      <a href="#files">Files</a>
      <a href="#reading">Recorded reading</a>
      <a href="media.html">Stills</a>
      <a href="midi/arrangement.mid">Arrangement</a>
    </nav>
  </header>
  <main>
    <section class="stage">
      <div>
        <p class="kicker">Eight studies · extensions, suspensions, voice leading</p>
        <h1 id="title">Suspended Step</h1>
        <p class="lede" id="identity"></p>
        <p class="meta" id="facts"></p>
        <p id="voicing"></p>
        <p class="note" id="limits"></p>
        <p class="note" id="departures"></p>
      </div>
      <div>
        <div class="rail" id="rail" role="tablist" aria-label="Studies"></div>
        <div class="switch" role="group" aria-label="Variation">
          <button type="button" id="var-a" aria-pressed="true">Variation A</button>
          <button type="button" id="var-b" aria-pressed="false">Variation B</button>
        </div>
        <div class="chart" id="chart">
          <svg id="leads" aria-hidden="true"></svg>
          <div class="columns" id="columns"></div>
        </div>
        <div class="basslane" id="basslane" hidden>
          <p>Bass guide, not part of the chord file</p>
          <div id="bassnotes"></div>
        </div>
        <p class="status" id="status" role="status">Reading the MIDI.</p>
      </div>
    </section>
    <p>{catalog['hand_distribution']}</p>
    <p class="warn">{WARNING}</p>
    <h2 id="files">Files</h2>
    <p class="meta">Validation {report['result']}. Core {catalog['core_part_count']}. Bass guides {catalog['reference_part_count']}. <a href="midi/validation-Cursor.json">validation report</a> · <a href="catalog/catalog-Cursor.json">catalog</a></p>
    <div class="table-scroll">
    <table class="files">
      <thead><tr><th>Part</th><th>Role</th><th>Var</th><th>Count</th><th>BPM</th><th>Notes</th></tr></thead>
      <tbody>
        {''.join(rows)}
      </tbody>
    </table>
    </div>
    <section class="play" id="reading">
      <p class="kicker">Recorded reading · study 01 variation A only</p>
      <p>This MP3 is {seconds} seconds. {PREVIEW_LINE}. The film is {film_seconds} seconds and shows {ON_PICTURE}.</p>
      <audio controls preload="metadata" src="preview/preview.mp3"></audio>
      <p><a href="preview/preview.mp3">preview/preview.mp3</a></p>
      <video controls preload="metadata" poster="film/poster.jpg" width="1280" height="720">
        <source src="film/preview.mp4" type="video/mp4">
        <track kind="captions" src="film/preview.vtt" srclang="en" label="English" default>
      </video>
      <p><a href="film/preview.mp4">film/preview.mp4</a> · <a href="film/preview.vtt">film/preview.vtt</a></p>
    </section>
    <p>{PROGRAM}</p>
    <p>{AUDITION}</p>
    <p>{PUBLICATION}</p>
  </main>
  <div class="transport">
    <button type="button" id="play">Play chart</button>
    <button type="button" id="bass-toggle" aria-pressed="false">Bass guide</button>
    <span id="transport-label">Space plays. J and K change study.</span>
  </div>
  <script id="pack" type="application/json">{data}</script>
  <script>
    const pack = JSON.parse(document.getElementById("pack").textContent);
    const NAMES = ["C","C#","D","D#","E","F","F#","G","G#","A","A#","B"];
    const rail = document.getElementById("rail");
    const columns = document.getElementById("columns");
    const leads = document.getElementById("leads");
    const basslane = document.getElementById("basslane");
    const bassnotes = document.getElementById("bassnotes");
    const status = document.getElementById("status");
    let studyId = "s01";
    let variation = "a";
    let chordNotes = [];
    let bassNotes = [];
    let showBass = false;
    let audio = null;
    let playing = false;
    let followId = 0;

    function pitchName(pitch) {{
      return NAMES[pitch % 12] + (Math.floor(pitch / 12) - 1);
    }}

    function readVlq(view, offset) {{
      let value = 0;
      let byte = 0;
      do {{
        byte = view.getUint8(offset);
        offset += 1;
        value = (value << 7) | (byte & 0x7f);
      }} while (byte & 0x80);
      return [value, offset];
    }}

    function parseMidi(buffer) {{
      const view = new DataView(buffer);
      const head = String.fromCharCode(view.getUint8(0), view.getUint8(1), view.getUint8(2), view.getUint8(3));
      if (head !== "MThd" || view.getUint16(12) !== 960) throw new Error("unexpected MIDI header");
      const tracks = view.getUint16(10);
      let offset = 14;
      const notes = [];
      for (let track = 0; track < tracks; track += 1) {{
        const mark = String.fromCharCode(view.getUint8(offset), view.getUint8(offset + 1), view.getUint8(offset + 2), view.getUint8(offset + 3));
        if (mark !== "MTrk") throw new Error("missing track");
        const length = view.getUint32(offset + 4);
        offset += 8;
        const end = offset + length;
        let tick = 0;
        let status = 0;
        const open = new Map();
        while (offset < end) {{
          let delta;
          [delta, offset] = readVlq(view, offset);
          tick += delta;
          let byte = view.getUint8(offset);
          if (byte < 0x80) {{
            if (!status) throw new Error("running status");
          }} else {{
            status = byte;
            offset += 1;
          }}
          if (status === 0xff) {{
            offset += 1;
            let metaLen;
            [metaLen, offset] = readVlq(view, offset);
            offset += metaLen;
            continue;
          }}
          if (status === 0xf0 || status === 0xf7) {{
            let sysLen;
            [sysLen, offset] = readVlq(view, offset);
            offset += sysLen;
            continue;
          }}
          const kind = status & 0xf0;
          const channel = status & 0x0f;
          const data1 = byte < 0x80 ? byte : view.getUint8(offset);
          if (byte >= 0x80) offset += 1;
          let data2 = 0;
          if (kind !== 0xc0 && kind !== 0xd0) {{
            data2 = view.getUint8(offset);
            offset += 1;
          }}
          const key = channel + ":" + data1;
          if (kind === 0x90 && data2 > 0) {{
            open.set(key, tick);
          }} else if (kind === 0x80 || (kind === 0x90 && data2 === 0)) {{
            const start = open.get(key);
            if (start !== undefined) {{
              notes.push({{ pitch: data1, start: start, duration: tick - start, velocity: data2 || 80, channel: channel }});
              open.delete(key);
            }}
          }}
        }}
      }}
      notes.sort((a, b) => a.start - b.start || a.pitch - b.pitch);
      return notes;
    }}

    function partPath(role) {{
      const found = pack.parts.find((part) => part.study_id === studyId && part.role === role && part.variation === variation);
      if (!found) throw new Error("missing " + role);
      return found.path;
    }}

    function study() {{
      return pack.studies.find((item) => item.id === studyId);
    }}

    function renderCopy() {{
      const item = study();
      document.getElementById("title").textContent = item.title;
      document.getElementById("identity").textContent = item.identity;
      document.getElementById("facts").textContent = item.id + " · " + item.bpm + " BPM · " + item.bars + " bars · " + item.collection + " · tonic " + item.tonic;
      document.getElementById("voicing").textContent = item.voicing;
      document.getElementById("limits").textContent = item.limitations;
      document.getElementById("departures").textContent = item.departures.length ? item.departures.join(" ") : "No pitch in this study is flagged as a departure.";
      document.getElementById("transport-label").textContent = item.title + " " + variation.toUpperCase() + " · Space plays · J and K change study";
      for (const button of rail.querySelectorAll("button")) {{
        button.setAttribute("aria-pressed", button.dataset.id === studyId ? "true" : "false");
      }}
      document.getElementById("var-a").setAttribute("aria-pressed", variation === "a" ? "true" : "false");
      document.getElementById("var-b").setAttribute("aria-pressed", variation === "b" ? "true" : "false");
    }}

    function groups(notes) {{
      const map = new Map();
      for (const note of notes) {{
        if (!map.has(note.start)) map.set(note.start, []);
        map.get(note.start).push(note);
      }}
      return [...map.entries()].sort((a, b) => a[0] - b[0]);
    }}

    function draw() {{
      const item = study();
      const container = item.bars * 4 * 960;
      const grouped = groups(chordNotes);
      columns.innerHTML = "";
      if (!grouped.length) {{
        status.textContent = "This variation has no chord notes.";
        return;
      }}
      const pitches = chordNotes.map((note) => note.pitch);
      const low = Math.min(...pitches);
      const high = Math.max(...pitches);
      const span = Math.max(1, high - low);
      grouped.forEach((entry, index) => {{
        const start = entry[0];
        const next = index + 1 < grouped.length ? grouped[index + 1][0] : container;
        const col = document.createElement("div");
        col.className = "col";
        col.dataset.start = String(start);
        col.dataset.end = String(next);
        entry[1].forEach((note) => {{
          const tone = document.createElement("div");
          tone.className = "tone";
          tone.dataset.pitch = String(note.pitch);
          tone.textContent = pitchName(note.pitch);
          const rise = (note.pitch - low) / span;
          tone.style.bottom = (rise * 82) + "%";
          col.appendChild(tone);
        }});
        columns.appendChild(col);
      }});
      bassnotes.innerHTML = "";
      basslane.hidden = !showBass;
      if (showBass) {{
        for (const note of bassNotes) {{
          const mark = document.createElement("div");
          mark.className = "bnote";
          mark.textContent = pitchName(note.pitch);
          mark.style.left = (8 + (note.start / container) * 84) + "%";
          bassnotes.appendChild(mark);
        }}
      }}
      requestAnimationFrame(drawLines);
    }}

    function drawLines() {{
      const cols = [...columns.querySelectorAll(".col")];
      leads.innerHTML = "";
      const width = columns.clientWidth;
      const height = columns.clientHeight;
      leads.setAttribute("viewBox", "0 0 " + width + " " + height);
      leads.setAttribute("width", String(width));
      leads.setAttribute("height", String(height));
      for (let index = 0; index < cols.length - 1; index += 1) {{
        const left = [...cols[index].querySelectorAll(".tone")];
        const right = [...cols[index + 1].querySelectorAll(".tone")];
        const used = new Set();
        for (const tone of left) {{
          let best = null;
          let bestGap = 99;
          for (const other of right) {{
            if (used.has(other)) continue;
            const gap = Math.abs(Number(tone.dataset.pitch) - Number(other.dataset.pitch));
            if (gap < bestGap) {{
              best = other;
              bestGap = gap;
            }}
          }}
          if (!best) continue;
          used.add(best);
          const a = tone.getBoundingClientRect();
          const b = best.getBoundingClientRect();
          const box = columns.getBoundingClientRect();
          const line = document.createElementNS("http://www.w3.org/2000/svg", "line");
          line.setAttribute("x1", String(a.left + a.width / 2 - box.left));
          line.setAttribute("y1", String(a.top + a.height / 2 - box.top));
          line.setAttribute("x2", String(b.left + b.width / 2 - box.left));
          line.setAttribute("y2", String(b.top + b.height / 2 - box.top));
          line.setAttribute("stroke", "#8a4b12");
          line.setAttribute("stroke-width", "1.4");
          leads.appendChild(line);
        }}
      }}
    }}

    async function loadStudy() {{
      stopPlayback();
      renderCopy();
      status.textContent = "Reading the MIDI.";
      columns.innerHTML = "";
      leads.innerHTML = "";
      try {{
        const chordRes = await fetch(partPath("chord-progression"));
        const bassRes = await fetch(partPath("bass-guide"));
        if (!chordRes.ok || !bassRes.ok) throw new Error("MIDI request failed");
        chordNotes = parseMidi(await chordRes.arrayBuffer());
        bassNotes = parseMidi(await bassRes.arrayBuffer());
        status.textContent = chordNotes.length + " chord notes. Bass guide stays on its own row.";
        draw();
      }} catch (error) {{
        chordNotes = [];
        bassNotes = [];
        status.textContent = "The MIDI did not load. " + error.message;
      }}
    }}

    function freq(pitch) {{
      return 440 * Math.pow(2, (pitch - 69) / 12);
    }}

    function schedule(ctx, pitch, when, duration, amount, type) {{
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();
      osc.type = type;
      osc.frequency.value = freq(pitch);
      const attack = Math.min(0.02, duration * 0.25);
      const end = when + duration;
      gain.gain.setValueAtTime(0.0001, when);
      gain.gain.exponentialRampToValueAtTime(amount, when + attack);
      gain.gain.exponentialRampToValueAtTime(0.0001, Math.max(end, when + attack + 0.01));
      osc.connect(gain);
      gain.connect(ctx.destination);
      osc.start(when);
      osc.stop(end + 0.02);
    }}

    function stopPlayback() {{
      playing = false;
      cancelAnimationFrame(followId);
      if (audio) {{
        audio.close();
        audio = null;
      }}
      document.getElementById("play").textContent = "Play chart";
      document.querySelectorAll(".col.now").forEach((col) => col.classList.remove("now"));
    }}

    function playChart() {{
      if (!chordNotes.length) return;
      stopPlayback();
      const ctx = new AudioContext();
      audio = ctx;
      playing = true;
      document.getElementById("play").textContent = "Stop";
      const item = study();
      const seconds = (tick) => tick / 960 * item.tempo_us / 1000000;
      const origin = ctx.currentTime + 0.06;
      const started = origin;
      for (const note of chordNotes) {{
        const when = origin + seconds(note.start);
        const duration = Math.max(0.05, seconds(note.duration));
        schedule(ctx, note.pitch, when, duration, 0.07, "sine");
        schedule(ctx, note.pitch, when, duration, 0.015, "triangle");
      }}
      if (showBass) {{
        for (const note of bassNotes) {{
          schedule(ctx, note.pitch, origin + seconds(note.start), Math.max(0.05, seconds(note.duration)), 0.11, "sine");
        }}
      }}
      const container = seconds(item.bars * 4 * 960);
      const follow = () => {{
        if (!playing || !audio) return;
        const tick = (audio.currentTime - started) * 1000000 / item.tempo_us * 960;
        document.querySelectorAll(".col").forEach((col) => {{
          const start = Number(col.dataset.start);
          const end = Number(col.dataset.end);
          col.classList.toggle("now", tick >= start && tick < end);
        }});
        if (audio.currentTime - started < container) followId = requestAnimationFrame(follow);
        else stopPlayback();
      }};
      follow();
    }}

    function togglePlay() {{
      if (playing) stopPlayback();
      else playChart();
    }}

    function step(direction) {{
      const index = pack.studies.findIndex((item) => item.id === studyId);
      const next = (index + direction + pack.studies.length) % pack.studies.length;
      studyId = pack.studies[next].id;
      loadStudy();
    }}

    pack.studies.forEach((item) => {{
      const button = document.createElement("button");
      button.type = "button";
      button.dataset.id = item.id;
      button.textContent = item.id.slice(1) + " " + item.title;
      button.addEventListener("click", () => {{
        studyId = item.id;
        loadStudy();
      }});
      rail.appendChild(button);
    }});
    document.getElementById("var-a").addEventListener("click", () => {{ variation = "a"; loadStudy(); }});
    document.getElementById("var-b").addEventListener("click", () => {{ variation = "b"; loadStudy(); }});
    document.getElementById("play").addEventListener("click", togglePlay);
    document.getElementById("bass-toggle").addEventListener("click", () => {{
      showBass = !showBass;
      document.getElementById("bass-toggle").setAttribute("aria-pressed", showBass ? "true" : "false");
      basslane.hidden = !showBass;
      if (chordNotes.length) draw();
    }});
    window.addEventListener("keydown", (event) => {{
      const tag = document.activeElement && document.activeElement.tagName;
      if (tag === "INPUT" || tag === "TEXTAREA") return;
      if (event.code === "Space") {{
        event.preventDefault();
        togglePlay();
      }} else if (event.key === "j" || event.key === "J") {{
        step(-1);
      }} else if (event.key === "k" || event.key === "K") {{
        step(1);
      }}
    }});
    window.addEventListener("resize", () => {{ if (chordNotes.length) drawLines(); }});
    loadStudy();
  </script>
</body>
</html>
"""


def _media_html() -> str:
    return """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Neo-Soul Chord Progressions, stills</title>
  <style>
    :root { color-scheme: light; --paper:#f4ead7; --ink:#2a1c14; --muted:#6d5648; --line:rgba(42,28,20,.16); --amber:#8a4b12; }
    * { box-sizing: border-box; }
    body { margin: 0; background: var(--paper); color: var(--ink); font-family: Georgia, "Iowan Old Style", serif; line-height: 1.45; }
    a { color: var(--amber); }
    header, main { width: min(1120px, calc(100% - 2rem)); margin: 0 auto; }
    header { padding: 28px 0 8px; }
    h1 { font-weight: 500; font-size: clamp(2.2rem, 5vw, 4rem); line-height: 0.95; margin: 8px 0; }
    .kicker { font-family: ui-monospace, Menlo, Consolas, monospace; letter-spacing: .14em; text-transform: uppercase; color: #c97a2a; font-size: .75rem; }
    .hero, .shot, .play { margin: 0 0 28px; }
    img, video, audio { display: block; width: 100%; height: auto; background: #1c120e; }
    figcaption { color: var(--muted); font-family: ui-monospace, Menlo, Consolas, monospace; font-size: .82rem; padding: 8px 0 0; }
    .gallery { display: grid; grid-template-columns: 1.1fr .7fr; gap: 18px; align-items: start; margin-bottom: 28px; }
    .play { border-top: 1px solid var(--line); padding-top: 22px; }
    @media (max-width: 800px) { .gallery { grid-template-columns: 1fr; } }
  </style>
</head>
<body>
  <header>
    <p class="kicker"><a href="index.html">Neo-Soul Chord Progressions</a></p>
    <h1>Stills, then the recording.</h1>
    <p>Each frame keeps its own shape. The film and the MP3 sit under the pictures.</p>
  </header>
  <main>
    <figure class="hero">
      <img src="art/hero.jpg" width="1280" height="720" alt="Illustration of vertical note stacks on a cream panel with a separate bass row. Not a photograph of a studio or of performers.">
      <figcaption>art/hero.jpg · 1280 by 720</figcaption>
    </figure>
    <div class="gallery">
      <figure class="shot">
        <img src="art/square.jpg" width="1080" height="1080" alt="Square illustration of vertical note stacks and a separate bass row.">
        <figcaption>art/square.jpg · 1080 by 1080</figcaption>
      </figure>
      <figure class="shot">
        <img src="social/instagram-Cursor/portrait.jpg" width="1080" height="1350" alt="Vertical crop of the note-stack illustration.">
        <figcaption>portrait · 1080 by 1350</figcaption>
      </figure>
    </div>
    <div class="gallery">
      <figure class="shot">
        <img src="social/x-Cursor/card.jpg" width="1600" height="900" alt="Wide card of the note-stack illustration.">
        <figcaption>x card · 1600 by 900</figcaption>
      </figure>
      <figure class="shot">
        <img src="film/poster.jpg" width="1280" height="720" alt="Film poster with the words preview, not master.">
        <figcaption>film/poster.jpg · disclosure on the picture</figcaption>
      </figure>
    </div>
    <section class="play">
      <p class="kicker">Recorded reading · study 01 only</p>
      <audio controls preload="metadata" src="preview/preview.mp3"></audio>
      <p><a href="preview/preview.mp3">preview/preview.mp3</a></p>
      <video controls preload="metadata" poster="film/poster.jpg" width="1280" height="720">
        <source src="film/preview.mp4" type="video/mp4">
        <track kind="captions" src="film/preview.vtt" srclang="en" label="English" default>
      </video>
    </section>
  </main>
</body>
</html>
"""
