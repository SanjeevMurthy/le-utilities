# python script to fetch all the videos URL in a YouTube playlist
import requests

#add function to check if transcription is available for each of the videos in the playlist
def is_transcription_available(video_id, api_key):
    base_url = "https://www.googleapis.com/youtube/v3/captions"
    params = {
        'part': 'snippet',
        'videoId': video_id,
        'key': api_key
    }
    response = requests.get(base_url, params=params)
    data = response.json()
    return len(data.get('items', [])) > 0

def get_playlist_videos(playlist_id, api_key):
    base_url = "https://www.googleapis.com/youtube/v3/playlistItems"
    videos = []
    next_page_token = None

    while True:
        params = {
            'part': 'snippet',
            'playlistId': playlist_id,
            'maxResults': 100,
            'key': api_key,
            'pageToken': next_page_token
        }
        response = requests.get(base_url, params=params)
        data = response.json()

        for item in data.get('items', []):
            video_id = item['snippet']['resourceId']['videoId']
            video_url = f"https://www.youtube.com/watch?v={video_id}"
            videos.append(video_url)

        next_page_token = data.get('nextPageToken')
        if not next_page_token:
            break

    return videos

# Example usage
if __name__ == "__main__":
    # Read API_KEY and PLAYLIST_ID as user inputs from the command line or environment variables
    API_KEY = input("Enter your YouTube Data API key: ")  # Replace with your YouTube Data API key
    PLAYLIST_ID = input("Enter your YouTube playlist ID: ")  # Replace with your YouTube playlist ID
    video_urls = get_playlist_videos(PLAYLIST_ID, API_KEY)
    #Print the video URLs and total count
    print(f"Total videos in playlist: {len(video_urls)}")
    # Write the video URLs to a text file
    with open(f'{ PLAYLIST_ID }.txt', 'w') as f:
        for url in video_urls:
            f.write(url + '\n')
    print("Video URLs:")
    for url in video_urls:
        print(url)
# Note: Make sure to replace 'your_api_key_here' and 'your_playlist_id_here' with actual values.
# You can obtain an API key from the Google Developer Console and a playlist ID from the YouTube playlist URL.