#!/usr/bin/env python3
"""
Convert a downloaded YouTube caption JSON3 file into readable text formats.

The script is intentionally offline-only:
1. Ask for the downloaded caption file path
2. Ask for the output format (default: txt)
3. Write a cleaned file next to the source file
"""

from __future__ import annotations

import argparse
import html
import json
import sys
from pathlib import Path


DEFAULT_FORMAT = "txt"
SUPPORTED_FORMATS = ("txt", "srt", "vtt")


def print_intro() -> None:
    """Show a short interactive header."""
    print("=" * 54)
    print("YouTube Caption JSON3 Converter")
    print("=" * 54)
    print("Paste the path to the caption file you downloaded from YouTube.")
    print(f"Supported output formats: {', '.join(SUPPORTED_FORMATS)}")
    print()


def ms_to_vtt(ms: int) -> str:
    """Convert milliseconds to WebVTT timestamp."""
    hours = ms // 3_600_000
    ms %= 3_600_000
    minutes = ms // 60_000
    ms %= 60_000
    seconds = ms // 1_000
    ms %= 1_000
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}.{ms:03d}"


def ms_to_srt(ms: int) -> str:
    """Convert milliseconds to SRT timestamp."""
    return ms_to_vtt(ms).replace(".", ",")


def ms_to_txt(ms: int) -> str:
    """Convert milliseconds to a readable timestamp for plain text output."""
    return ms_to_vtt(ms)


def load_json_file(path: Path) -> dict:
    """Load a caption export file as JSON."""
    try:
        raw = path.read_text(encoding="utf-8-sig")
    except UnicodeDecodeError:
        raw = path.read_text(encoding="utf-8")

    try:
        return json.loads(raw)
    except json.JSONDecodeError as exc:
        raise RuntimeError(
            f"Invalid JSON file: {path}. Make sure you downloaded the caption in JSON3 format."
        ) from exc


def parse_segments(payload: dict) -> list[dict]:
    """
    Extract clean caption segments from YouTube JSON3.

    We skip append-only events because YouTube uses them to animate rolling captions
    and they create duplicate lines in exported text.
    """
    if not isinstance(payload, dict):
        raise RuntimeError("The file content is not a JSON object.")

    events = payload.get("events")
    if not isinstance(events, list):
        raise RuntimeError("This file does not look like a YouTube JSON3 caption export.")

    segments: list[dict] = []

    for event in events:
        segs = event.get("segs")
        if not segs or event.get("aAppend"):
            continue

        text = html.unescape("".join(seg.get("utf8", "") for seg in segs)).strip()
        if not text:
            continue

        start = int(event.get("tStartMs", 0))
        duration = int(event.get("dDurationMs", 0))
        end = start + duration
        segments.append({"start": start, "end": end, "text": text})

    if not segments:
        raise RuntimeError("No caption segments were found in the file.")

    return segments


def to_txt(segments: list[dict]) -> str:
    """Render segments as plain text with timestamps beside each line."""
    return "\n".join(f"[{ms_to_txt(seg['start'])}] {seg['text']}" for seg in segments) + "\n"


def to_srt(segments: list[dict]) -> str:
    """Render segments as SRT."""
    lines: list[str] = []
    for index, seg in enumerate(segments, start=1):
        lines.extend(
            [
                str(index),
                f"{ms_to_srt(seg['start'])} --> {ms_to_srt(seg['end'])}",
                seg["text"],
                "",
            ]
        )
    return "\n".join(lines).rstrip() + "\n"


def to_vtt(segments: list[dict]) -> str:
    """Render segments as WebVTT."""
    lines = ["WEBVTT", ""]
    for index, seg in enumerate(segments, start=1):
        lines.extend(
            [
                str(index),
                f"{ms_to_vtt(seg['start'])} --> {ms_to_vtt(seg['end'])}",
                seg["text"],
                "",
            ]
        )
    return "\n".join(lines).rstrip() + "\n"


def build_output_path(source: Path, fmt: str) -> Path:
    """Place the converted file next to the source file."""
    return source.with_name(f"{source.stem}.converted.{fmt}")


def prompt_file_path() -> Path:
    """Ask the user for the downloaded caption file path."""
    while True:
        raw = input("Caption file path: ").strip().strip('"')
        if not raw:
            print("Please enter a file path.")
            continue

        path = Path(raw).expanduser()
        if not path.exists():
            print("File not found. Try again.")
            continue
        if not path.is_file():
            print("That path is not a file. Try again.")
            continue
        return path


def prompt_output_format() -> str:
    """Ask the user for a target format, defaulting to txt."""
    while True:
        raw = input(f"Output format [{DEFAULT_FORMAT}]: ").strip().lower() or DEFAULT_FORMAT
        if raw in SUPPORTED_FORMATS:
            return raw
        print(f"Unsupported format. Choose one of: {', '.join(SUPPORTED_FORMATS)}")


def convert_file(source: Path, fmt: str) -> Path:
    """Read, convert, and write a caption file."""
    payload = load_json_file(source)
    segments = parse_segments(payload)
    renderer = {"txt": to_txt, "srt": to_srt, "vtt": to_vtt}[fmt]
    output_path = build_output_path(source, fmt)
    output_path.write_text(renderer(segments), encoding="utf-8")
    return output_path


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Convert a downloaded YouTube JSON3 caption file into txt, srt, or vtt."
    )
    parser.add_argument("file", nargs="?", help="Path to the downloaded caption JSON3 file")
    parser.add_argument(
        "--format",
        "-f",
        choices=SUPPORTED_FORMATS,
        default=None,
        help=f"Output format (default: {DEFAULT_FORMAT})",
    )
    args = parser.parse_args()

    if not args.file:
        print_intro()

    source = Path(args.file).expanduser() if args.file else prompt_file_path()
    if not source.exists() or not source.is_file():
        print("Input file was not found.")
        sys.exit(1)

    fmt = args.format or prompt_output_format()

    try:
        output_path = convert_file(source, fmt)
    except Exception as exc:
        print(f"Conversion failed: {exc}")
        sys.exit(1)

    print(f"Done. Saved: {output_path.resolve()}")


if __name__ == "__main__":
    main()
