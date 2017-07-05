# _*_ coding:utf8 _*_
# !/usr/bin/env python
import pandas as pd
import datetime
import numpy as np
import requests
import os
DEFAULT_VOL_WINDOW = 200 # a little less than a year
PRICE_FIELD = 'close'
URL = 'https://www.barchart.com/proxies/timeseries/queryeod.ashx?data=daily&maxrecords=10000&dividends=true&daystoexpiration=1'

def get_returns(ticker, start=datetime.datetime(1940, 1, 1), end=datetime.datetime.now(), period=1):
	file = 'data/barchart/%s.csv' % ticker
	file2 = 'data/caihui/future/%s_INDEX_MAIN_VOLUME' % ticker
	if os.path.exists(file):
		df = pd.read_csv(file)
	elif os.path.exists(file2):
		df = pd.read_csv(file2)
	else:
		print ticker," not found data file, get from barchart..."
		res = requests.get('%s&symbol=%s' % (URL, ticker))
		lines = res.text.split('\n')
		arrays = [line.split(',') for line in lines]
		df = pd.DataFrame.from_records(arrays)
		del df[7]
		df.columns = ['symbol', 'date', 'open', 'high', 'low', 'close', 'volume']
	df.index = df['date']
	# df = df.dropna()
	df['open'] = df['open'].astype(float)
	df['high'] = df['high'].astype(float)
	df['low'] = df['low'].astype(float)
	df['close'] = df['close'].astype(float)
	df['volume'] = df['volume'].astype(float)
	df['Returns'] = df[PRICE_FIELD].pct_change(period)
	df['Log Returns'] = np.log(df[PRICE_FIELD]) - np.log(df[PRICE_FIELD].shift(1))
	return df

def get_annualized_volatility_of_series(series, window=DEFAULT_VOL_WINDOW):
	"""
	计算年化波动率
	:param series:
	:param window:
	:return:
	"""
	std = np.std(series.tail(window))
	ann_var = std * np.sqrt(252) # 252 is number of trading days in a year
	return ann_var
