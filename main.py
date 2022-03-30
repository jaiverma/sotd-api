import requests
import random
import string
import base64
import webbrowser
import json
import sys
from datetime import datetime

REDIRECT_URI = 'http://localhost:8000/'
SCOPES = 'user-read-private user-read-email'

class Image():
    def __init__(self, url, width, height):
        self._width = width
        self._height = height
        self.url = url

    def __str__(self):
        return f'url: {self.url}, {self._width}x{self._height}'

class Song():
    def __init__(self):
        self._images = []
        self._artists = []
        self.track_name = ''
        self.album_name = ''
        self.release_date = None
        self.added_date = None

    def add_song(self, track_name, album_name, added_at_date_str, release_date_str, artists, images):
        self.track_name = track_name
        self.album_name = album_name
        self.release_date = datetime.strptime(release_date_str, '%Y-%m-%d')
        self.added_date = datetime.fromisoformat(added_at_date_str.replace('Z', '+00:00'))
        self._artists.extend(artists)
        self._images.extend([Image(i['url'], i['width'], i['height']) for i in images])

    def get_image(self):
        for img in self._images:
            if img._width == 300 and img._height == 300:
                return img

    def __str__(self):
        s = 'Track:\n'
        s += f'\tName: {self.track_name}\n'
        s += f'\tAlbum: {self.album_name}\n'
        s += f'\tRelease Date: {self.release_date.strftime("%d/%m/%Y")}\n'
        s += f'\tArtists: {self._artists}\n'
        s += f'\tImage: {self.get_image()}\n'
        return s

    def html(self):
        artists = ', '.join(self._artists)
        return f'<li><h3>{self.track_name}</h3>\n<p>Album: {self.album_name}\nArtists: {artists}\n<img src="{self.get_image().url}" /></p></li>'

def client_credentials_flow():
    # url = 'https://accounts.spotify.com/api/token'
    # token = base64.b64encode(f'{CLIENT_ID}:{CLIENT_SECRET}'.encode('utf-8')).decode('utf-8')
    # headers = {
    #     'Authorization': f'Basic {token}',
    #     'Content-Type': 'application/x-www-form-urlencoded',
    # }
    # data = {
    #     'grant_type': 'client_credentials',
    # }

    # r = requests.post(url, headers=headers, data=data)
    # if r.status_code != 200:
    #     print('error')
    #     sys.exit(-1)

    # resp = json.loads(r.text)
    # bearer_token = resp['access_token']
    print(bearer_token)
    headers = {
        'Authorization': f'Bearer {bearer_token}',
    }

    playlist_id = '0IKkPLCIcb0NlBiZ0wjSkG'
    fields = 'tracks.items(added_at,track.name,track(album(name,artists,images,release_date)))'
    url = f'https://api.spotify.com/v1/playlists/{playlist_id}?'
    url += f'fields={fields}'
    r = requests.get(url, headers=headers)

    playlist = []

    print(r.status_code)
    data = json.loads(r.text)
    for t in data['tracks']['items']:
        added_at = t['added_at']
        track = t['track']
        track_name = track['name']
        a = track['album']
        album_name = a['name']
        release_date = a['release_date']
        images = a['images']
        artists = [i['name'] for i in a['artists']]

        # track_name, album_name, added_at_date_str, release_date_str, artists, images
        s = Song()
        s.add_song(track_name, album_name, added_at, release_date, artists, images)
        playlist.append(s)

    playlist = sorted(playlist, key=lambda x: x.added_date, reverse=True)
    print('<html>')
    print('<ul>')
    for song in playlist:
        print('\t' + song.html())
    print('</ul>')
    print('</html>')

def auth_flow():
    state = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
    url = 'https://accounts.spotify.com/authorize?'
    url += '&response_type=code'
    url += f'&client_id={CLIENT_ID}'
    url += f'&scope={SCOPES}'
    url += f'&redirect_uri={REDIRECT_URI}'
    url += f'&state={state}'

    webbrowser.open(url)

client_credentials_flow()
