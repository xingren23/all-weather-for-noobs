# _*_ coding:utf8 _*_
# !/usr/bin/env python

import requests
import pandas as pd


CEFX_DOWNLOAD_QUARTER_URL = 'http://www.closedendfundindex.com/indexdata/snapshots?index=CEFX'
def download_all_quarter_snapshots():
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

    result_df = pd.DataFrame()
    for quarter in all_quarters:
        url = '%s&quarter=%s' % (CEFX_DOWNLOAD_QUARTER_URL, quarter)
        print 'download %s' % url
        res = requests.get(url)
        lines = res.content.split('\n')
        arrays = [line.replace("\"","").split(',') for line in lines][1:]
        quarter_df = pd.DataFrame.from_records(arrays)
        quarter_df.columns = ['Ticker','Company','Country','Sector','Date','Weight']
        result_df = result_df.append(quarter_df.dropna())
    result_df.to_csv('data/cef/CEFX_QUARTER_SNAPSHOT.csv')

if __name__ == "__main__":
    download_all_quarter_snapshots()