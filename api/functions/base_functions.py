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
nltk.download("stopwords")

driver = webdriver.Chrome()
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

def url_format_handler(url):
    """Return url with http/https prefix if not written"""

    if not url.startswith("http") and not url.startswith("https"):
        url = "http://" + url

    return url

def get_hyperlinks(url):
    """Return all absolute hyperlinks within the home url"""

    print("Gathering hyperlinks...")
    base_url = url_format_handler(url)
    session = HTMLSession()
    try:
        r = session.get(base_url, headers = {'User-Agent': np.random.choice(user_agent_list)}, timeout=15)
        res = list(r.html.absolute_links)
        
        ## If r-html anchor failed, concate manually
        res_final = [""]
        for url in res:
            if not str(url).startswith("http"):  
                res_final.append(str(base_url + url))
            else:
                res_final.append(str(url))

        if len(res) == 0 or len(res_final) == 0:
            res = [""]
        else:
            res = res_final

        ## Catching expired domain websites
        if len(r.history) > 0:
            for response in r.history:
                if str(response) == '<Response [302]>':
                    res = [""]
    except:
        res = [""]

    print("Hyperlinks gathered.\n")

    return res

def get_hyperlinks_dynamic(url):
    try:
        print("- Gathering hyperlinks dynamically")
        driver.set_page_load_timeout(20)
        driver.get(url)
        soup = bs(driver.page_source, 'html.parser')
        links = soup.find_all("a")
    except:
        links = []

    return links

def decode_email(e):
    de = ""
    k = int(e[:2], 16)

    for i in range(2, len(e)-1, 2):
        de += chr(int(e[i:i+2], 16)^k)

    return de

def email_matcher(paragraf):
    email_match = re.search(r'[\w\.-]+(@|\[at])[\w\.-]+', paragraf)

    if email_match is not None:
        return 1
    else:
        return 0

def telephone_matcher(paragraf):
    telephone_match = re.search(r'(\d{3,5}[-\.\s]??\d{3,5}[-\.\s]??\d{3,5}|\(\d{3,5}\)\s*\d{3,5}[-\.\s]??\d{3,5}|\d{3,5}[-\.\s]??\d{3,5})',\
                                   paragraf)
    if telephone_match is not None:
        return 1
    else:
        return 0

def refund_policy_matcher(paragraf):
    keyword_refund = ['refunds', 'refund', 'refund policy', 'return', 'returns', 'return policy', \
                            'pengembalian', 'pengembalian dana', 'mengembalikan dana', 'dikembalikan', 'kembali',\
                            'pengembalian uang', 'mengembalikan', 'retur', 'tukar', 'penukaran']
    try:
        lang = 'indonesian' if tb(paragraf).detect_language() == 'id' else 'english'
        tokenizer = RegexpTokenizer(r'\w+')
        words = tokenizer.tokenize(paragraf)
        stop_words = nltk.corpus.stopwords.words(lang)

        cleaned_words = []
        for word in words:
            if word not in stop_words:
                cleaned_words.append(word)
    except:
        cleaned_words = ""

    mask = pd.Series(cleaned_words).str.contains("|".join(keyword_refund))

    count_refund = np.count_nonzero(mask)
    if count_refund > 0:
        return 1           
    else:
        return 0

def paragraf_extractor(url):
    try:
        page = requests.get(url, headers = {'User-Agent': np.random.choice(user_agent_list)}, timeout=15)
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
            if not re.search('<div', str(p)):
                list_p.append(unidecode.unidecode(p.getText()) + "\n")

        paragraf = "".join(list_p)
        paragraf += meta_property + meta_name + email + div_address
        paragraf = paragraf.lower()
    except:
        paragraf = ""

    return paragraf

def paragraf_extractor_dynamic(url):
    try:
        print("- Extracting paragraphs dynamically")
        driver.set_page_load_timeout(20)
        driver.get(url)
        soup = bs(driver.page_source, 'html.parser')
        all_ps = soup.find_all("p") + soup.find_all("em") + soup.find_all("li") + soup.find_all("address")\
        + soup.find_all("h1") + soup.find_all("h2") + soup.find_all("h3") + soup.find_all("h4") + soup.find_all("h5")\
        + soup.find_all("h6") + soup.find_all("a") + soup.find_all("strong")

        list_p = []
        for p in all_ps:
            if not re.search('<div', str(p)):
                list_p.append(unidecode.unidecode(p.getText()) + "\n")

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

        paragraf = "".join(list_p)
        paragraf += meta_property + meta_name + email + div_address
        paragraf = paragraf.lower()
    except:
        paragraf = ""

    return paragraf

def broken_link_score(df, hyperlinks):
    """Return score (percentage) of broken link in a website"""

    print("Checking broken link...")
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
    if len(hyperlinks) > 10:
        hyperlinks = sample(hyperlinks, 10)
    rs = (grequests.get(x, \
        headers = {}, \
        timeout=15) for x in hyperlinks)
    rs_res = grequests.map(rs, size = 3)
    
    links = {}
    i = 0
    if len(hyperlinks) == 1 and hyperlinks[0] == "":
        links = "No hyperlinks gathered"
    else:
        for response in rs_res:
            try:
                links[response.request.url] = str(response)
            except:
                links[hyperlinks[i]] = 'No Response/Timeout'
            i += 1

    status_not_ok = np.count_nonzero(np.array(rs_res, dtype=str) != '<Response [200]>')
    status_length = len(rs_res)

    try:
        score = status_not_ok/status_length*100
    except:
        score = 100

    res_df = pd.DataFrame({"merchant_name": df['merchant_name'].values[0], "broken_link_score": score,\
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
    
    ## Check for inexact link
    try:
        if about_count < 1:
           base_url = str(df['website'].values[0])
           links = get_hyperlinks_dynamic(url_format_handler(base_url))
           if len(links) > 0:
               for a in links:
                    ## About Us Link Finder
                    if pd.Series(str(a)).str.lower().str.contains('|'.join(keyword_about)).any():
                        about_count = 1
    except:
        pass

    res_df = pd.DataFrame({"merchant_name": df['merchant_name'].values[0], "link_about_us_exist": int(about_count)}, index=[0])

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
    exists = [0,0,0]
        
    try:
        contact_links = list(pd.Series(hyperlinks)[contact_mask].values)
    except:
        contact_links = []
    
    ## Check on all contact links
    if len(contact_links) > 0:
        for link in contact_links:
            paragraf = paragraf_extractor(link)

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
       links = get_hyperlinks_dynamic(url_format_handler(base_url))
       if len(links) > 0:
           for a in links:
                ## Contact Link Filtering
                if pd.Series(str(a)).str.lower().str.contains('|'.join(keyword_contact)).any():
                    print("Got you:"  + str(a))
                    try:
                        link = base_url + "/" + a['href']
                        exists[2] = 1

                        ## Search for cu features
                        paragraf = paragraf_extractor_dynamic(url_format_handler(link))
                        print(paragraf)
                        exists[0] = 1 if email_matcher(paragraf) == 1 else exists[0]
                        exists[1] = 1 if telephone_matcher(paragraf) == 1 else exists[1]
                    except:
                        print("Asup except")
                        continue

    score = np.count_nonzero(np.array(exists))/len(exists)*100

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
    except:
        tnc_links = []

    ## Refund Policy, Link
    exists = [0,0]

    if len(tnc_links) > 0:
        exists[1] = 1
        ## Check on all tnc links
        for link in tnc_links:
            paragraf = paragraf_extractor(link)
            exists[0] = refund_policy_matcher(paragraf)

    ## Check refund policy on HomePage
    if exists[0] == 0:
        base_url = str(df['website'].values[0])
        paragraf = paragraf_extractor(url_format_handler(base_url))
        exists[0] = refund_policy_matcher(paragraf)

    ## Try dynamic crawling if website cannot detect tnc link / refund policy
    if (len(tnc_links) == 0 | exists[0] == 0) and len(hyperlinks) != 0:
       ## Find Inexact TnC Link
       base_url = str(df['website'].values[0])
       links = get_hyperlinks_dynamic(url_format_handler(base_url))
       if len(links) > 0:
           for a in links:
                ## TnC Link Filtering
                if (pd.Series(str(a)).str.lower().str.contains('|'.join(keyword_tnc)) \
                    & ~pd.Series(str(a)).str.lower().str.contains('|'.join(avoid))).any():
                    try:
                        link = base_url + "/" + a['href']
                        exists[1] = 1

                        ## Search for refund_policy features
                        paragraf = paragraf_extractor_dynamic(url_format_handler(link))
                        exists[0] = refund_policy_matcher(paragraf)
                    except:
                        continue

    score = np.count_nonzero(np.array(exists))/len(exists)*100

    res_df = pd.DataFrame({"merchant_name": df['merchant_name'].values[0], "tnc_score": score, \
                           "tnc_refund_policy_exist": int(exists[0]), "link_tnc_exist": int(exists[1])}, index=[0])

    print("TnC checked.\n")

    return res_df

def orchestrator(url):

    start_time = time.time()
    print("\n--- " + url + " ---")
    df = pd.DataFrame({"merchant_name": url, "website": url}, index=[0])
    hyperlinks = get_hyperlinks(url)
    if len(hyperlinks) == 0:
        hyperlinks = get_hyperlinks(url)

    broken_df = broken_link_score(df, hyperlinks)
    if broken_df['broken_link_score'].values[0] == 100:
                broken_df = broken_link_score(df, hyperlinks)

    about_df = about_us_check(df, hyperlinks)
    contact_df = contact_us_score(df, hyperlinks)
    tnc_df = tnc_score(df, hyperlinks)

    dfs = [broken_df, about_df, contact_df, tnc_df]
    dfs = [df.set_index("merchant_name") for df in dfs]
    res = pd.concat(dfs, axis=1).reset_index().to_dict('r')[0]
    res['total_score'] = 'null'
    print("--- Time taken: %s seconds ---" % (time.time() - start_time))

    return res