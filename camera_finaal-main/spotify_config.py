import spotipy
from spotipy.oauth2 import SpotifyOAuth

# Replace these with your Spotify app details
CLIENT_ID = "63ae557f57cd4e31aeb8bcc0db1673d8"
CLIENT_SECRET = "93cc866850954c41a38d0f5b16925a03"
REDIRECT_URI = "http://localhost:8888/callback"

scope = "user-modify-playback-state user-read-playback-state"

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    redirect_uri=REDIRECT_URI,
    scope=scope
))
