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
nltk.download("stopwords")

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

    ## Remove whitspaces in URL
    url = url.strip()

    ## Adding schema
    if not url.lower().startswith("http") and not url.lower().startswith("https"):
        url = "http://" + url

    return url

def decode_email(e):
    de = ""
    k = int(e[:2], 16)

    for i in range(2, len(e)-1, 2):
        de += chr(int(e[i:i+2], 16)^k)

    return de

def get_hyperlinks(url):
    """Return all absolute hyperlinks within the home url"""

    print("Gathering hyperlinks...")
    base_url = url_format_handler(url)
    session = HTMLSession()
    try:
        r = session.get(base_url, headers = {'User-Agent': np.random.choice(user_agent_list)}, timeout=20)
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

def paragraf_extractor(url):
    try:
        page = requests.get(url, headers = {'User-Agent': np.random.choice(user_agent_list)}, timeout=20)
        soup = bs(page.content, 'html.parser')
        all_ps = soup.find_all("p") + soup.find_all("em") + soup.find_all("li") + soup.find_all("address")\
        + soup.find_all("h1") + soup.find_all("h2") + soup.find_all("h3") + soup.find_all("h4") + soup.find_all("h5")\
        + soup.find_all("h6") + soup.find_all("strong") + soup.find_all("a")

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

## Change this to your new training data
df = pd.read_csv("./datasets/df_cleaned.csv").iloc[:,1:]
df = df.drop_duplicates(subset='website')

rejected_websites = df[df.label == 'REJECTED'].website
approved_websites = df[df.label == 'APPROVED'].website

rejected_paragraphs = []
approved_paragraphs = []

# for i in range(len(rejected_websites)):
#     print("\n%s" % rejected_websites.values[i])
#     url = url_format_handler(rejected_websites.values[i])
#     rejected_paragraphs.append(paragraf_extractor(url))

# df_rejected = pd.DataFrame({'website': rejected_websites, 'paragraph': rejected_paragraphs})
# res_url = './datasets/rejected_paragraphs.csv'
# df_rejected.to_csv(res_url, index=False)

for i in range(len(approved_websites)):
    print("\n%s" % approved_websites.values[i])
    url = url_format_handler(approved_websites.values[i])
    approved_paragraphs.append(paragraf_extractor(url))

df_approved = pd.DataFrame({'website': approved_websites, 'paragraph': approved_paragraphs})
res_url = './datasets/approved_paragraphs.csv'
df_approved.to_csv(res_url, index=False)