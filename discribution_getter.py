# _*_ coding:utf8 _*_
# !/usr/bin/env python

import pandas as pd
from modules.util import get_distribution


def main():
    distributions_pd = pd.DataFrame()
    cefs = pd.read_csv('data/CEFConnect.csv')
    flag = False
    for key, item in cefs.iterrows():
        ticker = item['TICKER']
        res = get_distribution(ticker=ticker)
        if len(res['Data']) > 0:
            dist_pd = pd.DataFrame(data=res['Data'])
            dist_pd['TICKER'] = item['TICKER']
            dist_pd.to_csv('data/barchart/cef/%s_DIST.csv' % item['TICKER'])
            distributions_pd = distributions_pd.append(dist_pd.ix[0])
            print item['TICKER'], " get history distribution."
        else:
            print item['TICKER'], " not found distribution."

    distributions_pd.to_csv('data/barchart/cef/ALL_CEFS_DIST.csv')

if __name__ == "__main__":
    main()
