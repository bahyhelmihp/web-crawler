# -------------------------------------------------------------------------------- NOTEBOOK-CELL: CODE
from gevent import monkey as curious_george
curious_george.patch_all(thread=False, select=False)

# -------------------------------------------------------------------------------- NOTEBOOK-CELL: CODE
# -*- coding: utf-8 -*-
from requests_html import HTMLSession
# import dataiku
# from dataiku import pandasutils as pdu
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
nltk.download("stopwords")

# # -------------------------------------------------------------------------------- NOTEBOOK-CELL: CODE
# # Read recipe inputs
# merchants = dataiku.Dataset("merchants")
# merchants_df = merchants.get_dataframe().drop("No", axis=1)

# -------------------------------------------------------------------------------- NOTEBOOK-CELL: CODE
# merchants_df = pd.read_excel("merchants.xlsx").drop("No", axis=1)

# -------------------------------------------------------------------------------- NOTEBOOK-CELL: CODE
# merchants_df

# -------------------------------------------------------------------------------- NOTEBOOK-CELL: MARKDOWN
# ### Pre-processing

# -------------------------------------------------------------------------------- NOTEBOOK-CELL: CODE
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

# -------------------------------------------------------------------------------- NOTEBOOK-CELL: CODE
def url_format_handler(url):
    """Return url with http/https prefix if not written"""

    if not url.startswith("http") and not url.startswith("https"):
        url = "http://" + url

    return url

def get_hyperlinks(url):
    """Return all absolute hyperlinks within the home url"""

    url = url_format_handler(url)
    session = HTMLSession()
    try:
        r = session.get(url, headers = {'User-Agent': np.random.choice(user_agent_list)})
        res = list(r.html.absolute_links)
        if len(res) == 0:
            res = [""]
    except:
        res = [""]

    return res

def decode_email(e):
    de = ""
    k = int(e[:2], 16)

    for i in range(2, len(e)-1, 2):
        de += chr(int(e[i:i+2], 16)^k)

    return de

# -------------------------------------------------------------------------------- NOTEBOOK-CELL: MARKDOWN
# ### Broken Link

# -------------------------------------------------------------------------------- NOTEBOOK-CELL: CODE
def broken_link_score(df, hyperlinks):
    """Return score (percentage) of broken link in a website"""

    if len(hyperlinks) > 10:
        hyperlinks = sample(hyperlinks, 10)
    rs = (grequests.get(x, headers = {'User-Agent': np.random.choice(user_agent_list)}) for x in hyperlinks)
    rs_res = grequests.map(rs, size = 10)

    status_not_ok = np.count_nonzero(np.array(rs_res, dtype=str) != '<Response [200]>')
    status_length = len(rs_res)

    try:
        score = status_not_ok/status_length*100
    except:
        score = 100

    res_df = pd.DataFrame({"merchant_name": df['Merchant Name'].values[0], "broken_link_score": score}, index=[0])

    return res_df

# -------------------------------------------------------------------------------- NOTEBOOK-CELL: CODE
def important_links_check(df, hyperlinks):
    """Return boolean of important links (contact, about, tnc) existance"""

    keyword_contact = ["contact", "kontak", "call"]
    keyword_about = ["about", "tentang"]
    keyword_tnc = ["terms", "term", "syarat", "ketentuan", "condition", \
                   "tnc", "kebijakan", "refund", "disclaimer", "policy", "prasyarat"]
    avoid = ["conditioner", "termurah", "termahal"]

    contact_mask = pd.Series(hyperlinks).str.contains('|'.join(keyword_contact)) \
    & ~pd.Series(hyperlinks).str.contains('|'.join(avoid))
    contact_count = 1 if np.count_nonzero(np.array(hyperlinks)[contact_mask]) >= 1 else 0

    about_mask = pd.Series(hyperlinks).str.contains('|'.join(keyword_about)) \
    & ~pd.Series(hyperlinks).str.contains('|'.join(avoid))
    about_count = 1 if np.count_nonzero(np.array(hyperlinks)[about_mask]) >= 1 else 0

    tnc_mask = pd.Series(hyperlinks).str.contains('|'.join(keyword_tnc)) \
    & ~pd.Series(hyperlinks).str.contains('|'.join(avoid))
    tnc_count = 1 if np.count_nonzero(np.array(hyperlinks)[tnc_mask]) >= 1 else 0

    res_df = pd.DataFrame({"merchant_name": df['Merchant Name'].values[0], "contact_us_exist": contact_count,\
                          "about_us_exist": about_count, "tnc_exist": tnc_count}, index=[0])

    return res_df

# -------------------------------------------------------------------------------- NOTEBOOK-CELL: MARKDOWN
# ### Contact Us Score

# -------------------------------------------------------------------------------- NOTEBOOK-CELL: CODE
def contact_us_score(df, hyperlinks):
    """Return score (percentage) of contact us component in a website"""

    keyword_contact = ["contact", "kontak", "call"]
    avoid = ["conditioner", "termurah", "termahal"]

    contact_mask = pd.Series(hyperlinks).str.contains('|'.join(keyword_contact)) \
    & ~pd.Series(hyperlinks).str.contains('|'.join(avoid))

    exists = [0,0]
    try:
        contact_link = pd.Series(hyperlinks)[contact_mask].values[0]

        page = requests.get(contact_link, headers = {'User-Agent': np.random.choice(user_agent_list)})
        soup = bs(page.content, 'html.parser')
        all_ps = soup.find_all("p")

        list_p = []
        for p in all_ps:
            list_p.append(unidecode.unidecode(p.getText()) + "\n")

        paragraf = "".join(list_p)

        ## If using CloudFare, email should be decrypted
        if re.search('data-cfemail', str(page.content)) is not None:
            email_code = re.search('data-cfemail="(.+?)"', str(page.content)).group(1)
            email = decode_email(email_code)
            paragraf = paragraf + str(email)

        email_match = re.search(r'[\w\.-]+@[\w\.-]+', paragraf)
        if email_match is not None:
            exists[0] = 1

        telephone_match = re.search(r'(\d{3}[-\.\s]??\d{3}[-\.\s]??\d{4}|\(\d{3}\)\s*\d{3}[-\.\s]??\d{4}|\d{3}[-\.\s]??\d{4})',\
                                   paragraf)
        if telephone_match is not None:
            exists[1] = 1

    except IndexError:
        exists = [0,0]

    score = np.count_nonzero(np.array(exists))/len(exists)*100
    res_df = pd.DataFrame({"merchant_name": df['Merchant Name'].values[0], "contact_us_score": score}, index=[0])

    return res_df

# -------------------------------------------------------------------------------- NOTEBOOK-CELL: MARKDOWN
# ### TnC Score

# -------------------------------------------------------------------------------- NOTEBOOK-CELL: CODE
def tnc_score(df, hyperlinks):
    """Return score (percentage) of tnc component in a website"""

    keyword_tnc = ["terms", "term", "syarat", "ketentuan", "condition", "tnc", "refund", "kebijakan"]
    avoid = ["conditioner", "termurah", "termahal"]

    tnc_mask = pd.Series(hyperlinks).str.contains('|'.join(keyword_tnc)) \
    & ~pd.Series(hyperlinks).str.contains('|'.join(avoid))

    try:
        tnc_link = pd.Series(hyperlinks)[tnc_mask].values[0]

        page = requests.get(tnc_link, headers = {'User-Agent': np.random.choice(user_agent_list)})
        soup = bs(page.content, 'html.parser')
        all_ps = soup.find_all("p") + soup.find_all("h3") + soup.find_all("h2")\
        + soup.find_all("h1") + soup.find_all("li")

        list_p = []
        for p in all_ps:
            list_p.append(unidecode.unidecode(p.getText()).lower() + "\n")

        paragraf = "".join(list_p)
        meta = soup.find("meta", property="og:description")
        if meta is not None:
            meta = soup.find("meta", property="og:description")["content"]
        else:
            meta = ""
        paragraf += meta

        lang = 'indonesian' if tb(paragraf).detect_language() == 'id' else 'english'
        tokenizer = RegexpTokenizer(r'\w+')
        words = tokenizer.tokenize(paragraf)
        stop_words = nltk.corpus.stopwords.words(lang)

        cleaned_words = []
        for word in words:
            if word not in stop_words:
                cleaned_words.append(word)

        mask = np.isin(['refunds', 'refund', 'refund policy', 'return', 'returns', 'return policy', \
                        'pengembalian', 'pengembalian dana', 'mengembalikan dana', 'dikembalikan', 'kembali',\
                        'pengembalian uang', 'mengembalikan', 'kembali'], words)

        score = 100 if np.count_nonzero(mask) > 0 else 0

    except:
        paragraf = ""
        score = 0

    res_df = pd.DataFrame({"merchant_name": df['Merchant Name'].values[0], "tnc_score": score}, index=[0])

    return res_df

# -------------------------------------------------------------------------------- NOTEBOOK-CELL: MARKDOWN
# ### Join All

# -------------------------------------------------------------------------------- NOTEBOOK-CELL: CODE
# merchants_df

# merchants_df = pd.read_excel("merchants.xlsx").drop("No", axis=1)
def orchestrator(url):

    df = pd.DataFrame({"Merchant Name": url, "Website": url}, index=[0])
    hyperlinks = get_hyperlinks(url)

    broken_df = broken_link_score(df, hyperlinks)
    important_df = important_links_check(df, hyperlinks)
    contact_df = contact_us_score(df, hyperlinks)
    tnc_df = tnc_score(df, hyperlinks)

    dfs = [broken_df, important_df, contact_df, tnc_df]
    dfs = [df.set_index("merchant_name") for df in dfs]
    res = pd.concat(dfs, axis=1).reset_index().to_dict('r')[0]
    res['total_score'] = 'null'

    return res
    

# -------------------------------------------------------------------------------- NOTEBOOK-CELL: CODE
# df_res = pd.DataFrame({"merchant_name": [], "broken_link_score": [], "contact_us_exist": [], "about_us_exist": [],\
#                        "tnc_exist": [], "contact_us_score": [], "tnc_score": []})

# for i in range(len(merchants_df)):
#     df = merchants_df.reset_index()
#     df = df[df.index == i]
#     url = df['Website'].values[0]
#     print(url)
#     hyperlinks = get_hyperlinks(url)

#     broken_df = broken_link_score(df, hyperlinks)
#     important_df = important_links_check(df, hyperlinks)
#     contact_df = contact_us_score(df, hyperlinks)
#     tnc_df = tnc_score(df, hyperlinks)

#     dfs = [broken_df, important_df, contact_df, tnc_df]
#     dfs = [df.set_index("merchant_name") for df in dfs]
#     res = pd.concat(dfs, axis=1).reset_index()

#     df_res = pd.concat([df_res, res])

# # -------------------------------------------------------------------------------- NOTEBOOK-CELL: CODE
# # Compute recipe outputs from inputs
# # TODO: Replace this part by your actual code that computes the output, as a Pandas dataframe
# # NB: DSS also supports other kinds of APIs for reading and writing data. Please see doc.

# features_output_df = df_res # For this sample code, simply copy input to output


# # Write recipe outputs
# features_output = dataiku.Dataset("features_output")
# features_output.write_with_schema(features_output_df)