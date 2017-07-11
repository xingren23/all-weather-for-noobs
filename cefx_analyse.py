# _*_ coding:utf8 _*_
# !/usr/bin/env python

import pandas as pd
import os
import numpy as np
from datetime import datetime

DATA_PATH = 'data/cef'

def cefx_merge(index, all_cefs_pd):

    cefx_quarters = pd.read_csv('%s/%s_QUARTER_SNAPSHOT.csv' % (DATA_PATH,index))
    cefx_quarters['Ticker'] = cefx_quarters['Ticker'].apply(lambda x: x[:x.find(" ")] if x.find(" ")>0 else x)
    cefx_quarters.index = cefx_quarters['Ticker']
    cefx_pd = pd.DataFrame()
    start_date = None
    end_date = None
    for date, quarter in cefx_quarters.groupby('Date'):
        if not start_date:
            start_date = date
        end_date = date
        quarter_pd = pd.DataFrame(quarter['Weight'])
        quarter_pd.columns = [datetime.strptime(date, '%Y-%m-%d')]
        cefx_pd = cefx_pd.append(quarter_pd.T)

    idx = pd.date_range(start_date, end_date)
    cefx_pd = cefx_pd.reindex(idx, method='ffill')
    cefx_pd = cefx_pd.fillna(0)
    # print cefx_pd

    day_groups = all_cefs_pd.groupby('DataDateJs')
    returns = []
    for time,row in cefx_pd.T.iteritems():
        date = time.strftime('%Y-%m-%d')
        if date in day_groups.groups.keys():
            day_pd = day_groups.get_group(date)
            day_pd.index = day_pd['TICKER']
            # print day_pd
            row_value = 0.0
            for symbol, weight in row.iteritems():
                if symbol in day_pd.index:
                    row_value += weight * day_pd.ix[symbol]['Percent']

            print date, row_value
            returns.append({'date': date, 'value': row_value})

    returns_pd = pd.DataFrame(returns)
    returns_pd.to_csv('%s/%s_MERGED_RETURNS.csv' % (DATA_PATH, index))


def merge_all():
    # load cefs history data
    all_cefs_pd = pd.DataFrame()
    all_files = [item for item in os.listdir(DATA_PATH) if item.endswith('_HISTORY.csv')]
    for item_file in all_files:
        data = pd.read_csv('%s/%s' % (DATA_PATH, item_file))
        data['Percent'] = data['Data'].pct_change()
        if item_file == 'ZF_HISTORY.csv':
            continue
        all_cefs_pd = all_cefs_pd.append(data[['DataDateJs', 'TICKER', 'Percent']]).fillna(0)

    indexes = [ 'CEFIGX', 'CEFOIX','CEFHYX', 'CEFBLX', 'CEFX']
    for index in indexes:
        print index, 'merge index returns.'
        cefx_merge(index, all_cefs_pd)
        # break

if __name__ == "__main__":
    merge_all()