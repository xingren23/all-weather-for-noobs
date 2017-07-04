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

	INDICES_TICKERS = ["$IUXX", "$SPX"]
	OVERRIDE_TICKERS.extend(INDICES_TICKERS)
	COMMIDITIES_TICKERS = ["DXY00","B6Y00","D6Y00","J6Y00","S6Y00","E6Y00","A6Y00","M6Y00","N6Y00","T6Y00",
						   "L6Y00","R6Y00","CLY00","HOY00","RBY00","NGY00","QAY00","ZKY00","ZBY00","UDY00",
						   "ZNY00","TNY00","ZFY00","ZTY00","ZQY00","GEY00","ZWY00","ZCY00","ZSY00","ZMY00",
						   "ZLY00","ZOY00","ZRY00","KEY00","MWY00","RSY00","ESY00","NQY00","YMY00","RJY00",
						   "EWY00","VIY00","GDY00","LEY00","GFY00","HEY00","DLY00","GCY00","SIY00","HGY00",
						   "PLY00","PAY00","CTY00","OJY00","KCY00","SBY00","CCY00","LSY00","SDY00"]
	OVERRIDE_TICKERS.extend(COMMIDITIES_TICKERS)
	for ticker in OVERRIDE_TICKERS:
		try:
			tick_df = util.get_returns(ticker, start, end)
			print ticker, np.std(tick_df['Returns'])
			tick_df.to_csv("data/barchart/%s.csv" % ticker)
		except:
			print ticker, ' error get data '


if __name__ == "__main__":
	main()