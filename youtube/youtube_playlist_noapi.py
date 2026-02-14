# Extract all video URLs from a YouTube playlist without requiring an API key
# Uses yt-dlp library for extraction
import sys
import os
from urllib.parse import urlparse, parse_qs

try:
    import yt_dlp
except ImportError:
    print("Error: yt-dlp is not installed. Run: pip3 install yt-dlp")
    sys.exit(1)


def parse_playlist_input(user_input):
    """Accept a playlist URL or bare playlist ID, return (url, playlist_id)."""
    user_input = user_input.strip()
    if user_input.startswith(("http://", "https://")):
        parsed = urlparse(user_input)
        qs = parse_qs(parsed.query)
        playlist_id = qs.get("list", [None])[0]
        if not playlist_id:
            print("Error: Could not extract playlist ID from URL.")
            sys.exit(1)
        return user_input, playlist_id
    else:
        playlist_id = user_input
        url = f"https://www.youtube.com/playlist?list={playlist_id}"
        return url, playlist_id


def get_playlist_videos(playlist_url):
    """Extract all video URLs from a playlist using yt-dlp."""
    ydl_opts = {
        'extract_flat': True,
        'quiet': True,
        'no_warnings': True,
        'ignoreerrors': True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        result = ydl.extract_info(playlist_url, download=False)

    if result is None:
        print("Error: Could not extract playlist information. Check the playlist ID/URL.")
        sys.exit(1)

    playlist_title = result.get('title', 'Unknown Playlist')
    entries = result.get('entries', [])

    video_urls = []
    for entry in entries:
        if entry is None:
            continue
        video_id = entry.get('id', '')
        if video_id:
            video_urls.append(f"https://www.youtube.com/watch?v={video_id}")

    return playlist_title, video_urls


def save_results(video_urls, filename_prefix, playlist_id):
    """Write video URLs to a text file, one per line."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_file = os.path.join(script_dir, f"{filename_prefix}_{playlist_id}.txt")
    with open(output_file, 'w') as f:
        for url in video_urls:
            f.write(url + '\n')
    return output_file


if __name__ == "__main__":
    print("=" * 60)
    print("YouTube Playlist Video Extractor (No API Key Required)")
    print("=" * 60)

    user_input = input("\nEnter playlist URL or playlist ID: ").strip()
    if not user_input:
        print("Error: No input provided.")
        sys.exit(1)

    filename_prefix = input("Enter filename prefix: ").strip()
    if not filename_prefix:
        print("Error: No filename prefix provided.")
        sys.exit(1)

    playlist_url, playlist_id = parse_playlist_input(user_input)

    print(f"\nFetching videos from playlist...")

    try:
        playlist_title, video_urls = get_playlist_videos(playlist_url)
    except Exception as e:
        print(f"Error extracting playlist: {e}")
        sys.exit(1)

    if not video_urls:
        print("No videos found in playlist.")
        sys.exit(1)

    print(f"Playlist: {playlist_title}")
    print(f"Total videos found: {len(video_urls)}")

    output_file = save_results(video_urls, filename_prefix, playlist_id)
    print(f"Results saved to: {output_file}")

    print("\n" + "-" * 60)
    print("Video URLs:")
    print("-" * 60)
    for url in video_urls:
        print(f"  {url}")
    print("=" * 60)
