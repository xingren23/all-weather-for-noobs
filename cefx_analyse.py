# _*_ coding:utf8 _*_
# !/usr/bin/env python

import pandas as pd
import os
from datetime import datetime

DATA_PATH = 'data/cef'

def cefx_merge(index, all_cefs_pd, adjusted):

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
            day_pd.index = day_pd['TICKER']

            discount_value, full_discount_value = cal_row_value(date, row, day_pd, 'discount', adjusted)
            preminum_value, full_preminum_value = cal_row_value(date, row, day_pd, 'preminum', adjusted)
            row_value, full_value = cal_row_value(date, row, day_pd, '', adjusted)
            print date, row_value, discount_value, preminum_value
            returns.append({'date': date,
                            'value': row_value, 'full_value': full_value,
                            'preminum_value': preminum_value, 'full_preminum_value': full_preminum_value,
                            'discount_value':discount_value, 'full_discount_value':full_discount_value})


    returns_pd = pd.DataFrame(returns)
    if adjusted:
        returns_pd.to_csv('%s/%s_ADJUSTED_MERGED_RETURNS.csv' % (DATA_PATH, index))
    else:
        returns_pd.to_csv('%s/%s_MERGED_RETURNS.csv' % (DATA_PATH, index))


def cal_row_value(date, row, day_pd, sort, adjusted):
    if sort == 'discount':
        data_pd = day_pd.ix[row.index].sort_values(by='DiscountData',ascending=True).dropna()
        data_pd = data_pd.head(int(0.3*len(data_pd)))
    elif sort == 'preminum':
        data_pd = day_pd.ix[row.index].sort_values(by='DiscountData',ascending=False).dropna()
        data_pd = data_pd.head(int(0.3*len(data_pd)))
    else:
        data_pd = day_pd.ix[row.index].dropna()

    # print day_pd
    row_value = 0.0
    full_value = 0.0
    row_weight = 0.001
    for symbol, weight in row.iteritems():
        if symbol in data_pd.index:
            row_value += weight * data_pd.ix[symbol]['Percent']
            if adjusted:
                full_value += weight * data_pd.ix[symbol]['Adj_Percent']
            row_weight += weight

    row_value *= 100.0 / row_weight
    full_value *= 100.0 / row_weight
    return row_value, full_value


def merge_all(adjusted=False):
    # load cefs history data
    all_cefs_pd = pd.DataFrame()
    all_files = [item for item in os.listdir(DATA_PATH) if item.endswith('_YAHOO_HISTORY.csv')]
    for item_file in all_files:

        symbol = item_file[:item_file.find("_")]
        if symbol == 'BGX':
            continue
        data = pd.read_csv('%s/%s_HISTORY.csv' % (DATA_PATH, symbol))
        data.index = data['DataDateJs']
        if adjusted:
            # yahoo_history 是日净值 -> 转换为周净值
            yahoo_data = pd.read_csv('%s/%s_YAHOO_HISTORY.csv' % (DATA_PATH, symbol), index_col = 'Date')
            yahoo_data = yahoo_data.ix[data.index]
            data['Adj_Percent'] = yahoo_data['Adj Close'].astype(float).pct_change(5)
            data['Percent'] = yahoo_data['Close'].astype(float).pct_change(5)
            data = data.reset_index(drop=True)
            all_cefs_pd = all_cefs_pd.append(data[['DataDateJs', 'TICKER', 'Percent', 'DiscountData', 'Adj_Percent']]).fillna(0)

        else:
            # history 是周净值
            data['Percent'] = data['Data'].astype(float).pct_change()
            data = data.reset_index(drop=True)
            all_cefs_pd = all_cefs_pd.append(data[['DataDateJs', 'TICKER', 'Percent', 'DiscountData']]).fillna(0)

    indexes = [ 'CEFIGX', 'CEFOIX','CEFHYX', 'CEFBLX', 'CEFX']
    # indexes = ['CEFHYX']
    for index in indexes:
        cefx_merge(index, all_cefs_pd, adjusted)
        # break

if __name__ == "__main__":
    merge_all(False)
    merge_all(True)