# song_recommender.py

import os
import webbrowser
from dotenv import load_dotenv
import google.generativeai as genai
import time  # Import time module for delay

# Load .env
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

# Configure Gemini
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('models/gemini-2.0-flash')

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

def play_songs_on_youtube(song_list):
    print("\n🔁 Preparing YouTube links for the songs...\n")
    youtube_links = []
    for song in song_list:
        search_url = f"https://www.youtube.com/results?search_query={song.replace(' ', '+')}"
        youtube_links.append(search_url)
        print(f"🎵 {song}: {search_url}")

    print("\n🎶 Opening the first song in your browser...")
    if youtube_links:
        webbrowser.open_new_tab(youtube_links[0])  # Open the first song
    else:
        print("❌ No songs to play.")

    print("\n📋 You can manually queue the rest of the songs using the links above.")

def extract_songs(raw_text):
    songs = []
    for line in raw_text.split('\n'):
        if line.strip():
            songs.append(line.strip("- ").strip())
    return songs

def main():
    mood, genre, count = get_user_input()
    prompt = generate_prompt(mood, genre, count)
    print("\n🧠 Generating song list using Gemini AI...")
    raw_output = get_songs_from_gemini(prompt)
    print("\n🎶 Songs Recommended:\n", raw_output)

    songs = extract_songs(raw_output)
    play_songs_on_youtube(songs)

if __name__ == "__main__":
    main()