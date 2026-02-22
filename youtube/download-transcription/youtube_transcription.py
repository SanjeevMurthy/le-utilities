#!/usr/bin/env python3
"""
Download YouTube video transcription (English) — single video or entire playlist.

Dependencies:
    pip3 install youtube-transcript-api yt-dlp

Usage:
    python3 youtube_transcription.py
    # Then enter a YouTube video URL, video ID, or playlist URL when prompted.
"""

import sys
import os
import re
from urllib.parse import urlparse, parse_qs

try:
    from youtube_transcript_api import YouTubeTranscriptApi
except ImportError:
    print("Error: youtube-transcript-api is not installed.")
    print("Run: pip3 install youtube-transcript-api")
    sys.exit(1)

try:
    import yt_dlp
except ImportError:
    print("Error: yt-dlp is not installed.")
    print("Run: pip3 install yt-dlp")
    sys.exit(1)


# ─── Input Detection ────────────────────────────────────────────────

def detect_input_type(user_input):
    """
    Determine whether the input is a single video, a playlist, or a text file.
    Returns 'file', 'playlist', or 'video'.
    """
    stripped = user_input.strip()

    # Check if it's a path to an existing text file
    if os.path.isfile(stripped):
        return "file"

    parsed = urlparse(stripped)
    qs = parse_qs(parsed.query)

    # Dedicated playlist page: youtube.com/playlist?list=...
    if parsed.path.startswith("/playlist") and "list" in qs:
        return "playlist"

    # Watch URL that includes a playlist param: ?v=xxx&list=...
    if "list" in qs:
        return "playlist"

    return "video"


def extract_video_id(user_input):
    """Extract a YouTube video ID from a URL or bare video ID."""
    user_input = user_input.strip()

    # Handle direct video ID (11 chars, alphanumeric + _ -)
    if re.match(r'^[A-Za-z0-9_-]{11}$', user_input):
        return user_input

    # Handle various YouTube URL formats
    parsed = urlparse(user_input)
    hostname = parsed.hostname or ""

    # Standard: youtube.com/watch?v=VIDEO_ID
    if "youtube.com" in hostname:
        qs = parse_qs(parsed.query)
        video_id = qs.get("v", [None])[0]
        if video_id:
            return video_id

    # Short: youtu.be/VIDEO_ID
    if "youtu.be" in hostname:
        video_id = parsed.path.lstrip("/")
        if video_id:
            return video_id

    # Embedded: youtube.com/embed/VIDEO_ID
    if "youtube.com" in hostname and "/embed/" in parsed.path:
        video_id = parsed.path.split("/embed/")[-1].split("/")[0]
        if video_id:
            return video_id

    return None


def read_urls_from_file(filepath):
    """
    Read YouTube video URLs from a text file (one URL per line).
    Skips blank lines and lines starting with #.
    Returns a list of URL strings.
    """
    urls = []
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                urls.append(line)
    return urls


def extract_playlist_id(user_input):
    """Extract a YouTube playlist ID from a URL."""
    parsed = urlparse(user_input.strip())
    qs = parse_qs(parsed.query)
    return qs.get("list", [None])[0]


# ─── Playlist Helpers ────────────────────────────────────────────────

def get_playlist_info(playlist_id):
    """
    Fetch playlist title and all video entries using yt-dlp.
    Returns (playlist_title, [(video_id, video_title), ...]).
    """
    url = f"https://www.youtube.com/playlist?list={playlist_id}"
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'skip_download': True,
        'extract_flat': 'in_playlist',
        'ignoreerrors': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            playlist_title = info.get('title', playlist_id)
            entries = info.get('entries', [])
            videos = []
            for entry in entries:
                if entry is None:
                    continue
                vid = entry.get('id') or entry.get('url')
                title = entry.get('title', vid)
                if vid:
                    videos.append((vid, title))
            return playlist_title, videos
    except Exception as e:
        print(f"Error fetching playlist info: {e}")
        return None, []


# ─── Video Metadata ─────────────────────────────────────────────────

def get_video_title(video_id):
    """Fetch the video title using yt-dlp."""
    url = f"https://www.youtube.com/watch?v={video_id}"
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'skip_download': True,
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return info.get('title', video_id)
    except Exception:
        return video_id


def sanitize_filename(name):
    """Remove or replace characters not safe for filenames."""
    name = re.sub(r'[\\/:*?"<>|]', '_', name)
    name = re.sub(r'[\s_]+', '_', name)
    name = name.strip('_ ')
    if len(name) > 200:
        name = name[:200]
    return name


# ─── Transcript Download & Formatting ───────────────────────────────

def download_english_transcript(video_id, verbose=True):
    """
    Download the English transcript for a video.
    Tries manually created English first, then auto-generated.
    Returns (segments, transcript_type) or (None, None).
    """
    ytt_api = YouTubeTranscriptApi()

    try:
        transcript_list = ytt_api.list(video_id)
    except Exception as e:
        if verbose:
            print(f"  Error listing transcripts: {e}")
        return None, None

    if verbose:
        print("  Available transcripts:")
        for transcript in transcript_list:
            tag = "[auto-generated]" if transcript.is_generated else "[manual]"
            print(f"    {transcript.language} ({transcript.language_code}) {tag}")

    # Priority: manual English > auto-generated English
    transcript = None
    transcript_type = None

    try:
        transcript = transcript_list.find_manually_created_transcript(['en'])
        transcript_type = "manual"
        if verbose:
            print("  ✓ Found manually created English transcript.")
    except Exception:
        pass

    if transcript is None:
        try:
            transcript = transcript_list.find_generated_transcript(['en'])
            transcript_type = "auto-generated"
            if verbose:
                print("  ✓ Found auto-generated English transcript.")
        except Exception:
            pass

    if transcript is None:
        if verbose:
            print("  ✗ No English transcript available.")
        return None, None

    try:
        fetched = transcript.fetch()
        segments = fetched.to_raw_data()
        return segments, transcript_type
    except Exception as e:
        if verbose:
            print(f"  Error fetching transcript: {e}")
        return None, None


def format_transcript(segments):
    """Format transcript segments into readable plain text."""
    lines = []
    for seg in segments:
        text = seg.get('text', '')
        lines.append(text)
    return '\n'.join(lines)


def format_transcript_with_timestamps(segments):
    """Format transcript segments with timestamps."""
    lines = []
    for seg in segments:
        start = seg.get('start', 0)
        text = seg.get('text', '')

        hours = int(start // 3600)
        minutes = int((start % 3600) // 60)
        seconds = int(start % 60)

        if hours > 0:
            timestamp = f"[{hours:02d}:{minutes:02d}:{seconds:02d}]"
        else:
            timestamp = f"[{minutes:02d}:{seconds:02d}]"

        lines.append(f"{timestamp} {text}")

    return '\n'.join(lines)


def save_transcript(text, video_title, output_dir):
    """Save transcript text to a file named after the video."""
    safe_name = sanitize_filename(video_title)
    output_file = os.path.join(output_dir, f"{safe_name}.txt")
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(text)
    return output_file


# ─── Processing Logic ───────────────────────────────────────────────

def ask_format_choice():
    """Ask the user for transcript format preference."""
    print("\nFormat options:")
    print("  1. Plain text (no timestamps)")
    print("  2. With timestamps")
    choice = input("Choose format [1/2] (default: 1): ").strip()
    return choice


def process_single_video(video_id, format_choice, output_dir, video_title=None, index=None, total=None):
    """
    Download and save the transcript for a single video.
    Returns (success: bool, output_file: str or None).
    """
    prefix = f"[{index}/{total}] " if index and total else ""

    # Get title if not provided
    if not video_title:
        print(f"\n{prefix}Fetching video title...")
        video_title = get_video_title(video_id)

    print(f"\n{prefix}Processing: {video_title}")
    print(f"  Video ID: {video_id}")

    # Download transcript
    segments, transcript_type = download_english_transcript(video_id, verbose=True)

    if segments is None:
        print(f"  ✗ Skipped — no English transcript available.")
        return False, None

    # Format
    if format_choice == "2":
        transcript_text = format_transcript_with_timestamps(segments)
    else:
        transcript_text = format_transcript(segments)

    # Save
    output_file = save_transcript(transcript_text, video_title, output_dir)
    print(f"  ✓ Saved ({len(segments)} segments, {transcript_type}): {os.path.basename(output_file)}")
    return True, output_file


# ─── Main ────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 60)
    print("YouTube Transcription Downloader")
    print("Supports: Single Video  |  Full Playlist  |  URL File")
    print("=" * 60)

    user_input = input("\nEnter YouTube video URL, video ID, playlist URL, or path to .txt file: ").strip()
    if not user_input:
        print("Error: No input provided.")
        sys.exit(1)

    input_type = detect_input_type(user_input)
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # ── File Mode ─────────────────────────────────────────────────
    if input_type == "file":
        filepath = user_input.strip()
        urls = read_urls_from_file(filepath)
        if not urls:
            print("Error: No URLs found in the file.")
            sys.exit(1)

        file_label = os.path.splitext(os.path.basename(filepath))[0]
        print(f"\n📄 File detected: {os.path.basename(filepath)}")
        print(f"   Video URLs found: {len(urls)}")

        # Create output subfolder named after the file
        file_dir = os.path.join(script_dir, sanitize_filename(file_label))
        os.makedirs(file_dir, exist_ok=True)

        # Ask format once
        format_choice = ask_format_choice()

        # Process each URL
        successes = 0
        failures = []

        for idx, url in enumerate(urls, start=1):
            vid = extract_video_id(url)
            if not vid:
                print(f"\n[{idx}/{len(urls)}] ✗ Could not extract video ID from: {url}")
                failures.append((url, "Invalid URL"))
                continue
            ok, _ = process_single_video(
                video_id=vid,
                format_choice=format_choice,
                output_dir=file_dir,
                index=idx,
                total=len(urls),
            )
            if ok:
                successes += 1
            else:
                failures.append((vid, url))

        # Summary
        print(f"\n{'=' * 60}")
        print(f"✓ File batch complete: {os.path.basename(filepath)}")
        print(f"  Output folder : {file_dir}")
        print(f"  Total URLs    : {len(urls)}")
        print(f"  Downloaded    : {successes}")
        print(f"  Failed/Skipped: {len(failures)}")
        if failures:
            print("\n  Failed videos:")
            for vid, info in failures:
                print(f"    - {vid} ({info})")
        print("=" * 60)

    # ── Playlist Mode ────────────────────────────────────────────
    elif input_type == "playlist":
        playlist_id = extract_playlist_id(user_input)
        if not playlist_id:
            print("Error: Could not extract playlist ID from the URL.")
            sys.exit(1)

        print(f"\n🎵 Playlist detected (ID: {playlist_id})")
        print("Fetching playlist info...")

        playlist_title, videos = get_playlist_info(playlist_id)
        if not videos:
            print("Error: Could not fetch any videos from the playlist.")
            sys.exit(1)

        print(f"Playlist: {playlist_title}")
        print(f"Videos found: {len(videos)}")

        # Create output subfolder for the playlist
        playlist_dir = os.path.join(script_dir, sanitize_filename(playlist_title))
        os.makedirs(playlist_dir, exist_ok=True)

        # Ask format once for all videos
        format_choice = ask_format_choice()

        # Process each video
        successes = 0
        failures = []

        for idx, (vid, title) in enumerate(videos, start=1):
            ok, _ = process_single_video(
                video_id=vid,
                format_choice=format_choice,
                output_dir=playlist_dir,
                video_title=title,
                index=idx,
                total=len(videos),
            )
            if ok:
                successes += 1
            else:
                failures.append((vid, title))

        # Summary
        print(f"\n{'=' * 60}")
        print(f"✓ Playlist complete: {playlist_title}")
        print(f"  Output folder : {playlist_dir}")
        print(f"  Total videos  : {len(videos)}")
        print(f"  Downloaded    : {successes}")
        print(f"  Failed/Skipped: {len(failures)}")
        if failures:
            print("\n  Videos without transcripts:")
            for vid, title in failures:
                print(f"    - {title} ({vid})")
        print("=" * 60)

    # ── Single Video Mode ────────────────────────────────────────
    else:
        video_id = extract_video_id(user_input)
        if not video_id:
            print("Error: Could not extract video ID from input.")
            print("Accepted formats:")
            print("  - https://www.youtube.com/watch?v=VIDEO_ID")
            print("  - https://youtu.be/VIDEO_ID")
            print("  - VIDEO_ID (11 characters)")
            sys.exit(1)

        print(f"\n🎬 Single video detected (ID: {video_id})")

        # Get title
        print("Fetching video title...")
        video_title = get_video_title(video_id)
        print(f"Video title: {video_title}")

        # Ask format
        format_choice = ask_format_choice()

        # Process
        ok, output_file = process_single_video(
            video_id=video_id,
            format_choice=format_choice,
            output_dir=script_dir,
            video_title=video_title,
        )

        if not ok:
            print("\nCould not download transcription. Exiting.")
            sys.exit(1)

        # Preview
        with open(output_file, 'r', encoding='utf-8') as f:
            content = f.read()

        print(f"\n{'=' * 60}")
        print(f"✓ Transcript saved to: {output_file}")
        preview_lines = content.split('\n')[:10]
        print("\nPreview (first 10 lines):")
        print("-" * 40)
        for line in preview_lines:
            print(f"  {line}")
        if len(content.split('\n')) > 10:
            print("  ...")
        print("=" * 60)
