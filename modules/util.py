# _*_ coding:utf8 _*_
# !/usr/bin/env python
import pandas as pd
import datetime
import numpy as np
import requests
import os
DEFAULT_VOL_WINDOW = 200 # a little less than a year
PRICE_FIELD = 'close'
QUOTE_URL = 'https://www.barchart.com/proxies/timeseries/queryeod.ashx?data=daily&maxrecords=10000&dividends=true&daystoexpiration=1'
ROOT_URL = 'https://core-api.barchart.com/v1/quotes/get?fields=symbol%2CcontractSymbol%2CdailyLastPrice%2CdailyPriceChange%2CdailyOpenPrice%2CdailyHighPrice%2CdailyLowPrice%2CdailyPreviousPrice%2CdailyVolume%2CdailyOpenInterest%2CdailyDate1dAgo%2CsymbolCode%2CsymbolType%2ChasOptions&list=futures.contractInRoot&meta=field.shortName%2Cfield.type%2Cfield.description&hasOptions=true&page=1&limit=100&raw=1'
DISCRIBUTION_URL = 'http://www.cefconnect.com/api/v3/distributionhistory/fund'
def get_returns(ticker, start=datetime.datetime(1940, 1, 1), end=datetime.datetime.now(), period=1):
	"""
	加载行情
	:param ticker:
	:param start:
	:param end:
	:param period:
	:return:
	"""
	file = 'data/barchart/%s.csv' % ticker
	file2 = 'data/caihui/future/%s_INDEX_MAIN_VOLUME' % ticker
	if os.path.exists(file):
		df = pd.read_csv(file)
	elif os.path.exists(file2):
		df = pd.read_csv(file2)
	else:
		print ticker," not found data file, get from barchart..."
		res = requests.get('%s&symbol=%s' % (QUOTE_URL, ticker))
		lines = res.text.split('\n')
		arrays = [line.split(',') for line in lines]
		df = pd.DataFrame.from_records(arrays)
		del df[7]
		df.columns = ['symbol', 'date', 'open', 'high', 'low', 'close', 'volume']
	df.index = df['date']
	df = df.ix[df['close'].dropna().index]
	df['close'] = df['close'].astype(float)
	df['Returns'] = df[PRICE_FIELD].pct_change(period)
	df['Log Returns'] = np.log(df[PRICE_FIELD]) - np.log(df[PRICE_FIELD].shift(1))
	return df


def get_all_contract(ticker):
	"""
	获取所有合约
	:param ticker:
	:return:
	"""
	res = requests.get('%s&root=%s' % (ROOT_URL, ticker))
	return res.json()


def get_distribution(ticker,start=datetime.datetime(1940, 1, 1), end=datetime.datetime.now()):
	"""
	获取指定时间内的分红数据
	:param ticker:
	:param start:
	:param end:
	:return:
	"""
	start = end - datetime.timedelta(days=365)
	res = requests.get('%s/%s/%s/%s' % (DISCRIBUTION_URL, ticker, start.strftime('%m-%d-%Y'), end.strftime('%m-%d-%Y')))
	if res.json().has_key('Success') and not res.json()['Success']:
		start = datetime.datetime(end.year, 1, 1)
		res = requests.get('%s/%s/%s/%s' % (DISCRIBUTION_URL, ticker, start.strftime('%m-%d-%Y'), end.strftime('%m-%d-%Y')))
		return res.json()
	else:
		return res.json()


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
