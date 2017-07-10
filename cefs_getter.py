# _*_ coding:utf8 _*_
# !/usr/bin/env python

import pandas as pd
from modules.util import get_distribution, get_history


def get_histories():
    cefs = pd.read_csv('data/CEFConnect.csv')
    for key, item in cefs.iterrows():
        ticker = item['TICKER']
        res = get_history(ticker=ticker)
        if res.has_key('Success') and not res['Success']:
            print ticker, " get history error"
        elif len(res['Data']) > 0:
            dist_pd = pd.DataFrame(data=res['Data'])
            dist_pd['TICKER'] = item['TICKER']
            dist_pd.to_csv('data/barchart/cef/%s_HISTORY.csv' % item['TICKER'])
            print item['TICKER'], " get history."
        else:
            print ticker, " not found history."


def get_discributions():
    distributions_pd = pd.DataFrame()
    cefs = pd.read_csv('data/CEFConnect.csv')
    for key, item in cefs.iterrows():
        ticker = item['TICKER']
        res = get_distribution(ticker=ticker)
        if len(res['Data']) > 0:
            dist_pd = pd.DataFrame(data=res['Data'])
            dist_pd['TICKER'] = ticker
            dist_pd.to_csv('data/barchart/cef/%s_DIST.csv' % item['TICKER'])
            distributions_pd = distributions_pd.append(dist_pd.ix[0])
            print ticker, " get history distribution."
        else:
            print ticker, " not found distribution."

    distributions_pd.to_csv('data/barchart/cef/ALL_CEFS_DIST.csv')

if __name__ == "__main__":
    get_discributions()
    # get_histories()
