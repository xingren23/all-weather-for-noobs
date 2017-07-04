# _*_ coding:utf8 _*_
# !/usr/bin/env python

import pandas as pd
import datetime
import collections

import modules.util as util
import modules.backtesting as backtesting
import pprint
from modules.all_weather_settings import *
from modules.risk_parity import calcu_w

##### IMPLEMENTATION DETAILS ##### 
# 商品期货合成

# given a tuple of (label, value)s, return
# risk parity equalized {"label": weight}
def equalize_weights(tuples):
	tuples = [tup for tup in tuples if tup[1] != 0.0] # remove zero values
	num_args = len(tuples)

	if (num_args):
		last_vol = tuples[num_args-1][1]
		last_label = tuples[num_args-1][0]

		last_vol_over_other_vols = []
		for i in range(0, num_args-1): 
			curr_vol = tuples[i][1]
			last_vol_over_other_vols.append(last_vol/curr_vol)

		weight_n = 1.0 / (sum(last_vol_over_other_vols) + 1)
		weights_i = collections.defaultdict(lambda: 0.0)
		for i in range(0, num_args-1):
			curr_vol = tuples[i][1]
			curr_label = tuples[i][0]
			weights_i[curr_label] = (last_vol / curr_vol) * weight_n

		weights_i[last_label] = weight_n
		return weights_i
	else:
		return collections.defaultdict(lambda: 0.0)


# environment_box: gf|gr|ir|if
def finalize_ticker_weights(tickers, asset_class_weights, weights_by_asset_predefined):


	print "Predefined weights: ",weights_by_asset_predefined
	weights_by_asset = weights_by_asset_predefined

	weights_dict = {}

	for asset_class in weights_by_asset:
		for ticker in tickers[asset_class]:
			weights_dict[ticker] = asset_class_weights[asset_class][ticker] * weights_by_asset[asset_class]

	weights_dict['Date'] = datetime.datetime.now().strftime("%m/%d/%y")

	return weights_dict


# return {"stocks": int, "commodities": int, etc} 
# @param: whatever is returend from get_asset_class_weights
def get_asset_class_volatilities_from_ticker_weights(asset_class_weights, ticker_volatilities):
	asset_volatilities = {}
	for asset_class in asset_class_weights:
		weights = asset_class_weights[asset_class]
		volatility = 0.0
		for ticker in weights:
			weight = weights[ticker]
			volatility += weight * ticker_volatilities[ticker]
		asset_volatilities[asset_class] = volatility
	return asset_volatilities

# return {asset_class: {tickers: weights}}
def get_asset_class_weights(tickers, ticker_volatilities):
	asset_class_weights = {}
	for asset_class in tickers: # stocks, commodities, EM credit, etc
		tickers_in_asset_class = tickers[asset_class]
		volatilities_for_tickers = [ticker_volatilities[ticker] for ticker in tickers_in_asset_class]
		ordered_weights_by_ticker = equalize_weights(zip(tickers_in_asset_class, volatilities_for_tickers)).values()
		asset_class_weights[asset_class] = dict(zip(tickers_in_asset_class, ordered_weights_by_ticker))

	return asset_class_weights


def get_asset_class_weights_avg(tickers):
	asset_class_weights = {}
	for asset_class in tickers: # stocks, commodities, EM credit, etc
		tickers_in_asset_class = tickers[asset_class]
		ordered_weights_by_ticker = [1.0/len(tickers_in_asset_class) for ticker in tickers_in_asset_class]
		asset_class_weights[asset_class] = dict(zip(tickers_in_asset_class, ordered_weights_by_ticker))

	return asset_class_weights

# Overriding historical volatility with implied
def perform_variance_overrides(overrides_tickers, ticker_volatilities):
	for ticker in overrides_tickers:
		if (ticker in ticker_volatilities): 
			print ">> Overriding volatility %s. Setting to %0.05f" % (ticker, overrides_tickers[ticker])
			ticker_volatilities[ticker] = overrides_tickers[ticker]

	return ticker_volatilities


# given a dictionary from get_ticker_data, get volatility
def get_ticker_volatilities(ticker_data):
	ticker_volatilities = {}
	for ticker in ticker_data:
		ticker_volatilities[ticker] = util.get_annualized_volatility_of_series(ticker_data[ticker]['Returns'], window=VOL_WINDOW)

	ticker_volatilities = perform_variance_overrides([], ticker_volatilities)
	return ticker_volatilities


# get price history
def get_ticker_data(tickers, start=datetime.datetime(1940, 1, 1), end = datetime.datetime.now()):
	# get all ticker price data -- we take the window of volatility 
	# in util.get_annualized_volatility_of_series
	ret = {}
	for group in tickers:
		for ticker in tickers[group]:
			ret[ticker] = util.get_future_returns(ticker, start=start, end=end)
	return ret


def main():
	pp = pprint.PrettyPrinter(indent=4)

	# first get ticker price and volatility data
	print ">> Getting ticker data..."
	TICKERS = {
		"energies": ['CLY00', 'RBY00', 'NGY00', 'QAY00'],
		"grains": ['ZWY00', 'ZCY00', 'ZSY00'],
		"metals": ['GCY00', 'SIY00', 'HGY00'],
		"softs": ['CTY00', 'SBY00', 'CCY00']
	}

	weights_by_asset_predefined = {
		"energies": 0.25,
		"grains": 0.25,
		"metals": 0.25,
		"softs": 0.25
	}

	ticker_data = get_ticker_data(TICKERS)

	ticker_volatilities = get_ticker_volatilities(ticker_data)
	
	# then treat each group (like stocks) as its own portfolio and equalize volatility contributions
	# asset_class_weights = get_asset_class_weights(TICKERS, ticker_volatilities)
	asset_class_weights = get_asset_class_weights_avg(TICKERS)

	# find individual asset weight by multiplying box_weights and environment_weights per my all weather configuration
	risk_weight_dict = finalize_ticker_weights(TICKERS, asset_class_weights, weights_by_asset_predefined)
	date = risk_weight_dict['Date']
	del risk_weight_dict['Date']

	# risk weight to value weight
	ticker_data_pd = pd.DataFrame()
	risk_weights = []
	for key in ticker_data:
		ticker_data_pd[key] = ticker_data[key]['Returns']
		risk_weights.append(risk_weight_dict[key])
	V = np.matrix(ticker_data_pd.dropna().corr())

	weights = calcu_w(risk_weights, V, [0.1 for i in risk_weight_dict])
	value_weight_dict = {}
	for i, key in enumerate(ticker_data):
		value_weight_dict[key] = weights[i]

	print "\n>> Volatilities"
	pp.pprint(ticker_volatilities)
	print "\n>> Final risk weights"
	pp.pprint(risk_weight_dict)
	print "\n>> Final value weights"
	pp.pprint(value_weight_dict)

	backtesting.backtest(value_weight_dict, output='commodities') # yes, this is backtesting with weights we could have only known today, so it's not super rigorous


if __name__ == "__main__":
	main()