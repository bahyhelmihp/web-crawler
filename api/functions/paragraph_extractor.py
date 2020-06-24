def paragraph_extractor(url):
    ''' Extract all paragraph (texts) found in a given URL '''

    try:
        ## Send request
        page = requests.get(url, headers = {'User-Agent': np.random.choice(user_agent_list)}, timeout=30, verify=False)
        
        ## Parse content
        soup = bs(page.content, 'html.parser')
        all_ps = soup.find_all("p") + soup.find_all("em") + soup.find_all("li") + soup.find_all("address")\
        + soup.find_all("h1") + soup.find_all("h2") + soup.find_all("h3") + soup.find_all("h4") + soup.find_all("h5")\
        + soup.find_all("h6") + soup.find_all("a") + soup.find_all("strong")

        ## CloudFare email getter
        if re.search('data-cfemail', str(soup)) is not None:
            email_code = re.search('data-cfemail="(.+?)"', str(soup)).group(1)
            email = str(decode_email(email_code))
        else:
            email = ""

        ## Metadata getter
        meta_property = soup.find("meta", property="og:description")
        meta_name = soup.find("meta", {"name":"description"})

        if meta_property is not None:
            meta_property = soup.find("meta", property="og:description")["content"]
        else:
            meta_property = ""
        if meta_name is not None:
            meta_name = soup.find("meta", {"name":"description"})["content"]
        else:
            meta_name = ""

        ## Div with class:address getter
        div_address = str(soup.find("div", {"class":'address'}))
        if div_address is None:
            div_address = ""

        list_p = []
        for p in all_ps:
            list_p.append(unidecode.unidecode(p.getText()) + "\n")

        ## Join all paragraphs element
        paragraf = "".join(list_p)
        paragraf += meta_property + meta_name + email + div_address
        paragraf = paragraf.lower()

    except Exception as e:
        print(e)
        paragraf = ""

    return paragraf