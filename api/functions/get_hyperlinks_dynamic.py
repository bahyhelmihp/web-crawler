def get_hyperlinks_dynamic(url):
    global hyperlinks_dynamic, dynamic_links, dynamic_texts
    try:
        ## Do not gather (again) if has been gathered before
        if hyperlinks_dynamic == True:
            print("- Using previously gathered hyperlinks")
            links, texts = dynamic_links, dynamic_texts
        else:
            print("- Gathering hyperlinks dynamically")
            driver.set_page_load_timeout(60)
            driver.get(url)
            elems = driver.find_elements_by_xpath("//a[@href]")
            links = []
            texts = []
            for elem in elems:
                links.append(elem.get_attribute("href"))
                texts.append(elem.text)
            ## Set to true, collect hyperlinks
            hyperlinks_dynamic = True
            dynamic_links, dynamic_texts = links, texts
    except Exception as e:
        reset_browser()
        print(e)
        links, texts = [], []
    return links, texts