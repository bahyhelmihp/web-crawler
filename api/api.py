from gevent import monkey
monkey.patch_all()
import flask
from flask import request, jsonify
from functions.base_functions import run_crawler
from functions.batch_processor import batch_process
import numpy as np
import pickle as p
import pandas as pd
import json

app = flask.Flask(__name__)
app.config["DEBUG"] = False

@app.route('/', methods=['GET'])
def home():
    return '''Home'''

## Endpoint for single crawling + score    
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
    results = run_crawler(url)
    
    return jsonify(results)

## Endpoint for batch crawling + score
@app.route('/api/v1/crawler-batch', methods=['GET'])
def api_url_batch():
    # Check if an url was provided as part of the URL.
    # If url is provided, assign it to a variable.
    # If no url is provided, display an error in the browser.
    if 'input_file' in request.args:
        url = str(request.args['input_file'])
    else:
        return "Error: No url field provided. Please specify an url."
    
    if 'start_index' in request.args:
        start = int(request.args['start_index'])
    else:
        start = 0

    if 'end_index' in request.args:
        end = int(request.args['end_index'])
    else:
        end = 0

    if 'output_file' in request.args:
        name = str(request.args['output_file'])
    else:
        name = 'output_file'

    ## Crawl with/without fraud score, use train = 'true' if you wanted fraud score to be excluded
    if 'train' in request.args:
        train = str(request.args['train']).lower()
    else:
        train = 'true'

    # Create an empty list for our results
    res = batch_process(url, start, end, name, train)
    
    return jsonify(res)

## Endpoint for single score prediction
@app.route('/api/v1/model', methods=['POST'])
def make_prediction():
    # Receive line of features, return prediction score
    data = request.get_json()
    test_data = pd.DataFrame(data)
    prediction = model.predict_proba(test_data)[0][1]
    res = str(prediction)

    return res

if __name__ == "__main__":
    modelfile = 'models/model.pickle'
    model = p.load(open(modelfile, 'rb'))
    app.run(host='0.0.0.0')
