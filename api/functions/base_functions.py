from gevent import monkey
monkey.patch_all()
from requests_html import HTMLSession
import pandas as pd
from bs4 import BeautifulSoup as bs
import grequests
import requests
import datetime
import numpy as np
import unidecode
from textblob import TextBlob as tb
import re
from nltk.tokenize import word_tokenize, RegexpTokenizer
import nltk
from random import sample
from flask import request, jsonify
from selenium import webdriver
import time
import json
from selenium.common.exceptions import TimeoutException
import urllib3
nltk.download("stopwords")
urllib3.disable_warnings()

user_agent_list = [

    #Chrome
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36',
    'Mozilla/5.0 (Windows NT 5.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36',

    #Firefox
    'Mozilla/4.0 (compatible; MSIE 9.0; Windows NT 6.1)',
    'Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko',
    'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0)',
    'Mozilla/5.0 (Windows NT 6.1; Trident/7.0; rv:11.0) like Gecko',
    'Mozilla/5.0 (Windows NT 6.2; WOW64; Trident/7.0; rv:11.0) like Gecko',
    'Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko',
    'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.0; Trident/5.0)',
    'Mozilla/5.0 (Windows NT 6.3; WOW64; Trident/7.0; rv:11.0) like Gecko',
    'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0)',
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64; Trident/7.0; rv:11.0) like Gecko',
    'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; WOW64; Trident/6.0)',
    'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; Trident/6.0)',
    'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; .NET CLR 2.0.50727; .NET CLR 3.0.4506.2152; .NET CLR 3.5.30729)'
]

driver = webdriver.Chrome()
hyperlinks_dynamic = False
dynamic_links = []
dynamic_texts = []
    
def reset_browser():
    global driver
    global hyperlinks_dynamic
    global dynamic_links
    global dynamic_texts

    ## Quit driver
    driver.close()
    driver.quit()

    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--ignore-certificate-errors')

    driver = webdriver.Chrome(chrome_options=chrome_options)    
    hyperlinks_dynamic = False
    dynamic_links = []
    dynamic_texts = []

def url_format_handler(url):
    """Return url with http/https prefix if not written"""

    ## Remove whitspaces in URL
    url = url.strip()

    ## Adding schema
    ## Change all URL without schema to https
    if not url.lower().startswith("http") and not url.lower().startswith("https"):  ## no http/https
        url = "https://" + url.lower()
    ## Change all http URL to https
    if url.lower().startswith("http") and not url.lower().startswith("https"):  ## no https
        url = "https://" + url.lower().split("http://")[1]
    ## Remove backslash at the end of url
    if url.endswith("/"):
        url = url.lower()[:-1]

    return url

def get_hyperlinks(url):
    """Return all absolute hyperlinks within the home url"""

    print("Gathering hyperlinks...")
    base_url = url_format_handler(url)
    session = HTMLSession()
    try:
        r = session.get(base_url, headers = {'User-Agent': np.random.choice(user_agent_list)}, timeout=30, verify=False)
        res = list(r.html.absolute_links)
        
        ## If r-html anchor failed, concate manually
        res_final = [""]
        for url in res:
            if not str(url).startswith("http"):  
                res_final.append(str(base_url + url))
            else:
                res_final.append(str(url))

        ## Check if domain expired/redirects
        domain = base_url.split("//")[1]
        if any(domain in url for url in res_final):
            pass
        else:
            res_final = [""]

        ## If website does not return hyperlink
        if len(res) == 0 or len(res_final) == 0:
            res = [""]
        else:
            res = res_final
        
    except Exception as e:
        print(e)
        res = [""]

    print("Hyperlinks gathered.\n")

    return res

def get_hyperlinks_dynamic(url):
    global hyperlinks_dynamic
    global dynamic_links
    global dynamic_texts

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
            dynamic_links = links
            dynamic_texts = texts
    except Exception as e:
        reset_browser()
        print(e)
        links = []
        texts = []

    return links, texts

def decode_email(e):
    de = ""
    k = int(e[:2], 16)

    for i in range(2, len(e)-1, 2):
        de += chr(int(e[i:i+2], 16)^k)

    return de

def email_matcher(paragraf):
    email_match = re.search(r'[\w\.-]+(@|\[at])[\w\.-]+', paragraf)

    if email_match is not None:
        print("Email: %s" % email_match.group(0))
        return 1
    else:
        return 0

def telephone_matcher(paragraf):
    telephone_match = re.search(r'(\d{3,5}[-\.\s]??\d{3,5}[-\.\s]??\d{3,5}|\(\d{3,5}\)\s*\d{3,5}[-\.\s]??\d{3,5}|\d{3,5}[-\.\s]??\d{3,5})',\
                                   paragraf)
    if telephone_match is not None:
        print("Phone Number: %s" % telephone_match.group(0))
        return 1
    else:
        return 0

def refund_policy_matcher(paragraf):
    keyword_refund = ['refunds', 'refund', 'refund policy', 'return', 'returns', 'return policy', \
                            'pengembalian', 'pengembalian dana', 'mengembalikan dana', 'dikembalikan', 'kembali',\
                            'pengembalian uang', 'mengembalikan', 'retur', 'tukar', 'penukaran']
    
    ## Tokenizing & cleaning paragraf into words
    try:
        lang = 'indonesian' if tb(paragraf).detect_language() == 'id' else 'english'
        tokenizer = RegexpTokenizer(r'\w+')
        words = tokenizer.tokenize(paragraf)
        stop_words = nltk.corpus.stopwords.words(lang)

        cleaned_words = []
        for word in words:
            if word not in stop_words:
                cleaned_words.append(word)
    except Exception as e:
        print(e)
        cleaned_words = ""

    mask = pd.Series(cleaned_words).str.contains("|".join(keyword_refund))

    count_refund = np.count_nonzero(mask)
    if count_refund > 0:
        return 1           
    else:
        return 0

def paragraf_extractor(url):
    try:
        page = requests.get(url, headers = {'User-Agent': np.random.choice(user_agent_list)}, timeout=30, verify=False)
        soup = bs(page.content, 'html.parser')
        all_ps = soup.find_all("p") + soup.find_all("em") + soup.find_all("li") + soup.find_all("address")\
        + soup.find_all("h1") + soup.find_all("h2") + soup.find_all("h3") + soup.find_all("h4") + soup.find_all("h5")\
        + soup.find_all("h6") + soup.find_all("a") + soup.find_all("strong")

        ## CloudFare Email Getter
        if re.search('data-cfemail', str(soup)) is not None:
            email_code = re.search('data-cfemail="(.+?)"', str(soup)).group(1)
            email = str(decode_email(email_code))
        else:
            email = ""

        ## Meta Getter
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

        ## Div Address Getter
        div_address = str(soup.find("div", {"class":'address'}))
        if div_address is None:
            div_address = ""

        list_p = []
        for p in all_ps:
            list_p.append(unidecode.unidecode(p.getText()) + "\n")

        paragraf = "".join(list_p)
        paragraf += meta_property + meta_name + email + div_address
        paragraf = paragraf.lower()
    except Exception as e:
        print(e)
        paragraf = ""

    return paragraf

def paragraf_extractor_dynamic(url):
    try:
        print("- Extracting paragraphs dynamically")
        driver.set_page_load_timeout(60)
        driver.get(url)
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

        ## CloudFare Email Getter
        if re.search('data-cfemail', str(soup)) is not None:
            email_code = re.search('data-cfemail="(.+?)"', str(soup)).group(1)
            email = str(decode_email(email_code))
        else:
            email = ""

        ## Meta Getter
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

        ## Div Address Getter
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

def about_us_check(df, hyperlinks):
    """Return boolean of about us link existance"""

    print("Checking about us...")
    keyword_about = ["about", "tentang"]
    avoid = ["conditioner", "termurah", "termahal", "expired", "expire", "renewal"]

    about_mask = pd.Series(hyperlinks).str.lower().str.contains('|'.join(keyword_about)) \
                 & ~pd.Series(hyperlinks).str.lower().str.contains('|'.join(avoid))
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

    res_df = pd.DataFrame({"merchant_name": df['merchant_name'].values[0], "link_about_us_exist": int(about_count)},
                          index=[0])

    print("About us checked.\n")

    return res_df

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

def tnc_score(df, hyperlinks):
    """Return score (percentage) of tnc component in a website"""

    print("Checking TnC...")
    keyword_tnc = ["terms", "term", "syarat", "ketentuan", "condition", \
                   "tnc", "kebijakan", "refund", "disclaimer", "policy", "prasyarat", \
                   "agreement", "exchange", "return", "retur", "tukar", "faq", "aturan", \
                   "pengembalian", "penukaran", "perjanjian"]
    avoid = ["conditioner", "termurah", "termahal", "expired", "expire", "renewal"]

    tnc_mask = pd.Series(hyperlinks).str.lower().str.contains('|'.join(keyword_tnc)) \
               & ~pd.Series(hyperlinks).str.lower().str.contains('|'.join(avoid))

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

def run_crawler(url):

    start_time = time.time()
    print("\n--- " + url + " ---")
    df = pd.DataFrame({"merchant_name": url, "website": url}, index=[0])
    hyperlinks = get_hyperlinks(url)
    if len(hyperlinks) == 0:
        hyperlinks = get_hyperlinks_dynamic(url)

    broken_df = broken_link_score(df, hyperlinks)
    if broken_df['broken_link_score'].values[0] == 1:
                broken_df = broken_link_score(df, hyperlinks)

    about_df = about_us_check(df, hyperlinks)
    contact_df = contact_us_score(df, hyperlinks)
    tnc_df = tnc_score(df, hyperlinks)

    dfs = [broken_df, about_df, contact_df, tnc_df]
    dfs = [df.set_index("merchant_name") for df in dfs]
    features = pd.concat(dfs, axis=1).reset_index().to_dict('r')[0]
    print("--- Time taken: %s seconds ---\n" % (time.time() - start_time))
    res = calculate_score(features).to_dict('r')[0]
    reset_browser()

    return res
