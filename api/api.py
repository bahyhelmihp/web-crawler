from gevent import monkey
monkey.patch_all()
import flask
from flask import request, jsonify
from functions.base_functions import orchestrator
from functions.batch_processor import batch_process

app = flask.Flask(__name__)
app.config["DEBUG"] = False

@app.route('/', methods=['GET'])
def home():
    return '''Home'''
    
@app.route('/api/v1/crawler', methods=['GET'])
def api_url():
    # Check if an url was provided as part of the URL.
    # If url is provided, assign it to a variable.
    # If no url is provided, display an error in the browser.
    if 'url' in request.args:
        url = str(request.args['url'])
    else:
        return "Error: No url field provided. Please specify an url."

    # Create an empty list for our results
    results = orchestrator(url)
    return jsonify(results)

@app.route('/api/v1/crawler-batch', methods=['GET'])
def api_url_batch():
    # Check if an url was provided as part of the URL.
    # If url is provided, assign it to a variable.
    # If no url is provided, display an error in the browser.
    if 'url' in request.args:
        url = str(request.args['url'])
    else:
        return "Error: No url field provided. Please specify an url."
    
    if 'start' in request.args:
        start = int(request.args['start'])
    else:
        start = 0

    if 'end' in request.args:
        end = int(request.args['end'])
    else:
        end = 0

    if 'name' in request.args:
        name = str(request.args['name'])
    else:
        name = 'results'

    # Create an empty list for our results
    res = batch_process(url, start, end, name)
    return res

if __name__ == "__main__":
    app.run()
