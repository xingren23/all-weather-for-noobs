# _*_ coding:utf8 _*_
# !/usr/bin/env python
import requests
import pandas as pd
from modules.util import get_distribution, get_history

CEFX_DOWNLOAD_QUARTER_URL = 'http://www.closedendfundindex.com/indexdata/snapshots?'
CEFX_DOWNLOAD_RETURN_URL = 'http://www.closedendfundindex.com/indexdata/timeseries?mode=3&periodicity=1&currency=usd&all-dates=on'

def get_histories():
    cefs = pd.read_csv('data/cef/CEFConnect.csv')
    for key, item in cefs.iterrows():
        ticker = item['TICKER']
        res = get_history(ticker=ticker)
        if res.has_key('Success') and not res['Success']:
            print ticker, " get history error"
        elif len(res['Data']) > 0:
            dist_pd = pd.DataFrame(data=res['Data']['PriceHistory'])
            dist_pd['TICKER'] = item['TICKER']
            dist_pd['NAVTicker'] = res['Data']['NAVTicker']
            dist_pd['DataDateJs'] = dist_pd['DataDateJs'].str.replace("/", "-")
            dist_pd.to_csv('data/cef/%s_HISTORY.csv' % item['TICKER'])
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
            dist_pd.to_csv('data/cef/%s_DIST.csv' % item['TICKER'])
            distributions_pd = distributions_pd.append(dist_pd.ix[0])
            print ticker, " get history distribution."
        else:
            print ticker, " not found distribution."

    distributions_pd.to_csv('data/cef/ALL_CEFS_DIST.csv')

def download_index_returns():
    indexes = ['CEFOIX', 'CEFIGX', 'CEFHYX', 'CEFMX', 'CEFBLX', 'CEFX']
    for index in indexes:
        print index, ' download total returns.'
        url = '%s&index=%s' % (CEFX_DOWNLOAD_RETURN_URL, index)
        res = requests.get(url)
        lines = res.content.split('\n')
        arrays = [line.replace("\"","").split(',') for line in lines][1:]
        if len(arrays) > 1:
            returns_df = pd.DataFrame.from_records(arrays)
            returns_df.columns = ['Index', 'Currency', 'Date', 'Price', 'Total Return']
            returns_df.dropna().to_csv('data/cef/%s_RETURNS.csv' % index)


def download_all_quarter_snapshots():
    indexes = ['CEFOIX', 'CEFIGX', 'CEFHYX', 'CEFMX', 'CEFBLX', 'CEFX']
    all_quarters = ['2017-06-30','2017-03-31',
                '2016-12-30','2016-09-30','2016-06-30','2016-03-31',
                '2015-12-31','2015-10-01','2015-06-30','2015-03-31',
                '2014-12-31','2014-09-30','2014-06-30','2014-03-31',
                '2013-12-31','2013-09-30','2013-06-28','2013-03-29',
                '2012-12-31','2012-09-28','2012-06-29','2012-03-30',
                '2011-12-30','2011-09-30','2011-06-30','2011-04-01',
                '2010-12-17','2010-09-17','2010-06-18','2010-03-19',
                '2009-12-21','2009-09-21','2009-06-22','2009-03-23',
                '2008-12-22','2008-09-22','2008-06-23','2008-03-24',
                '2007-12-24','2007-09-24','2007-06-18','2007-03-20',
                '2006-12-18','2006-09-18','2006-06-19','2006-03-20',
                '2005-12-31']

    for index in indexes:
        result_df = pd.DataFrame()
        print index, " get quarter snapshot..."
        for quarter in all_quarters:
            url = '%sindex=%s&quarter=%s' % (CEFX_DOWNLOAD_QUARTER_URL, index, quarter)
            print 'download %s' % url
            res = requests.get(url)
            lines = res.content.split('\n')
            arrays = [line.replace("\"","").split(',') for line in lines][1:]
            if len(arrays) > 1:
                quarter_df = pd.DataFrame.from_records(arrays)
                quarter_df.columns = ['Ticker','Company','Country','Sector','Date','Weight']
                result_df = result_df.append(quarter_df.dropna())
            else:
                print index, ' has no more quarter data.'
                break
        result_df.to_csv('data/cef/%s_QUARTER_SNAPSHOT.csv' % index)

if __name__ == "__main__":
    # get_discributions()
    # get_histories()
    # download_all_quarter_snapshots()
    download_index_returns()
