def contact_us_score(df, hyperlinks):
    """Return score (percentage) of contact us component in a website"""

    print("Checking contact us...")
    keyword_contact = ["contact", "kontak", "call", "hubungi"]
    avoid = ["conditioner", "termurah", "termahal"]

    contact_mask = pd.Series(hyperlinks).str.lower().str.contains('|'.join(keyword_contact)) \
                   & ~pd.Series(hyperlinks).str.lower().str.contains('|'.join(avoid))

    ## Email, Telephon, Link
    exists = [0, 0, 0]

    try:
        contact_links = list(pd.Series(hyperlinks)[contact_mask].values)
    except Exception as e:
        print(e)
        contact_links = []

    ## Check on all contact links
    if len(contact_links) > 0:
        for link in contact_links:
            paragraf = paragraf_extractor(link)
            print("Contact Us Link: %s" % link)

            exists[0] = 1 if email_matcher(paragraf) == 1 else exists[0]
            exists[1] = 1 if telephone_matcher(paragraf) == 1 else exists[1]
            exists[2] = 1

    ## Check Email & Phone on HomePage
    if np.count_nonzero(exists) == 0:
        base_url = str(df['website'].values[0])
        paragraf = paragraf_extractor(url_format_handler(base_url))
        exists[0] = 1 if email_matcher(paragraf) == 1 else exists[0]
        exists[1] = 1 if telephone_matcher(paragraf) == 1 else exists[1]

    ## Check for Phone in Hyperlink
    if exists[1] == 0 and pd.Series(hyperlinks).str.contains("tel").any():
        tel = pd.Series(hyperlinks)[pd.Series(hyperlinks).str.contains("tel")].values[0]
        exists[1] = 1 if telephone_matcher(tel) == 1 else 0

    if exists[1] == 0 and pd.Series(hyperlinks).str.contains("api.whatsapp").any():
        wa = pd.Series(hyperlinks)[pd.Series(hyperlinks).str.contains("api.whatsapp")].values[0]
        exists[1] = 1 if telephone_matcher(wa) == 1 else 0

    if exists[1] == 0 and pd.Series(hyperlinks).str.contains("wa.me").any():
        wa = pd.Series(hyperlinks)[pd.Series(hyperlinks).str.contains("wa.me")].values[0]
        exists[1] = 1 if telephone_matcher(wa) == 1 else 0

    if exists[0] == 0 and pd.Series(hyperlinks).str.contains("mailto").any():
        mailto = pd.Series(hyperlinks)[pd.Series(hyperlinks).str.contains("mailto")].values[0]
        exists[1] = 1 if email_matcher(mailto) == 1 else 0

    ## Try dynamic crawling if website cannot detect contact link / cu features
    if (len(contact_links) == 0 | exists[1] == 0 | exists[0] == 0) and len(hyperlinks) != 0:
        ## Find Inexact Contact Link
        base_url = str(df['website'].values[0])
        links, texts = get_hyperlinks_dynamic(url_format_handler(base_url))
        if len(links) > 0:
            for i in range(len(links)):
                ## Contact Link Filtering
                if pd.Series(str(texts[i])).str.lower().str.contains('|'.join(keyword_contact)).any():
                    try:
                        link = links[i]
                        print("Contact Us Link: %s" % link)
                        exists[2] = 1

                        ## Search for cu features
                        paragraf = paragraf_extractor_dynamic(url_format_handler(link))
                        exists[0] = 1 if email_matcher(paragraf) == 1 else exists[0]
                        exists[1] = 1 if telephone_matcher(paragraf) == 1 else exists[1]
                    except Exception as e:
                        print(e)
                        continue

    score = np.count_nonzero(np.array(exists)) / len(exists) * 100

    res_df = pd.DataFrame({"merchant_name": df['merchant_name'].values[0], "contact_us_score": score, \
                           "cu_email_exist": int(exists[0]), "cu_phone_number_exist": int(exists[1]), \
                           "link_contact_us_exist": int(exists[2])}, index=[0])

    print("Contact us checked.\n")

    return res_df