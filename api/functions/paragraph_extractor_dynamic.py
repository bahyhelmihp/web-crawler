def paragraf_extractor_dynamic(url):
    ''' Extract all paragraph (texts) found in a given dynamic page URL '''
    try:
        ## Send request
        print("- Extracting paragraphs dynamically")
        driver.set_page_load_timeout(60)
        driver.get(url)
        ## Parse content
        soup = bs(driver.page_source, 'html.parser')
        all_ps = driver.find_elements_by_tag_name("p") + driver.find_elements_by_tag_name("em") + driver.find_elements_by_tag_name("li") + driver.find_elements_by_tag_name("address") + driver.find_elements_by_tag_name("h1") + driver.find_elements_by_tag_name("h2") + driver.find_elements_by_tag_name("h3") + driver.find_elements_by_tag_name("h4") + driver.find_elements_by_tag_name("h5") + driver.find_elements_by_tag_name("h6") + driver.find_elements_by_tag_name("a") + driver.find_elements_by_tag_name("strong") + driver.find_elements_by_tag_name("span")

        ## Decode text
        texts = []
        for p in all_ps:
            texts.append(p.text + "\n")

        ## Implement CloudFare email getter

        ## Implement metadata getter

        ## Implement div with class:address getter

        ## Concat all texts founded
        
    except Exception as e:
        reset_browser()
        print(e)
        paragraf = ""

    return paragraf