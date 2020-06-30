def about_us_check(df, hyperlinks):
    """Return boolean of about us link existance"""

    print("Checking about us...")
    keyword_about = ["about", "tentang"]
    avoid = ["conditioner", "termurah", "termahal", "expired", "expire", "renewal"]

    about_mask = pd.Series(hyperlinks).str.lower().str.contains('|'.join(keyword_about)) & ~pd.Series(hyperlinks).str.lower().str.contains('|'.join(avoid))
    about_count = 1 if np.count_nonzero(np.array(hyperlinks)[about_mask]) >= 1 else 0
    
    if about_count == 1:
        print("About Us Link: %s" % np.array(hyperlinks)[about_mask][0])
    ## Check for inexact link
    try:
        if about_count < 1:
            base_url = str(df['website'].values[0])
            links, texts = get_hyperlinks_dynamic(url_format_handler(base_url))
            if len(links) > 0:
                for i in range(len(links)):
                    ## About Us Link Finder
                    if pd.Series(str(texts[i])).str.lower().str.contains('|'.join(keyword_about)).any():
                        print("About Us Link: %s" % links[i])
                        about_count = 1
    except Exception as e:
        print(e)
        pass

    res_df = pd.DataFrame({"merchant_name": df['merchant_name'].values[0], "link_about_us_exist": int(about_count)}, index=[0])
    print("About us checked.\n")

    return res_df