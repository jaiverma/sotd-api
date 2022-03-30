from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello_world():
    return '<p>Hello Anu!</p>'

@app.route('/get_sotd')
def sotd():
    return {
        'a': 'b'
    }