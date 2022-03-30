import spotipy
from spotipy.oauth2 import SpotifyOAuth

REDIRECT_URI = 'http://localhost:8000/'
SCOPES = 'user-read-private user-read-email user-library-read user-read-recently-played user-read-currently-playing'

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=CLIENT_ID,
                                               client_secret=CLIENT_SECRET,
                                               redirect_uri=REDIRECT_URI,
                                               scope=SCOPES))

results = sp.current_user_playing_track()
print(results)
