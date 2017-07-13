# _*_ coding:utf8 _*_
# !/usr/bin/env python

import pandas as pd
import os
from datetime import datetime

DATA_PATH = 'data/cef'

def cefx_merge(index, in_index, index_classes, all_cefs_pd, adjusted):
    cefx_quarters = pd.read_csv('%s/%s_QUARTER_SNAPSHOT.csv' % (DATA_PATH,index))
    cefx_quarters['Ticker'] = cefx_quarters['Ticker'].apply(lambda x: x[:x.find(" ")] if x.find(" ")>0 else x)
    if in_index != index:
        # 只选择in_index中包括的股票代码
        cefx_quarters = cefx_quarters.loc[cefx_quarters['Ticker'].isin(index_classes[in_index])]
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

            discount_value, full_discount_value, discount_ratio, discount_volume = cal_row_value(index, in_index, index_classes, date, row, day_pd, 'discount', adjusted)
            preminum_value, full_preminum_value, preminum_ratio, preminum_volume = cal_row_value(index, in_index, index_classes, date, row, day_pd, 'preminum', adjusted)
            row_value, full_value, row_ratio, row_volume = cal_row_value(index, in_index, index_classes, date, row, day_pd, '', adjusted)
            print date, row_value, discount_value, preminum_value, row_ratio, row_volume
            returns.append({'date': date,
                            'value': row_value, 'full_value': full_value,'ratio': row_ratio, 'row_volume': row_volume,
                            'preminum_value': preminum_value, 'full_preminum_value': full_preminum_value, 'preminum_ratio': preminum_ratio, 'preminum_volume': preminum_volume,
                            'discount_value':discount_value, 'full_discount_value':full_discount_value, 'discount_ratio': discount_ratio, 'discount_volume': discount_volume,
                            })

    returns_pd = pd.DataFrame(returns)
    if adjusted:
        returns_pd.to_csv('%s/%s_ADJUSTED_MERGED_RETURNS.csv' % (DATA_PATH, in_index))
    else:
        returns_pd.to_csv('%s/%s_MERGED_RETURNS.csv' % (DATA_PATH, in_index))


def cal_row_value(index, in_index, index_classes, date, row, day_pd, sort, adjusted):
    if sort == 'discount':
        if index == in_index:
            # 类型中性化
            data_pd = pd.DataFrame()
            for type, type_w in index_classes[in_index].iteritems():
                type_pd = day_pd.ix[index_classes[type]].sort_values(by='DiscountData', ascending=True).dropna()
                type_pd = type_pd.head(int(type_w*0.3*len(data_pd)))
                data_pd.append(type_pd)
        else:
            data_pd = day_pd.ix[row.index].sort_values(by='DiscountData', ascending=True).dropna()
            data_pd = data_pd.head(int(0.3*len(data_pd)))
    elif sort == 'preminum':
        if index == in_index:
            # 类型中性化
            data_pd = pd.DataFrame()
            for type, type_w in index_classes[in_index].iteritems():
                type_pd = day_pd.ix[index_classes[type]].sort_values(by='DiscountData', ascending=True).dropna()
                type_pd = type_pd.head(int(type_w*0.3*len(data_pd)))
                data_pd.append(type_pd)
        else:
            data_pd = day_pd.ix[row.index].sort_values(by='DiscountData', ascending=False).dropna()
            data_pd = data_pd.head(int(0.3*len(data_pd)))
    else:
        data_pd = day_pd.ix[row.index].dropna()

    # print row, data_pd, adjusted

    # print day_pd
    row_value = 0.0
    full_value = 0.0
    row_weight = 0.001
    discount_ratio = 0
    volume = 0.0
    for symbol, weight in row.iteritems():
        if symbol in data_pd.index:
            if adjusted:
                full_value += weight * data_pd.ix[symbol]['Adj_Percent']
                volume += weight * data_pd.ix[symbol]['Volume']

            if symbol == 'DSU':
                continue
            row_value += weight * data_pd.ix[symbol]['Percent']
            row_weight += weight

            discount_ratio += weight * data_pd.ix[symbol]['DiscountData']

    row_value *= 100.0 / row_weight
    full_value *= 100.0 / row_weight
    discount_ratio *= 100.0 / row_weight
    volume *= 100.0 / row_weight
    return row_value, full_value, discount_ratio, volume


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
            yahoo_data = yahoo_data.ix[data.index].fillna(0)
            data['Adj_Percent'] = yahoo_data['Adj Close'].astype(float).pct_change()
            data['Percent'] = yahoo_data['Close'].astype(float).pct_change()
            # yahoo 数据源 close与adj close 乱了
            data['Volume'] = yahoo_data['Volume'].astype(int) * yahoo_data['Adj Close'].astype(float)
            data = data.reset_index(drop=True)
            all_cefs_pd = all_cefs_pd.append(data[['DataDateJs', 'TICKER', 'Percent', 'Volume', 'DiscountData', 'Adj_Percent']])

        else:
            # history 是周净值
            data['Percent'] = data['Data'].astype(float).pct_change()
            data = data.reset_index(drop=True)
            all_cefs_pd = all_cefs_pd.append(data[['DataDateJs', 'TICKER', 'Percent', 'DiscountData']]).fillna(0)


    indexes = [ 'CEFIGX', 'CEFOIX','CEFHYX', 'CEFBLX', 'CEFX']
    # indexes = ['CEFX']
    index_classes = {}
    for index in indexes:
        if index == 'CEFX':
            index_classes[index] = {'CEFIGX': 0.4, 'CEFOIX':0.3, 'CEFHYX':0.3}
        else:
            in_cefx_quarters = pd.read_csv('%s/%s_QUARTER_SNAPSHOT.csv' % (DATA_PATH,index))
            in_cefx_quarters['Ticker'] = in_cefx_quarters['Ticker'].apply(lambda x: x[:x.find(" ")] if x.find(" ")>0 else x)
            in_cefx_quarters.index = in_cefx_quarters['Ticker']
            in_cefx_quarters.drop_duplicates(inplace=True)
            index_classes[index] = in_cefx_quarters.index

    indexes = ['CEFX']
    for index in indexes:
        cefx_merge('CEFX',index, index_classes, all_cefs_pd, adjusted)



if __name__ == "__main__":
    # merge_all(False)
    merge_all(True)