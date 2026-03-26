#!/usr/bin/env python3
"""
Download YouTube video transcription (English) — single video, playlist, or URL file.

Includes aggressive rate-limiting delays, typed exception handling, adaptive
throttling, retry queues, and IP-block cooldowns to avoid YouTube IP bans.

Dependencies:
    pip3 install youtube-transcript-api yt-dlp

Usage:
    python3 youtube_transcription.py
    # Then enter a YouTube video URL, video ID, playlist URL, or .txt file path.
"""

from __future__ import annotations

import sys
import os
import re
import time
import random
from urllib.parse import urlparse, parse_qs

try:
    from youtube_transcript_api import (
        YouTubeTranscriptApi,
        RequestBlocked,
        IpBlocked,
        NoTranscriptFound,
        TranscriptsDisabled,
    )
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


# ─── Configuration ──────────────────────────────────────────────────

# Delay (seconds) between consecutive transcript downloads in batch mode.
# A random jitter of ±30% is added to avoid predictable request patterns.
BATCH_DELAY_SECONDS = 15

# Retry settings for individual transcript fetches
MAX_RETRIES = 5
RETRY_BASE_DELAY = 30  # seconds — doubles on each retry (30, 60, 120, 240, 480)

# Adaptive throttling: increase delay after each rate-limit hit
PROGRESSIVE_DELAY_INCREMENT = 5  # add 5s to batch delay after each block
MAX_BATCH_DELAY = 60             # cap inter-video delay at 60s

# Cooldown when IP block is detected (seconds)
IP_BLOCK_COOLDOWN = 120  # 2-minute pause when IP blocked

# Retry queue settings for second-pass retries
RETRY_QUEUE_DELAY = 60  # 60s between retries in the second pass


# ─── Shared API Instance ────────────────────────────────────────────
# Reusing a single instance shares the underlying requests.Session and
# its cookies across all requests, which helps avoid triggering bans.

ytt_api = YouTubeTranscriptApi()


# ─── Input Detection ────────────────────────────────────────────────

def detect_input_type(user_input: str) -> str:
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


def extract_video_id(user_input: str) -> str | None:
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


def read_urls_from_file(filepath: str) -> list[str]:
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


def extract_playlist_id(user_input: str) -> str | None:
    """Extract a YouTube playlist ID from a URL."""
    parsed = urlparse(user_input.strip())
    qs = parse_qs(parsed.query)
    return qs.get("list", [None])[0]


# ─── Playlist Helpers ────────────────────────────────────────────────

def get_playlist_info(playlist_id: str) -> tuple[str | None, list[tuple[str, str]]]:
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

def get_video_title(video_id: str) -> str:
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


def sanitize_filename(name: str) -> str:
    """Remove or replace characters not safe for filenames."""
    name = re.sub(r'[\\/:*?"<>|]', '_', name)
    name = re.sub(r'[\s_]+', '_', name)
    name = name.strip('_ ')
    if len(name) > 200:
        name = name[:200]
    return name


# ─── Transcript Download & Formatting ───────────────────────────────

def download_english_transcript(
    video_id: str,
    verbose: bool = True,
) -> tuple[list | None, str | None]:
    """
    Download the English transcript for a video with retry logic.
    Tries manually created English first, then auto-generated.
    Retries up to MAX_RETRIES times with exponential backoff on rate-limit errors.
    Returns (segments, transcript_type) or (None, None).
    """
    for attempt in range(1, MAX_RETRIES + 1):
        result = _try_download_transcript(
            video_id, verbose=(verbose and attempt == 1),
        )

        segments, ttype = result

        if segments is not None and segments != "NO_TRANSCRIPT" and segments != "IP_BLOCKED":
            return segments, ttype  # success

        # No transcript available for this video — don't retry
        if segments == "NO_TRANSCRIPT":
            return None, None

        # IP blocked / rate-limited — retry with exponential backoff
        if attempt < MAX_RETRIES:
            delay = RETRY_BASE_DELAY * (2 ** (attempt - 1))
            jitter = random.uniform(0.7, 1.3)
            wait = delay * jitter
            print(f"  ⏳ Rate-limited. Retrying in {wait:.0f}s "
                  f"(attempt {attempt + 1}/{MAX_RETRIES})...")
            time.sleep(wait)

    print(f"  ✗ Failed after {MAX_RETRIES} attempts.")
    return None, None


def _try_download_transcript(
    video_id: str,
    verbose: bool = True,
) -> tuple[str | list | None, str | None]:
    """
    Single attempt to download a transcript.
    Returns:
      - (segments, type)        on success
      - ("NO_TRANSCRIPT", None) if no English transcript exists
      - ("IP_BLOCKED", None)    on rate-limit / IP block errors
      - (None, None)            on other transient errors
    """
    try:
        transcript_list = ytt_api.list(video_id)
    except (RequestBlocked, IpBlocked) as e:
        if verbose:
            print(f"  ⚠ IP blocked while listing transcripts: {type(e).__name__}")
        return "IP_BLOCKED", None
    except (NoTranscriptFound, TranscriptsDisabled) as e:
        if verbose:
            print(f"  ✗ {type(e).__name__}: {e}")
        return "NO_TRANSCRIPT", None
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
        return "NO_TRANSCRIPT", None

    try:
        fetched = transcript.fetch()
        segments = fetched.to_raw_data()
        return segments, transcript_type
    except (RequestBlocked, IpBlocked) as e:
        if verbose:
            print(f"  ⚠ IP blocked while fetching transcript: {type(e).__name__}")
        return "IP_BLOCKED", None
    except Exception as e:
        if verbose:
            print(f"  ⚠ Error fetching transcript: {e}")
        return None, None


def format_transcript(segments: list) -> str:
    """Format transcript segments into readable plain text."""
    lines = []
    for seg in segments:
        text = seg.get('text', '')
        lines.append(text)
    return '\n'.join(lines)


def format_transcript_with_timestamps(segments: list) -> str:
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


def save_transcript(text: str, video_title: str, output_dir: str) -> str:
    """Save transcript text to a file named after the video."""
    safe_name = sanitize_filename(video_title)
    output_file = os.path.join(output_dir, f"{safe_name}.txt")
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(text)
    return output_file


# ─── Failed Video Log ───────────────────────────────────────────────

def save_failed_log(
    failed_videos: list[tuple[str, str]],
    output_dir: str,
) -> str | None:
    """
    Write a _failed.txt file listing video IDs that couldn't be downloaded.
    Each line is: VIDEO_ID | TITLE_OR_REASON
    Returns the file path, or None if there are no failures.
    """
    if not failed_videos:
        return None
    log_path = os.path.join(output_dir, "_failed.txt")
    with open(log_path, 'w', encoding='utf-8') as f:
        f.write("# Failed video transcripts — re-run these individually or wait and retry\n")
        f.write("# Format: VIDEO_ID | TITLE_OR_REASON\n\n")
        for vid, info in failed_videos:
            f.write(f"{vid} | {info}\n")
    return log_path


# ─── Processing Logic ───────────────────────────────────────────────

def ask_format_choice() -> str:
    """Ask the user for transcript format preference."""
    print("\nFormat options:")
    print("  1. Plain text (no timestamps)")
    print("  2. With timestamps")
    choice = input("Choose format [1/2] (default: 1): ").strip()
    return choice


def batch_delay(
    index: int,
    total: int,
    current_delay: float,
) -> None:
    """
    Sleep between batch requests to avoid YouTube rate-limiting.
    Adds random jitter so requests don't look automated.
    """
    if index < total:  # don't sleep after the last video
        jitter = random.uniform(0.7, 1.3)
        delay = current_delay * jitter
        print(f"  💤 Waiting {delay:.1f}s before next video...")
        time.sleep(delay)


def ip_block_cooldown() -> None:
    """Pause for a long cooldown when an IP block is detected mid-batch."""
    jitter = random.uniform(0.8, 1.2)
    cooldown = IP_BLOCK_COOLDOWN * jitter
    print(f"\n  🛑 IP block detected! Cooling down for {cooldown:.0f}s "
          f"to let the ban expire...")
    time.sleep(cooldown)


def process_single_video(
    video_id: str,
    format_choice: str,
    output_dir: str,
    video_title: str | None = None,
    index: int | None = None,
    total: int | None = None,
) -> tuple[bool, str | None, bool]:
    """
    Download and save the transcript for a single video.
    Returns (success, output_file, was_rate_limited).
    was_rate_limited is True if the failure was due to IP blocking (retryable).
    """
    prefix = f"[{index}/{total}] " if index and total else ""

    # Get title if not provided (single video mode only — avoid extra requests
    # in batch mode where titles come from playlist metadata)
    if not video_title:
        print(f"\n{prefix}Fetching video title...")
        video_title = get_video_title(video_id)

    print(f"\n{prefix}Processing: {video_title}")
    print(f"  Video ID: {video_id}")

    # Download transcript (with retry logic built in)
    segments, transcript_type = download_english_transcript(video_id, verbose=True)

    if segments is None:
        # Check if the file already exists (from a previous run)
        safe_name = sanitize_filename(video_title)
        existing = os.path.join(output_dir, f"{safe_name}.txt")
        if os.path.isfile(existing):
            print(f"  ℹ Already downloaded in a previous run: {os.path.basename(existing)}")
            return True, existing, False

        print(f"  ✗ Skipped — no English transcript available.")
        # Determine if it was a rate-limit failure (heuristic: if all retries
        # exhausted, it's likely rate-limited rather than truly unavailable)
        return False, None, True

    # Format
    if format_choice == "2":
        transcript_text = format_transcript_with_timestamps(segments)
    else:
        transcript_text = format_transcript(segments)

    # Save
    output_file = save_transcript(transcript_text, video_title, output_dir)
    print(f"  ✓ Saved ({len(segments)} segments, {transcript_type}): "
          f"{os.path.basename(output_file)}")
    return True, output_file, False


def process_batch(
    video_list: list[tuple[str, str]],
    format_choice: str,
    output_dir: str,
    label: str,
) -> tuple[int, list[tuple[str, str]]]:
    """
    Process a batch of videos with adaptive throttling and a retry queue.
    video_list: [(video_id, video_title), ...]
    Returns (successes, permanent_failures).
    """
    total = len(video_list)
    successes = 0
    rate_limited_queue = []  # videos to retry in second pass
    permanent_failures = []  # videos with no English transcript at all
    current_delay = BATCH_DELAY_SECONDS

    # ── First Pass ───────────────────────────────────────────────
    print(f"\n{'─' * 60}")
    print(f"  Pass 1: Downloading {total} transcripts (delay: {current_delay}s)")
    print(f"{'─' * 60}")

    for idx, (vid, title) in enumerate(video_list, start=1):
        ok, _, was_rate_limited = process_single_video(
            video_id=vid,
            format_choice=format_choice,
            output_dir=output_dir,
            video_title=title,
            index=idx,
            total=total,
        )
        if ok:
            successes += 1
        elif was_rate_limited:
            rate_limited_queue.append((vid, title))
            # Increase delay adaptively
            current_delay = min(
                current_delay + PROGRESSIVE_DELAY_INCREMENT,
                MAX_BATCH_DELAY,
            )
            print(f"  📈 Adaptive delay increased to {current_delay:.0f}s")
            # Inject a cooldown if we're accumulating failures
            if len(rate_limited_queue) % 3 == 0:
                ip_block_cooldown()
        else:
            permanent_failures.append((vid, title))

        # Throttle between requests
        batch_delay(idx, total, current_delay)

    # ── Second Pass (Retry Queue) ────────────────────────────────
    if rate_limited_queue:
        print(f"\n{'─' * 60}")
        print(f"  Pass 2: Retrying {len(rate_limited_queue)} rate-limited videos "
              f"(delay: {RETRY_QUEUE_DELAY}s)")
        print(f"{'─' * 60}")

        # Long cooldown before retry pass
        ip_block_cooldown()

        retry_total = len(rate_limited_queue)
        still_failed = []

        for idx, (vid, title) in enumerate(rate_limited_queue, start=1):
            ok, _, was_rate_limited = process_single_video(
                video_id=vid,
                format_choice=format_choice,
                output_dir=output_dir,
                video_title=title,
                index=idx,
                total=retry_total,
            )
            if ok:
                successes += 1
            else:
                still_failed.append((vid, title))
                if was_rate_limited and len(still_failed) % 2 == 0:
                    ip_block_cooldown()

            # Longer delay for retry pass
            batch_delay(idx, retry_total, RETRY_QUEUE_DELAY)

        permanent_failures.extend(still_failed)

    return successes, permanent_failures


# ─── Main ────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 60)
    print("YouTube Transcription Downloader")
    print("Supports: Single Video  |  Full Playlist  |  URL File")
    print("=" * 60)

    user_input = input(
        "\nEnter YouTube video URL, video ID, playlist URL, "
        "or path to .txt file: "
    ).strip()
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

        # Build video list — extract IDs from URLs
        video_list = []
        invalid_urls = []
        for url in urls:
            vid = extract_video_id(url)
            if vid:
                video_list.append((vid, url))  # URL as placeholder title
            else:
                print(f"  ✗ Could not extract video ID from: {url}")
                invalid_urls.append((url, "Invalid URL"))

        # Process batch with adaptive throttling and retry queue
        successes, failures = process_batch(
            video_list=video_list,
            format_choice=format_choice,
            output_dir=file_dir,
            label=file_label,
        )

        # Add invalid URLs to failure list
        all_failures = invalid_urls + failures

        # Save failed log
        if all_failures:
            log_path = save_failed_log(all_failures, file_dir)
            if log_path:
                print(f"\n  📝 Failed video log: {log_path}")

        # Summary
        print(f"\n{'=' * 60}")
        print(f"✓ File batch complete: {os.path.basename(filepath)}")
        print(f"  Output folder : {file_dir}")
        print(f"  Total URLs    : {len(urls)}")
        print(f"  Downloaded    : {successes}")
        print(f"  Failed/Skipped: {len(all_failures)}")
        if all_failures:
            print("\n  Failed videos:")
            for vid, info in all_failures:
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

        # Process batch with adaptive throttling and retry queue
        successes, failures = process_batch(
            video_list=videos,
            format_choice=format_choice,
            output_dir=playlist_dir,
            label=playlist_title,
        )

        # Save failed log
        if failures:
            log_path = save_failed_log(failures, playlist_dir)
            if log_path:
                print(f"\n  📝 Failed video log: {log_path}")

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
        ok, output_file, _ = process_single_video(
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
