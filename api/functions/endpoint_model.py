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