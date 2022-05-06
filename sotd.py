import requests
import random
import string
import base64
import json
import sys
from datetime import datetime

CLIENT_ID = None
CLIENT_SECRET = None
BEARER_TOKEN = None

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
        self.track_url = ''
        self.track_uri = ''
        self.album_name = ''
        self.release_date = None
        self.added_date = None

    def add_song(self, track_uri, track_name, track_url, album_name, added_at_date_str, release_date_str, artists, images):
        self.track_name = track_name
        self.track_uri = track_uri
        self.track_url = track_url
        self.album_name = album_name
        try:
            self.release_date = datetime.strptime(release_date_str, '%Y-%m-%d')
        except ValueError:
            self.release_date = datetime.strptime(release_date_str, '%Y')
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

    def json(self):
        return {
            'track_name': self.track_name,
            'track_url': self.track_url,
            'track_uri': self.track_uri,
            'album_name': self.album_name,
            'release_date': self.release_date.strftime('%d/%m/%Y'),
            'artists': self._artists,
            'image': self.get_image().url,
        }

def load_config(config_path):
    global CLIENT_ID
    global CLIENT_SECRET

    with open(config_path) as f:
        for line in f:
            d = line.strip().split(':')
            d = list(map(lambda x: x.strip(), d))
            assert len(d) == 2
            k, v = d
            if k == 'CLIENT_ID':
                CLIENT_ID = v
            elif k == 'CLIENT_SECRET':
                CLIENT_SECRET = v

    if CLIENT_SECRET is None or CLIENT_SECRET is None:
        print('config failure...')
        sys.exit(-1)

def auth_and_get_token():
    global BEARER_TOKEN

    url = 'https://accounts.spotify.com/api/token'
    token = base64.b64encode(f'{CLIENT_ID}:{CLIENT_SECRET}'.encode('utf-8')).decode('utf-8')
    headers = {
        'Authorization': f'Basic {token}',
        'Content-Type': 'application/x-www-form-urlencoded',
    }
    data = {
        'grant_type': 'client_credentials',
    }

    r = requests.post(url, headers=headers, data=data)
    if r.status_code != 200:
        print('auth error')
        sys.exit(-1)

    resp = json.loads(r.text)
    BEARER_TOKEN = resp['access_token']

def construct_and_execute_request(endpoint, params=None):
    headers = {
        'Authorization': f'Bearer {BEARER_TOKEN}',
    }

    # build url
    url = f'https://api.spotify.com/v1'
    url += endpoint
    if params is not None:
        url += '?'
    for k, v in params.items():
        url += f'{k}={v}'
        url += '&'
    url = url.rstrip('&')

    r = requests.get(url, headers=headers)

    if r.status_code != 200:
        # the BEARER token probably expired, renew and try again
        auth_and_get_token()
        headers = {
            'Authorization': f'Bearer {BEARER_TOKEN}',
        }
        r = requests.get(url, headers=headers)
        if r.status_code != 200:
            print('something went wrong even after re-auth...')
            sys.exit(-1)

    return r.text

def get_sotd_playlist():
    playlist_id = '0IKkPLCIcb0NlBiZ0wjSkG'
    endpoint = f'/playlists/{playlist_id}'
    params = {'fields': 'tracks.items(added_at,track.name,track.uri,track.external_urls.spotify,track(album(name,artists,images,release_date)))'}
    data = construct_and_execute_request(endpoint, params)

    playlist = []

    data = json.loads(data)
    for t in data['tracks']['items']:
        added_at = t['added_at']
        track = t['track']
        track_url = track['external_urls']['spotify']
        track_uri = track['uri']
        track_name = track['name']
        a = track['album']
        album_name = a['name']
        release_date = a['release_date']
        images = a['images']
        artists = [i['name'] for i in a['artists']]

        # track_name, album_name, added_at_date_str, release_date_str, artists, images
        s = Song()
        s.add_song(track_uri, track_name, track_url, album_name, added_at, release_date, artists, images)
        playlist.append(s)

    playlist = sorted(playlist, key=lambda x: x.added_date, reverse=True)
    return list(map(lambda x: x.json(), playlist))

def get_sotd():
    playlist = get_sotd_playlist()
    assert len(playlist) > 0
    song = playlist[0]

    # add song of the day to past song list too so that when a new song is added
    # to the playlist, our past song list is already updated
    # to make sure we don't display the current song of the day in the past
    # songs list, only return `l[1:]`  in `get_past_songs`
    add_song_to_past(song)

    return song

def add_song_to_past(song):
    with open('past.json') as f:
        data = f.read()

    data = json.loads(data)

    # check if song uri is already present in past songs
    found = False
    for past_song in data:
        if song['track_uri'] == past_song['track_uri']:
            found = True
            break

    if found:
        # already present do nothing
        pass
    else:
        data.insert(0, song)

    with open('past.json', 'w') as f:
        json.dump(data, f)

def get_past_songs():
    past = None
    with open('past.json') as f:
        past = json.load(f)

    if past is None:
        print('error reading past songs :(')
        sys.exit(-1)

    return past[1:]

def main():
    load_config('./conf.txt')
    auth_and_get_token()
    print(get_sotd())

# run auth functions on import
load_config('./conf.txt')
auth_and_get_token()
