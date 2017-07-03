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

	MORE_TICKERS = ["$IUXX", "$SPX"]
	OVERRIDE_TICKERS.extend(MORE_TICKERS)
	for ticker in OVERRIDE_TICKERS:
		tick_df = util.get_returns(ticker, start, end)

		print np.std(tick_df['Returns'])
		tick_df.to_csv("data/barchart/%s.csv" % ticker)


if __name__ == "__main__":
	main()