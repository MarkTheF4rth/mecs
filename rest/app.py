from flask import Flask, render_template, request
from data_dump import data_dump
from flask import jsonify
import json

app = Flask(__name__)

#Routing
""" Main Page """
@app.route('/')
def index():
    # render home page and pass the data
    return render_template('home.html', data = dump_data)

""" If we want to credit anybody/anything or just write something"""
@app.route('/about')
def about():
    return render_template('about.html')

""" Returns all jsonified events in dump_data """
@app.route('/all', methods=['GET'])
def api_all():
    return jsonify(dump_data)

""" Returns jsonified event of the dump_data at the n-th position """
@app.route('/<string:id>/', methods=['GET'])
def api_event_id(id):
    num_id = int(id)
    return jsonify(dump_data[num_id-1])

""" Return most recent events """
@app.route('/recent', methods=['GET'])
def api_recent_events():
    to_send = list(most_recent)
    # clear most recent
    most_recent.clear()
    print(to_send)
    # send the most recent
    return jsonify(to_send)

""" Add a new event, remove most recent events and add new ones """
@app.route('/addEvent', methods=['POST'])
def api_add_event():
    data_json = json.loads(request.data)
    # update most recent events
    most_recent.append(data_json)
    return 'OK'
    
if __name__ == '__main__':
    # calls a method that reads local events and returns them
    # used solely for display purpposes
    dump_data = data_dump()
    # most recent data
    most_recent = []
    # run the app
    app.run(debug = True, use_reloader = False) # if use_reloader=True, debug=True causes SystemExit error
    