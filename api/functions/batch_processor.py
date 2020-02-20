from gevent import monkey
monkey.patch_all()
import pandas as pd
import flask
from functions.base_functions import *
import sys, os
import logging
import time
import datetime

def batch_process(url, start, end, name):
    """Function to batch process crawling function
    Input: CSV URL, index to read, output file name
    Output: CSV Results"""

    batch_start_time = datetime.datetime.now()
    input_df = pd.read_csv(url)
    if start == 0 and end == 0:
        end = len(input_df)
    
    df_res = pd.DataFrame({"merchant_name": [], "broken_link_score": [], "link_contact_us_exist": [], \
            "cu_email_exist": [], "cu_phone_number_exist": [], "link_about_us_exist": [],\
            "link_tnc_exist": [], "tnc_refund_policy_exist": [], "contact_us_score": [], \
            "tnc_score": [], "broken_links": [], "website": [], "label": []})
    
    input_df = input_df.reset_index()
    try:
        for i in range(start, end):
            start_time = time.time()
            df = input_df[input_df.index == i]  
            url = str(df['website'].values[0])
            
            print(url + " --> " + str(i+1-start))
            logging.info(url + " --> " + str(i+1-start))
            
            hyperlinks = get_hyperlinks(url)
            ## Recheck Hyperlinks
            if len(hyperlinks) == 0:
                hyperlinks = get_hyperlinks(url)
            broken_df = broken_link_score(df, hyperlinks)
            ## Recheck Broken Links
            if broken_df['broken_link_score'].values[0] == 100:
                broken_df = broken_link_score(df, hyperlinks)
            important_df = important_links_check(df, hyperlinks)
            contact_df = contact_us_score(df, hyperlinks)
            tnc_df = tnc_score(df, hyperlinks)

            dfs = [broken_df, important_df, contact_df, tnc_df]
            dfs = [df.set_index("merchant_name") for df in dfs]
            res = pd.concat(dfs, axis=1, sort=False).reset_index()
            res['label'] = df['label'].values[0]
            res['website'] = df['website'].values[0]

            df_res = pd.concat([df_res, res], sort=False)
            res_url = './datasets/' + name + '.csv'
            df_res.to_csv(res_url)
            print("--- Time taken: %s seconds ---\n" % (time.time() - start_time))

        print("--- Start Batch: %s ---" % batch_start_time.strftime("%Y-%m-%d %H:%M:%S"))
        print("--- End Batch: %s ---" % datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        return str(i+1-start) + " line(s) successfully written."
    except:
        res_url = './datasets/' + name + '.csv'
        df_res.to_csv(res_url)
        print("--- Start Batch: %s ---" % batch_start_time.strftime("%Y-%m-%d %H:%M:%S"))
        print("--- End Batch: %s ---" % datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        return "Error occured. " + str(i+1-start-1) + " line(s) successfully written."   