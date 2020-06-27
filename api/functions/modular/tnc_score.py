def tnc_score(df, hyperlinks):
    """Return the existance of TnC link and the existance of TnC component in a website"""

    print("Checking TnC...")
    keyword_tnc = ["terms", "term", "syarat", "ketentuan", "condition", "tnc", "kebijakan", "refund", "disclaimer", "policy", "prasyarat", "agreement", "exchange", "return", "retur", "tukar", "faq", "aturan", "pengembalian", "penukaran", "perjanjian"]
    avoid = ["conditioner", "termurah", "termahal", "expired", "expire", "renewal"]

    tnc_mask = pd.Series(hyperlinks).str.lower().str.contains('|'.join(keyword_tnc)) & ~pd.Series(hyperlinks).str.lower().str.contains('|'.join(avoid))

    try:
        tnc_links = pd.Series(hyperlinks)[tnc_mask].values
    except Exception as e:
        print(e)
        tnc_links = []

    ## Refund Policy, Link
    exists = [0, 0]

    if len(tnc_links) > 0:
        exists[1] = 1
        ## Check on all tnc links
        for link in tnc_links:
            paragraf = paragraf_extractor(link)
            print("TnC Link: %s" % link)
            exists[0] = 1 if refund_policy_matcher(paragraf) == 1 else exists[0]

    ## Check refund policy on HomePage
    if exists[0] == 0:
        base_url = str(df['website'].values[0])
        paragraf = paragraf_extractor(url_format_handler(base_url))
        exists[0] = refund_policy_matcher(paragraf)

    ## Try dynamic crawling if website cannot detect tnc link / refund policy
    if (len(tnc_links) == 0 | exists[0] == 0) and len(hyperlinks) != 0:
        ## Find Inexact TnC Link
        base_url = str(df['website'].values[0])
        links, texts = get_hyperlinks_dynamic(url_format_handler(base_url))
        if len(links) > 0:
            for i in range(len(links)):
                ## TnC Link Filtering
                if (pd.Series(str(texts[i])).str.lower().str.contains('|'.join(keyword_tnc)) \
                    & ~pd.Series(str(texts[i])).str.lower().str.contains('|'.join(avoid))).any():
                    try:
                        link = links[i]
                        print("TnC Link: %s" % link)
                        exists[1] = 1

                        ## Search for refund_policy features
                        paragraf = paragraf_extractor_dynamic(url_format_handler(link))
                        exists[0] = 1 if refund_policy_matcher(paragraf) == 1 else exists[0]
                    except Exception as e:
                        print(e)
                        continue

    score = np.count_nonzero(np.array(exists)) / len(exists) * 100

    res_df = pd.DataFrame({"merchant_name": df['merchant_name'].values[0], "tnc_score": score, \
                           "tnc_refund_policy_exist": int(exists[0]), "link_tnc_exist": int(exists[1])}, index=[0])

    print("TnC checked.\n")

    return res_df