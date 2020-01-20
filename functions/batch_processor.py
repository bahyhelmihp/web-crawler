import pandas as pd
import sys, os
from functions.base_functions import *
sys.path.append(os.path.abspath(os.path.join('..', 'web-crawler')))

def batch_process(url, line):
    df = pd.read_csv(url)
    if line == 0:
        row_processed = len(df)
    else:
        row_processed = line
    df_res = pd.DataFrame({"merchant_name": [], "broken_link_score": [], "link_contact_us_exist": [], \
            "cu_email_exist": [], "cu_phone_number_exist": [], "link_about_us_exist": [],\
            "link_tnc_exist": [], "tnc_refund_policy_exist": [], "contact_us_score": [], \
            "tnc_score": [], "label": []})
    for i in range(row_processed):
        df = df.reset_index()
        df = df[df.index == i]
        url = df['website'].values[0]
        print(url)
        hyperlinks = get_hyperlinks(url)

        broken_df = broken_link_score(df, hyperlinks)
        important_df = important_links_check(df, hyperlinks)
        contact_df = contact_us_score(df, hyperlinks)
        tnc_df = tnc_score(df, hyperlinks)

        dfs = [broken_df, important_df, contact_df, tnc_df]
        dfs = [df.set_index("merchant_name") for df in dfs]
        res = pd.concat(dfs, axis=1, sort=False).reset_index()
        res['label'] = df['label'].values[0]

        df_res = pd.concat([df_res, res], sort=False)


    res_url = 'datasets/results.csv'
    df_res.to_csv(res_url)
    return "File successfully written"