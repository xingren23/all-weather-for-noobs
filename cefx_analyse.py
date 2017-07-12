# _*_ coding:utf8 _*_
# !/usr/bin/env python

import pandas as pd
import os
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

    print index, 'merge index returns.'
    day_groups = all_cefs_pd.groupby('DataDateJs')
    returns = []
    for time,row in cefx_pd.T.iteritems():
        date = time.strftime('%Y-%m-%d')
        if date in day_groups.groups.keys():
            day_pd = day_groups.get_group(date)

            discount_value, full_discount_value = cal_row_value(date, row, day_pd, 'discount')
            preminum_value, full_preminum_value = cal_row_value(date, row, day_pd, 'preminum')
            row_value, full_value = cal_row_value(date, row, day_pd, '')
            print date, row_value, discount_value, preminum_value
            returns.append({'date': date,
                            'value': row_value, 'full_value': full_value,
                            'preminum_value': preminum_value, 'full_preminum_value': full_preminum_value,
                            'discount_value':discount_value, 'full_discount_value':full_discount_value})

    returns_pd = pd.DataFrame(returns)
    returns_pd.to_csv('%s/%s_MERGED_RETURNS.csv' % (DATA_PATH, index))


def cal_row_value(date, row, day_pd, sort):
    if sort == 'discount':
        day_pd.sort_values(by='DiscountData',ascending=True, inplace=True)
        day_pd = day_pd.head(int(0.3*len(day_pd)))
    elif sort == 'preminum':
        day_pd.sort_values(by='DiscountData',ascending=False, inplace=True)
        day_pd = day_pd.head(int(0.3*len(day_pd)))

    day_pd.index = day_pd['TICKER']

    # print day_pd
    row_value = 0.0
    full_value = 0.0
    row_weight = 0.001
    for symbol, weight in row.iteritems():
        if symbol in day_pd.index:
            if date == '2016-11-18' and symbol == 'DSU':
                continue
            #     print sort, symbol, weight, day_pd.ix[symbol]['Percent']
            row_value += weight * day_pd.ix[symbol]['Percent']
            full_value += weight * day_pd.ix[symbol]['Adj_Percent']
            row_weight += weight

    row_value *= 1.0 / row_weight
    full_value *= 1.0 / row_weight
    return row_value, full_value


def merge_all():
    # load cefs history data
    all_cefs_pd = pd.DataFrame()
    all_files = [item for item in os.listdir(DATA_PATH) if item.endswith('_YAHOO_HISTORY.csv')]
    for item_file in all_files:

        symbol = item_file[:item_file.find("_")]
        data = pd.read_csv('%s/%s_HISTORY.csv' % (DATA_PATH, symbol))
        data.index = data['DataDateJs']
        yahoo_data = pd.read_csv('%s/%s_YAHOO_HISTORY.csv' % (DATA_PATH, symbol), index_col = 'Date')
        yahoo_data = yahoo_data.ix[data.index]
        data['Adj_Percent'] = yahoo_data['Adj Close'].astype(float).pct_change() * 100
        data['Percent'] = yahoo_data['Close'].astype(float).pct_change() * 100

        if symbol == 'BGX':
            continue
        data = data.reset_index(drop=True)
        all_cefs_pd = all_cefs_pd.append(data[['DataDateJs', 'TICKER', 'Percent', 'DiscountData', 'Adj_Percent']]).fillna(0)


    indexes = [ 'CEFIGX', 'CEFOIX','CEFHYX', 'CEFBLX', 'CEFX']
    # indexes = ['CEFHYX']
    for index in indexes:
        cefx_merge(index, all_cefs_pd)
        # break

if __name__ == "__main__":
    merge_all()