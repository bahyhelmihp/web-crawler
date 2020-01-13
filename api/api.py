from gevent import monkey
monkey.patch_all()

import flask
from flask import request, jsonify
from webscrap import orchestrator

app = flask.Flask(__name__)
app.config["DEBUG"] = True

@app.route('/', methods=['GET'])
def home():
    return '''Home'''
    
@app.route('/api/v1/crawler', methods=['GET'])
def api_id():
    # Check if an ID was provided as part of the URL.
    # If ID is provided, assign it to a variable.
    # If no ID is provided, display an error in the browser.
    if 'url' in request.args:
        url = str(request.args['url'])
    else:
        return "Error: No url field provided. Please specify an url."

    # Create an empty list for our results
    results = orchestrator(url)

    return jsonify(results)

if __name__ == "__main__":
    application.run(host='0.0.0.0')
