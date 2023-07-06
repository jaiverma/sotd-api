from flask import Flask, request, jsonify
from flask_cors import CORS
import sotd

app = Flask(__name__)
CORS(app)

@app.route('/')
def hello_world():
    return '<p>Hello Anu!</p>'

@app.route('/get_sotd')
def song_of_the_day():
    return sotd.get_sotd()

@app.route('/add_to_past', methods=['POST'])
def add_to_past():
    content_type = request.headers.get('Content-Type')
    if content_type == 'application/json':
        data = request.json
        print(data)
        sotd.add_song_to_past(data)
        return 'done!'
    else:
        return 'failed...'

@app.route('/past_songs')
def past_songs():
    return jsonify(sotd.get_past_songs())

@app.route('/note/hi')
def hi_note():
    return 'hu'

@app.route('/note/love')
def love_note():
    return '<3'

if __name__ == '__main__':
    app.run(host='0.0.0.0')
