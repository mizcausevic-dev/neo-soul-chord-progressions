"""Procedural raster artwork and ffmpeg media steps.

The painter is original and deterministic. It draws vertical note stacks on a
walnut field, with a separate bass row under a gap. It is an illustration,
not a photograph of a session or of performers.

DejaVu Sans Bold is used only to rasterize the disclosure into the film and the
poster. The font file is not shipped.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
ON_PICTURE = "preview, not master"


def _clamp(value: int) -> int:
    return 0 if value < 0 else 255 if value > 255 else value


def paint(width: int, height: int, framing: str) -> bytes:
    columns = 8
    voices = (
        (0.22, 0.30, 0.46, 0.40),
        (0.26, 0.36, 0.42, 0.50),
        (0.24, 0.33, 0.48, 0.44),
        (0.20, 0.34, 0.41, 0.38),
        (0.28, 0.32, 0.47, 0.43),
        (0.23, 0.37, 0.44, 0.52),
        (0.21, 0.31, 0.40, 0.36),
        (0.25, 0.35, 0.45, 0.48),
    )
    margin_x = int(width * (0.12 if framing == "square" else 0.08))
    top = int(height * (0.16 if framing == "square" else 0.18))
    chord_bottom = int(height * (0.62 if framing == "square" else 0.68))
    bass_y = int(height * (0.78 if framing == "square" else 0.84))
    span = width - margin_x * 2
    step = span / columns
    dot = max(4, width // 140)
    pixels = bytearray(width * height * 3)
    for y in range(height):
        shade = y / max(1, height - 1)
        base_r = int(58 + 28 * (1 - shade))
        base_g = int(32 + 16 * (1 - shade))
        base_b = int(22 + 8 * (1 - shade))
        row = y * width * 3
        for x in range(width):
            r, g, b = base_r, base_g, base_b
            if top - 8 <= y <= chord_bottom + 10 and margin_x - 16 <= x <= width - margin_x + 16:
                r, g, b = 247, 239, 224
            if abs(y - (chord_bottom + 18)) <= 1 and margin_x <= x <= width - margin_x:
                r, g, b = 196, 154, 96
            pixels[row + x * 3] = r
            pixels[row + x * 3 + 1] = g
            pixels[row + x * 3 + 2] = b
    def blot(cx: int, cy: int, radius: int, color: tuple[int, int, int]) -> None:
        for y in range(max(0, cy - radius), min(height, cy + radius + 1)):
            for x in range(max(0, cx - radius), min(width, cx + radius + 1)):
                if (x - cx) * (x - cx) + (y - cy) * (y - cy) <= radius * radius:
                    index = (y * width + x) * 3
                    pixels[index] = color[0]
                    pixels[index + 1] = color[1]
                    pixels[index + 2] = color[2]
    for index, stack in enumerate(voices):
        cx = int(margin_x + step * (index + 0.5))
        stem_top = int(top + min(stack) * (chord_bottom - top))
        stem_bottom = int(top + max(stack) * (chord_bottom - top))
        for y in range(stem_top, stem_bottom + 1):
            for x in range(cx - 1, cx + 2):
                if 0 <= x < width:
                    offset = (y * width + x) * 3
                    pixels[offset] = 74
                    pixels[offset + 1] = 46
                    pixels[offset + 2] = 34
        for voice in stack:
            cy = int(top + voice * (chord_bottom - top))
            blot(cx, cy, dot, (201, 122, 42))
        blot(cx, bass_y, dot + 1, (42, 24, 18))
    return bytes(pixels)


def write_ppm(path: Path, width: int, height: int, rgb: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    header = f"P6\n{width} {height}\n255\n".encode("ascii")
    path.write_bytes(header + rgb)


def run(command: list[str]) -> None:
    completed = subprocess.run(command, check=False, capture_output=True, text=True)
    if completed.returncode != 0:
        raise RuntimeError(
            "command failed\n"
            + " ".join(command)
            + "\n"
            + completed.stderr[-2000:]
        )


def ppm_to_jpeg(ppm: Path, jpeg: Path, quality: int = 3) -> None:
    jpeg.parent.mkdir(parents=True, exist_ok=True)
    run(["ffmpeg", "-y", "-i", str(ppm), "-frames:v", "1", "-q:v", str(quality), str(jpeg)])


def draw_disclosure(source: Path, dest: Path, textfile: Path) -> list[str]:
    dest.parent.mkdir(parents=True, exist_ok=True)
    textfile.write_text(ON_PICTURE + "\n", encoding="utf-8")
    command = [
        "ffmpeg", "-y", "-i", str(source),
        "-vf",
        (
            f"drawtext=textfile={textfile}:fontfile={FONT}:fontsize=48:"
            "fontcolor=white:x=(w-text_w)/2:y=h-100:box=1:boxcolor=black@0.68:boxborderw=22"
        ),
        "-frames:v", "1",
        "-q:v", "3",
        str(dest),
    ]
    run(command)
    return command


def encode_mp3(wav: Path, mp3: Path) -> list[str]:
    mp3.parent.mkdir(parents=True, exist_ok=True)
    command = [
        "ffmpeg", "-y", "-i", str(wav),
        "-codec:a", "libmp3lame", "-b:a", "192k",
        str(mp3),
    ]
    run(command)
    return command


def encode_film(plate: Path, mp3: Path, mp4: Path, textfile: Path, duration: str) -> list[str]:
    mp4.parent.mkdir(parents=True, exist_ok=True)
    textfile.write_text(ON_PICTURE + "\n", encoding="utf-8")
    command = [
        "ffmpeg", "-y",
        "-loop", "1", "-framerate", "24", "-i", str(plate),
        "-i", str(mp3),
        "-t", duration,
        "-vf",
        (
            "scale=1280:720,"
            f"drawtext=textfile={textfile}:fontfile={FONT}:fontsize=48:"
            "fontcolor=white:x=(w-text_w)/2:y=h-100:box=1:boxcolor=black@0.68:boxborderw=22"
        ),
        "-r", "24",
        "-c:v", "libx264", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "160k",
        "-shortest",
        "-movflags", "+faststart",
        str(mp4),
    ]
    run(command)
    return command


def derive_social(hero: Path, square: Path, portrait: Path, card: Path) -> dict[str, list[str]]:
    portrait.parent.mkdir(parents=True, exist_ok=True)
    card.parent.mkdir(parents=True, exist_ok=True)
    portrait_cmd = [
        "ffmpeg", "-y", "-i", str(square),
        "-vf", "crop=864:1080:108:0,scale=1080:1350",
        "-q:v", "3",
        str(portrait),
    ]
    card_cmd = [
        "ffmpeg", "-y", "-i", str(hero),
        "-vf", "scale=1600:900",
        "-q:v", "3",
        str(card),
    ]
    run(portrait_cmd)
    run(card_cmd)
    return {"portrait": portrait_cmd, "card": card_cmd}
