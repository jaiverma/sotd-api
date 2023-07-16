# Song of the day

## Server

For running locally,

Create `conf.txt` with Spotify developer `CLIENT_ID`, CLIENT_SECRET', and a
local file path which will store the random state used for generating notes.

```
CLIENT_ID : <redacted>
CLIENT_SECRET : <redacted>
RANDOM_STATE : ./state.bin
```

To start the development server,

```py
$ python wsgi.py
```

To run locally with uwsgi,

```
$ uwsgi --ini ./sotd_api.ini --http :5000
```

To run this on a server using systemd, I created the following service
definition,

```
[Unit]
Description=uWSGI instance to serve sotd_api
After=network.target

[Service]
User=anu
Group=www-data
WorkingDirectory=/home/anu/sotd_api
Environment="PATH=/home/anu/spotify/bin"
ExecStart=/home/anu/spotify/bin/uwsgi --ini sotd_api.ini

[Install]
WantedBy=multi-user.target
```

## Updating notes

There are two note endpoints,

- `/note/love`
- `/note/hi`

I wanted these to be updated daily at midnight IST. My initial approach was to
create a repeating `Timer` using the `threading` module. While this worked in
my local testing for short time periods (e.g. 10 seconds), it would fail for
longer times (e.g. half a day) and I didn't know how to debug it.

I've replaced the note update logic to use a local unix domain socket instead.
The server creates a listener at `/tmp/notes_state.sock` and sending a message
to this socket called `save_state` in the server code, updating the notes.

The message expected is `b'\xc0\xc0\x00\x00\x01\x00\x00\x00'`.
