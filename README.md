# YouTube Caption JSON3 Converter

Clean up raw YouTube caption downloads and turn them into readable subtitle files with proper timing.

This project cleans up a caption file downloaded from YouTube and converts it into:

- `txt` with timestamps beside each line
- `srt`
- `vtt`

The downloaded file from YouTube is often saved as a `.txt` file, but its content is actually JSON3 caption data.

This script exists because the raw file is not pleasant to read as-is:

- it contains JSON instead of normal subtitle text
- it includes YouTube rolling-caption events
- the result looks messy if you want clean text with timing

The script works offline after you download that file once.

## Requirements

- Python 3.10 or newer

## Why set the language first

Before downloading anything, set the caption language on YouTube first.

That matters because the `timedtext` request you save is tied to the currently selected caption language. If you switch languages after that, you may end up downloading the wrong caption file.

## How to download the caption file from YouTube

1. Open the YouTube video in your browser.
2. Turn captions on.
3. Select the caption language you want.
4. Open DevTools.
   On Windows: `F12` or `Ctrl+Shift+I`
5. Open the `Network` tab.
6. In the filter box, search for `timedtext`.
7. Reload the page or seek in the video until a `timedtext` request appears.
8. Click that request and open its response in a new tab, or copy the response body.
9. Save the response as a local file.
   YouTube may save it with a `.txt` extension, but the content should still be JSON with an `events` array.

Important:

- If multiple `timedtext` requests appear, choose the one for the language you want.
- Look at query parameters like `lang=en`, `lang=fa`, or `tlang=...` to confirm the language.
- The best input for this script is a caption file downloaded in `json3` format.

## Usage

Run the script:

```bash
python yt_caption.py
```

The script will ask for:

1. The path to the downloaded caption file
2. The output format

Default output format is `txt`.

Example interactive session:

```text
======================================================
YouTube Caption JSON3 Converter
======================================================
Paste the path to the caption file you downloaded from YouTube.
Supported output formats: txt, srt, vtt

Caption file path: D:\Downloads\captions.txt
Output format [txt]:
Done. Saved: D:\Downloads\captions.converted.txt
```

## Command-line usage

You can also pass the file path directly:

```bash
python yt_caption.py "D:\Downloads\captions.txt"
python yt_caption.py "D:\Downloads\captions.txt" -f srt
python yt_caption.py "D:\Downloads\captions.txt" -f vtt
```

## Output behavior

- `txt` output includes timestamps beside each line, for example:

```text
[00:00:01.920] Example caption line
```

- `srt` output includes cue timing and numbering.
- `vtt` output includes cue timing and numbering in WebVTT format.

## Notes

- The script removes YouTube append-only caption events to avoid duplicated rolling lines.
- The source file can have a `.txt` extension as long as the content is valid JSON3.
- Output files are written next to the source file.
- The output filename pattern is:

```text
original-name.converted.txt
original-name.converted.srt
original-name.converted.vtt
```
