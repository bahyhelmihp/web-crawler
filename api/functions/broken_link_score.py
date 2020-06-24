def broken_link_score(df, hyperlinks):
    """ Return score of broken link in a website 
        1 for >= 50 %
        0 for < 50 %
    """

    print("Checking broken link...")

    ## Avoid extraction of external links
    avoid = pd.Series(hyperlinks).str.contains("wa.me") | pd.Series(hyperlinks).str.contains("youtube") | \
    pd.Series(hyperlinks).str.contains("linkedin") | pd.Series(hyperlinks).str.contains("facebook") | \
    pd.Series(hyperlinks).str.contains("cloudflare") | pd.Series(hyperlinks).str.contains("twitter") | \
    pd.Series(hyperlinks).str.contains("github") | pd.Series(hyperlinks).str.contains("instagram") | \
    pd.Series(hyperlinks).str.contains("tokopedia") | pd.Series(hyperlinks).str.contains("bukalapak") | \
    pd.Series(hyperlinks).str.match("tel") | pd.Series(hyperlinks).str.contains("gitlab") | \
    pd.Series(hyperlinks).str.contains("Tel") | pd.Series(hyperlinks).str.contains("jobstreet") | \
    pd.Series(hyperlinks).str.contains("download") | pd.Series(hyperlinks).str.contains("google") | \
    pd.Series(hyperlinks).str.contains("javaScript") | pd.Series(hyperlinks).str.contains("_blank")
    hyperlinks = list(pd.Series(hyperlinks)[~avoid].values)

    ## If length of hyperlinks collected > 10, do sampling
    if len(hyperlinks) > 10:
        hyperlinks = sample(hyperlinks, 10)

    ## Send request
    rs = (grequests.get(x, \
        headers = {}, \
        timeout=20, verify=False) for x in hyperlinks)
    rs_res = grequests.map(rs, size = 3)
    
    links = {}
    i = 0
    if len(hyperlinks) == 1 and hyperlinks[0] == "":
        links = "No hyperlinks gathered"
    else:
        ## Get all response code from sampled links
        for response in rs_res:
            try:
                links[response.request.url] = str(response)
            except Exception as e:
                print(e)
                ## No response/timeout return this
                links[hyperlinks[i]] = 'No Response/Timeout'
            i += 1

    status_not_ok = np.count_nonzero(np.array(rs_res, dtype=str) != '<Response [200]>')
    status_length = len(rs_res)

    try:
        ## Do scoring
        score = status_not_ok/status_length*100
    except Exception as e:
        print(e)
        score = 100

    res_df = pd.DataFrame({"merchant_name": df['merchant_name'].values[0], "broken_link_score": 0 if score < 50 else 1,\
                           "links_response": str(links)}, index=[0])

    print("Broken links checked.\n")

    return res_df