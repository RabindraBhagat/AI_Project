import os
from dotenv import load_dotenv
import google.generativeai as genai
import spotipy
from spotipy.oauth2 import SpotifyOAuth

# Load .env
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
SPOTIFY_REDIRECT_URI = os.getenv("SPOTIFY_REDIRECT_URI")

# Configure Gemini
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('models/gemini-2.0-flash')

# Configure Spotify
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=SPOTIFY_CLIENT_ID,
    client_secret=SPOTIFY_CLIENT_SECRET,
    redirect_uri=SPOTIFY_REDIRECT_URI,
    scope="playlist-modify-private,playlist-modify-public"
))

def get_user_input():
    mood = input("🎵 What's your current mood? (happy/sad/romantic etc): ").strip()
    genre = input("🎧 What domain/genre? (Bollywood, EDM, Lo-fi etc): ").strip()
    count = input("🔢 How many songs do you want?: ").strip()
    return mood, genre, count

def generate_prompt(mood, genre, count):
    return f"Suggest a list of {count} songs for a person who is feeling {mood} and wants to listen to {genre} songs. List only song name and artist."

def get_songs_from_gemini(prompt):
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"❌ Error generating content: {e}")
        return ""

def extract_songs(raw_text):
    songs = []
    for line in raw_text.split('\n'):
        if line.strip():
            songs.append(line.strip("- ").strip())
    return songs

def create_spotify_playlist(songs, mood, genre):
    user_id = sp.current_user()["id"]
    playlist_name = f"{mood.capitalize()} {genre.capitalize()} Playlist"
    playlist = sp.user_playlist_create(user=user_id, name=playlist_name, public=False)
    playlist_id = playlist["id"]

    print(f"\n🎶 Created Spotify Playlist: {playlist_name}")

    # Search and add songs to the playlist
    track_uris = []
    for song in songs:
        results = sp.search(q=song, type="track", limit=1)
        tracks = results.get("tracks", {}).get("items", [])
        if tracks:
            track_uris.append(tracks[0]["uri"])
        else:
            print(f"❌ Song not found on Spotify: {song}")

    if track_uris:
        sp.playlist_add_items(playlist_id, track_uris)
        print(f"✅ Added {len(track_uris)} songs to the playlist.")
        print(f"🎧 Open your playlist here: https://open.spotify.com/playlist/{playlist_id}")
    else:
        print("❌ No songs were added to the playlist.")

def main():
    mood, genre, count = get_user_input()
    prompt = generate_prompt(mood, genre, count)
    print("\n🧠 Generating song list using Gemini AI...")
    raw_output = get_songs_from_gemini(prompt)
    print("\n🎶 Songs Recommended:\n", raw_output)

    songs = extract_songs(raw_output)
    create_spotify_playlist(songs, mood, genre)

if __name__ == "__main__":
    main()

    