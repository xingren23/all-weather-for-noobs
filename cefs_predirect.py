# _*_ coding:utf8 _*_
# !/usr/bin/env python

import pandas as pd
import os
import statsmodels.formula.api as sm
import datetime

DATA_PATH = 'data/cef'

def load_history():
    print 'load history...'
    history_pd = pd.DataFrame()
    file = '%s/%s' % (DATA_PATH, 'ALL_CEFS_HISTORY.csv')
    if os.path.exists(file):
        history_pd = pd.read_csv(file, index_col = 'DataDateJs')
    else:
        symbols = [
            'TEI','WIW','WIA',
            'BCX','EMD','NHS','GIM','IAE','HIO','FAM','GHY','BGR','HYT','BTZ','ISD','EHI','MSD','DSU',
            'BHK','BDJ','HNW','DUC','FTF','VVR','PPR','HIX','JGH','CII','GDO','INB','BKT','BST','VBF','DIAX','MCN',
            'TSI'
        ]
        for symbol in symbols:
            # symbol = item_file[:item_file.find("_")]
            # print symbol
            history_file = '%s/%s_HISTORY.csv' % (DATA_PATH, symbol)
            hist_pd = pd.read_csv(history_file, index_col = 'DataDateJs')
            hist_pd['Return'] = hist_pd['Data'].pct_change() * 100
            hist_pd = hist_pd['2016-01-01':'2017-01-01'].dropna()
            hist_pd['DiscountRatio1'] = (hist_pd['DiscountData'] - hist_pd['DiscountData'].shift(1)) * 100/hist_pd['DiscountData'].shift(1)
            hist_pd['DiscountRatio2'] = hist_pd['DiscountRatio1'].shift(1)
            hist_pd['DiscountRatio3'] = hist_pd['DiscountRatio1'].shift(2)
            history_pd = history_pd.append(hist_pd[['TICKER','DiscountData', 'DiscountRatio1', 'DiscountRatio2', 'DiscountRatio3', 'Return']])

        history_pd = history_pd.dropna()
        history_pd.to_csv(file)
    return history_pd

def history_analyse():

    history_pd = load_history()
    history_pd.index = history_pd['TICKER']

    groups = history_pd.groupby(history_pd.index)
    for symbol, group in groups:
        mod = sm.ols(formula="Return ~ DiscountData", data=group).fit()
        print symbol, mod.summary()
        # break


if __name__ == "__main__":
    history_analyse()