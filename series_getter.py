import pandas as pd
import datetime
import numpy as np
import modules.util as util
import math
from modules.all_weather_settings import OVERRIDE_TICKERS

# Use this to get price data for any ticker from Yahoo! Finance
# as such: python series_getter.py VTI

def main():
	start = datetime.datetime(1940, 1, 1)
	end = datetime.datetime.now()

	# tickers = sys.argv[1:] # command line arguments

	# INDICES_TICKERS = ["$IUXX", "$SPX"]
	# OVERRIDE_TICKERS.extend(INDICES_TICKERS)
	# for ticker in OVERRIDE_TICKERS:
	# 	try:
	# 		tick_df = util.get_returns(ticker, start, end)
	# 		print ticker, np.std(tick_df['Returns'])
	# 		tick_df.to_csv("data/barchart/%s.csv" % ticker)
	# 	except:
	# 		print ticker, ' error get data.'

	COMMIDITIES_TICKERS = ["DX","B6","D6","J6","S6","E6","A6","M6","N6","T6",
						   "L6","R6","CL","HO","RB","NG","QA","ZK","ZB","UD",
						   "ZN","TN","ZF","ZT","ZQ","GE","ZW","ZC","ZS","ZM",
						   "ZL","ZO","ZR","KE","MW","RS","ES","NQ","YM","RJ",
						   "EW","VI","GD","LE","GF","HE","DL","GC","SI","HG",
						   "PL","PA","CT","OJ","KC","SB","CC","LS","SD"]
	# COMMIDITIES_TICKERS = ['CL']
	all_datas = []
	dailyDate = 'None'
	for ticker in COMMIDITIES_TICKERS:
		try:
			print ticker, 'get all data'
			ticker_data = []
			all_contract = util.get_all_contract(ticker)
			for item_data in all_contract['data']:
				row_data = item_data['raw']
				row_data['root'] = ticker
				expiredDate = row_data['contractSymbol'][row_data['contractSymbol'].index('(') + 1:row_data['contractSymbol'].index(')')]
				if expiredDate == 'Cash':
					row_data['expiredDate'] = row_data['dailyDate1dAgo']
				else:
					row_data['expiredDate'] = (datetime.datetime.strptime(expiredDate, '%b \'%y') + datetime.timedelta(days=15)).strftime('%Y-%m-%d')
				row_data['main_volume'] = False
				ticker_data.append(row_data)

			ticker_pd = pd.DataFrame(ticker_data)
			ticker_pd.index = ticker_pd['contractSymbol']
			ticker_pd['main_volume'].ix[ticker_pd['dailyVolume'].idxmax(axis=1)] = True

			base_price = None
			dailyDate = None
			for key, row_data in ticker_pd.iterrows():
				if row_data['main_volume']:
					row_data['year_num'] = 1/365.0
					row_data['preminum'] = 0
					row_data['implied_roll_yeild'] = None
					base_price = row_data['dailyLastPrice']
					dailyDate = row_data['expiredDate']
				elif base_price and dailyDate:
					year_num_span = datetime.datetime.strptime(row_data['expiredDate'], '%Y-%m-%d') - datetime.datetime.strptime(dailyDate, '%Y-%m-%d') + datetime.timedelta(days=15)
					row_data['year_num'] = year_num_span.total_seconds() / (24 * 3600) / 365.0
					row_data['preminum'] = base_price / row_data['dailyLastPrice']
					row_data['implied_roll_yeild'] = np.power(row_data['preminum'], row_data['year_num']).round(4) - 1
				all_datas.append(row_data)
		except:
			print ticker, ' error get all contract.'
			raise
	all_pd = pd.DataFrame(all_datas)
	all_pd.to_csv('data/barchart/ALL_COMMODITIES_%s.csv' % dailyDate)
	print all_pd[['implied_roll_yeild', 'contractSymbol', 'main_volume', 'dailyVolume']]

	
if __name__ == "__main__":
	main()