import pandas as pd
import datetime
import numpy as np
import modules.util as util
from modules.all_weather_settings import OVERRIDE_TICKERS

# Use this to get price data for any ticker from Yahoo! Finance
# as such: python series_getter.py VTI

def main():
	start = datetime.datetime(1940, 1, 1)
	end = datetime.datetime.now()

	# tickers = sys.argv[1:] # command line arguments

	for ticker in OVERRIDE_TICKERS:
		tick_df = util.get_returns(ticker, start, end)
		tick_df['Standard Deviation (60d)'] = pd.rolling_std(tick_df['Returns'], window=60)
		tick_df['Standard Deviation (200d)'] = pd.rolling_std(tick_df['Returns'], window=200)

		print ticker + " Standard Deviation"
		print np.std(tick_df['Returns'])
		tick_df.to_csv("output/%s.csv" % ticker)

	FUTURE_TICKERS = ['ZNU17']
	for future_ticker in FUTURE_TICKERS:
		tick_df = util.get_future_returns(future_ticker, start, end)
		tick_df['Standard Deviation (60d)'] = pd.rolling_std(tick_df['Returns'], window=60)
		tick_df['Standard Deviation (200d)'] = pd.rolling_std(tick_df['Returns'], window=200)

		print future_ticker + " Standard Deviation"
		print np.std(tick_df['Returns'])
		tick_df.to_csv("output/%s.csv" % future_ticker)


if __name__ == "__main__":
	main()