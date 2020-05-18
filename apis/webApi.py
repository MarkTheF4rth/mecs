import flask
from flask import request, jsonify
from flask_cors import CORS, cross_origin
import pika
import json
import threading

events = []
max_size = 50

app = flask.Flask(__name__)
app.config["DEBUG"] = True
app.config['CORS_HEADERS'] = 'Content-Type'

@app.route('/', methods = ['GET'])
@cross_origin()
def home():
    return jsonify(events)

@app.route('/update', methods = ['POST'])
def update():
    global events
    event = json.loads(request.data)
    events.append(event)
    if len(events) > max_size:
        events = events[1:]
    print('[x] Event received!')
    return 'OK'

if __name__ == "__main__":
    app.run(host='0.0.0.0')
