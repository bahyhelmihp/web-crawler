def calculate_score(features):
    """Return fraud prediction score of a website, 0-100 (Good - Bad)"""
    
    ## Post API URL, change the URL to the host site URL
    url = 'http://127.0.0.1:5000/api/v1/model'
    
    ## Process Test Data
    df = pd.DataFrame(features, index=[0])
    columns = ['broken_link_score','link_contact_us_exist', 'cu_email_exist',\
    'cu_phone_number_exist', 'link_about_us_exist', 'link_tnc_exist',\
    'tnc_refund_policy_exist']
    test_df = df[columns]
    data = test_df.to_json()

    ## Post to Model API
    headers = {'content-type': 'application/json', 'Accept-Charset': 'UTF-8'}
    req = requests.post(url, data=data, headers=headers).text
    score = float(req)

    df['prediction_prob'] = score
    df['prediction_class'] = 1 if score >= 0.5 else 0
    res = df

    return res