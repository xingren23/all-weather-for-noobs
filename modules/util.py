import pandas as pd
import datetime
import numpy as np
import requests
DEFAULT_VOL_WINDOW = 200 # a little less than a year
PRICE_FIELD = 'close'
URL = 'https://www.barchart.com/proxies/timeseries/queryeod.ashx?data=daily&maxrecords=10000&dividends=true&daystoexpiration=1'

def get_returns(ticker, start=datetime.datetime(1940, 1, 1), end=datetime.datetime.now(), period=1):
	res = requests.get('%s&symbol=%s' % (URL, ticker))
	lines = res.text.split('\n')
	arrays = [line.split(',') for line in lines]
	df = pd.DataFrame.from_records(arrays, columns=['symbol', 'date', 'open', 'high', 'low', 'close', 'volume'])
	df.index = df['date']
	df = df.dropna()
	df['open'] = df['open'].astype(float)
	df['high'] = df['high'].astype(float)
	df['low'] = df['low'].astype(float)
	df['close'] = df['close'].astype(float)
	df['volume'] = df['volume'].astype(float)
	df['Returns'] = df[PRICE_FIELD].pct_change(period)
	df['Log Returns'] = np.log(df[PRICE_FIELD]) - np.log(df[PRICE_FIELD].shift(1))
	return df


# we want variance so that when we sum, we can just do the straight sum
def get_annualized_variance_of_series(series, window=DEFAULT_VOL_WINDOW):
	window_std = np.std(series.tail(window))
	variance = window_std ** 2
	ann_var = variance * np.sqrt(252) # 252 is number of trading days in a year
	return ann_var
