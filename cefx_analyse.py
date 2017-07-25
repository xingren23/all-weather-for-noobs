# _*_ coding:utf8 _*_
# !/usr/bin/env python

import pandas as pd
import os
from datetime import datetime

DATA_PATH = 'data/cef'
INDEX_WEIGHTS = {'CEFIGX': 0.4, 'CEFOIX':0.3, 'CEFHYX':0.3}

def cefx_merge(index, in_index, index_groups, all_cefs_pd, adjusted):
    cefx_quarters = pd.read_csv('%s/%s_QUARTER_SNAPSHOT.csv' % (DATA_PATH,index))
    cefx_quarters['Ticker'] = cefx_quarters['Ticker'].apply(lambda x: x[:x.find(" ")] if x.find(" ")>0 else x)
    cefx_quarters.index = cefx_quarters['Ticker']
    if index != in_index:
        # 只选择in_index中包括的股票代码
        in_index_pd = index_groups.get_group(in_index)
        cefx_quarters = cefx_quarters.loc[cefx_quarters.index.isin(in_index_pd['Ticker'])]

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
    last_discount_pd = pd.DataFrame()
    last_preminum_pd = pd.DataFrame()
    last_pd = pd.DataFrame()
    for time,row in cefx_pd.T.iteritems():
        date = time.strftime('%Y-%m-%d')
        # if date != '2008-10-03':
        #     continue
        if date in day_groups.groups.keys():
            day_pd = day_groups.get_group(date)
            day_pd.index = day_pd['TICKER']

            row = row[row>0]
            discount_value, full_discount_value, discount_ratio, discount_volume, discount_turnover, last_discount_pd = \
                cal_row_value(index, in_index, index_groups, date, row, day_pd, 'discount', adjusted, last_discount_pd)
            preminum_value, full_preminum_value, preminum_ratio, preminum_volume, preminum_turnover, last_preminum_pd = \
                cal_row_value(index, in_index, index_groups, date, row, day_pd, 'preminum', adjusted, last_preminum_pd)
            row_value, full_value, row_ratio, row_volume, row_turnover, last_pd \
                = cal_row_value(index, in_index, index_groups, date, row, day_pd, 'normal', adjusted, last_pd)
            print date, row_value, row_ratio, row_volume, row_turnover, discount_value, preminum_value
            returns.append({'date': date,
                            'value': row_value, 'full_value': full_value,
                            'ratio': row_ratio, 'volume': row_volume, 'turnover': row_turnover,
                            'preminum_value': preminum_value, 'full_preminum_value': full_preminum_value,
                            'preminum_ratio': preminum_ratio, 'preminum_volume': preminum_volume, 'preminum_turnover':preminum_turnover,
                            'discount_value':discount_value, 'full_discount_value':full_discount_value,
                            'discount_ratio': discount_ratio, 'discount_volume': discount_volume, 'discount_turnover': discount_turnover
                            })

    returns_pd = pd.DataFrame(returns)
    if adjusted:
        returns_pd.to_csv('%s/%s_ADJUSTED_MERGED_RETURNS.csv' % (DATA_PATH, in_index))
    else:
        returns_pd.to_csv('%s/%s_MERGED_RETURNS.csv' % (DATA_PATH, in_index))


def cal_row_value(index, in_index, index_groups, date, row, day_pd, sort, adjusted, last_day_pd):
    day_pd = day_pd.loc[day_pd.index.isin(row.index)]
    day_pd['weight'] = row
    if sort == 'discount':
        if index == in_index:
            # 类型中性化
            data_pd = pd.DataFrame()
            total_num = len(row) * 0.15
            for type, type_w in INDEX_WEIGHTS.iteritems():
                type_pd = day_pd.loc[day_pd.index.isin(index_groups.get_group(type)['Ticker'])].sort_values(by='DiscountData', ascending=True)
                type_pd = type_pd.head(int(type_w * total_num))
                data_pd = data_pd.append(type_pd)
        else:
            data_pd = day_pd.loc[day_pd.index.isin(index_groups.get_group(in_index)['Ticker'])].sort_values(by='DiscountData', ascending=True)
            data_pd = data_pd.head(int(0.15*len(data_pd)))
    elif sort == 'preminum':
        if index == in_index:
            # 类型中性化
            data_pd = pd.DataFrame()
            total_num = len(row) * 0.15
            for type, type_w in INDEX_WEIGHTS.iteritems():
                type_pd = day_pd.loc[day_pd.index.isin(index_groups.get_group(type)['Ticker'])].sort_values(by='DiscountData', ascending=False)
                type_pd = type_pd.head(int(type_w*total_num))
                data_pd = data_pd.append(type_pd)
        else:
            data_pd = day_pd.loc[day_pd.index.isin(index_groups.get_group(in_index)['Ticker'])].sort_values(by='DiscountData', ascending=False)
            data_pd = data_pd.head(int(0.15*len(data_pd)))
    else:
        data_pd = day_pd

    data_pd.drop_duplicates(inplace=True)
    # print row, data_pd, adjusted

    # print day_pd
    row_value = 0.0
    full_value = 0.0
    row_weight = 0.001
    discount_ratio = 0
    volume = 0.0
    turnover = 0.0
    for symbol in data_pd.index:
        weight = data_pd.ix[symbol]['weight']
        if adjusted:
            if sort == 'discount' or sort == 'preminum':
                full_value += weight * data_pd.ix[symbol]['Discount_Adj_Percent']
            else:
                full_value += weight * data_pd.ix[symbol]['Adj_Percent']
            volume += weight * data_pd.ix[symbol]['Volume']

        if symbol == 'DSU':
            continue

        if sort == 'discount' or sort == 'preminum':
            row_value += weight * data_pd.ix[symbol]['Discount_Percent']
        else:
            row_value += weight * data_pd.ix[symbol]['Percent']
        row_weight += weight

        discount_ratio += weight * data_pd.ix[symbol]['DiscountData']
        # 不再上次的data_pd中,意味着换手
        if symbol not in last_day_pd.index:
            turnover += weight

    last_day_pd = data_pd

    row_value *= 100.0 / row_weight
    full_value *= 100.0 / row_weight
    discount_ratio *= 100.0 / row_weight
    volume *= 100.0 / row_weight
    turnover *= 100.0 / row_weight
    return row_value, full_value, discount_ratio, volume, turnover, last_day_pd

def load_cefs_history(adjusted):
    # load cefs history data
    all_cefs_pd = pd.DataFrame()
    all_yahoo_history = '%s/%s' % (DATA_PATH,'ALL_CEFS_YAHOO.csv')
    all_history = '%s/%s' % (DATA_PATH, 'ALL_CEFS.csv')
    if os.path.exists(all_yahoo_history) and adjusted:
        all_cefs_pd = pd.read_csv(all_yahoo_history)
    elif os.path.exists(all_history) and not adjusted:
        all_cefs_pd = pd.read_csv(all_history)
    else:
        all_files = [item for item in os.listdir(DATA_PATH) if item.endswith('_YAHOO_HISTORY.csv')]
        for item_file in all_files:

            symbol = item_file[:item_file.find("_")]
            if symbol == 'BGX':
                continue
            data = pd.read_csv('%s/%s_HISTORY.csv' % (DATA_PATH, symbol))
            data.index = data['DataDateJs']
            if adjusted:
                yahoo_data = pd.read_csv('%s/%s_YAHOO_HISTORY.csv' % (DATA_PATH, symbol), index_col = 'Date')
                # yahoo_history 是日净值 -> 转换为周净值
                yahoo_data = yahoo_data.ix[data.index]
                data['Adj_Percent'] = yahoo_data['Adj Close'].astype(float).pct_change()
                data['Percent'] = yahoo_data['Close'].astype(float).pct_change()
                data['Discount_Adj_Percent'] = yahoo_data['Adj Close'].astype(float).pct_change().shift(-1)
                data['Discount_Percent'] = yahoo_data['Close'].astype(float).pct_change().shift(-1)
                # yahoo 数据源 close与adj close 乱了
                data['Volume'] = yahoo_data['Volume'].fillna(0).astype(int) * yahoo_data['Adj Close'].astype(float)
                data = data.reset_index(drop=True)
                all_cefs_pd = all_cefs_pd.append(data[['DataDateJs', 'TICKER', 'Percent', 'Volume',
                                                       'DiscountData', 'Adj_Percent', 'Discount_Adj_Percent', 'Discount_Percent']]).fillna(0)

            else:
                # history 是周净值
                data['Percent'] = data['Data'].astype(float).pct_change()
                data['Discount_Percent'] = data['Data'].astype(float).pct_change().shift(-1)
                data = data.reset_index(drop=True)
                all_cefs_pd = all_cefs_pd.append(data[['DataDateJs', 'TICKER', 'Percent', 'DiscountData',
                                                    'Discount_Percent']]).fillna(0)
        if adjusted:
            all_cefs_pd[all_cefs_pd['DataDateJs']>'2001-01-01'].to_csv(all_yahoo_history)
        else:
            all_cefs_pd[all_cefs_pd['DataDateJs']>'2001-01-01'].to_csv(all_history)
    return all_cefs_pd


def load_cefs_types():
    index_classes_pd = pd.DataFrame()
    cefs_type_file = '%s/CEFS_TYPES.csv' % DATA_PATH
    if os.path.exists(cefs_type_file):
        index_classes_pd = pd.read_csv(cefs_type_file)
    else:
        for index in INDEX_WEIGHTS.keys():
            in_cefx_quarters = pd.read_csv('%s/%s_QUARTER_SNAPSHOT.csv' % (DATA_PATH,index))
            in_cefx_quarters['Ticker'] = in_cefx_quarters['Ticker'].apply(lambda x: x[:x.find(" ")] if x.find(" ")>0 else x)
            in_cefx_quarters.index = in_cefx_quarters['Ticker']
            in_cefx_quarters = in_cefx_quarters.groupby(in_cefx_quarters.index).first()
            in_cefx_quarters['TYPE'] = index
            index_classes_pd = index_classes_pd.append(pd.DataFrame(in_cefx_quarters[['TYPE', 'Ticker']]))
        index_classes_pd.index = index_classes_pd['Ticker']
        index_classes_pd.to_csv(cefs_type_file)
    return index_classes_pd


def merge_all(adjusted=False):
    # load history data
    all_cefs_pd = load_cefs_history(adjusted)
    # load types
    index_types_pd = load_cefs_types()

    indexes = ['CEFX']
    for index in indexes:
        cefx_merge('CEFX', index, index_types_pd.groupby('TYPE'), all_cefs_pd, adjusted)


if __name__ == "__main__":
    merge_all(False)
    merge_all(True)