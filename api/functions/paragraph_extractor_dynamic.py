def paragraf_extractor_dynamic(url):
    ''' Extract all paragraph (texts) found in a given dynamic page URL '''

    try:
        ## Send request
        print("- Extracting paragraphs dynamically")
        driver.set_page_load_timeout(60)
        driver.get(url)

        ## Parse content
        soup = bs(driver.page_source, 'html.parser')

        all_ps = driver.find_elements_by_tag_name("p") + driver.find_elements_by_tag_name(
            "em") + driver.find_elements_by_tag_name("li") + driver.find_elements_by_tag_name("address") \
                 + driver.find_elements_by_tag_name("h1") + driver.find_elements_by_tag_name(
            "h2") + driver.find_elements_by_tag_name("h3") + driver.find_elements_by_tag_name(
            "h4") + driver.find_elements_by_tag_name("h5") \
                 + driver.find_elements_by_tag_name("h6") + driver.find_elements_by_tag_name(
            "a") + driver.find_elements_by_tag_name("strong") + driver.find_elements_by_tag_name("span")

        texts = []
        for p in all_ps:
            texts.append(p.text + "\n")

        ## CloudFare email getter
        if re.search('data-cfemail', str(soup)) is not None:
            email_code = re.search('data-cfemail="(.+?)"', str(soup)).group(1)
            email = str(decode_email(email_code))
        else:
            email = ""

        ## Metadata getter
        meta_property = soup.find("meta", property="og:description")
        meta_name = soup.find("meta", {"name": "description"})

        if meta_property is not None:
            meta_property = soup.find("meta", property="og:description")["content"]
        else:
            meta_property = ""
        if meta_name is not None:
            meta_name = soup.find("meta", {"name": "description"})["content"]
        else:
            meta_name = ""

        ## Div with class:address getter
        div_address = str(soup.find("div", {"class": 'address'}))
        if div_address is None:
            div_address = ""

        paragraf = "".join(texts)
        paragraf += meta_property + meta_name + email + div_address
        paragraf = paragraf.lower()
    except Exception as e:
        reset_browser()
        print(e)
        paragraf = ""

    return paragraf