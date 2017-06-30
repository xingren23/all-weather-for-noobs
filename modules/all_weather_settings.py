from modules.implied_vol import *

WEIGHTS_FILE = "output/weights.csv"

###############################################
# INPUT HERE

TICKERS = {
	"stocks": ['SPY', 'QQQ', 'EWJ', 'FXI'],
	"commodities": ['DBC'],
	"corporate credit": ['LQD'],
	"EM credit": ['EMB'],  # empty for now, can add
	"nominal bonds": ['TLT', 'IEF'],
	"inflation-linked": ['GLD']
}

TICKER_VOLATILITY_OVERRIDES = {
	"stocks": ['SPY', 'QQQ', 'EWJ', 'FXI'],
	"commodities": ['DBC'],
	"corporate credit": ['LQD'],
	"EM credit": ['EMB'],  # empty for now, can add
	"nominal bonds": ['TLT', 'IEF'],
	"inflation-linked": ['GLD']
}
OVERRIDE_TICKERS = [
	'SPY', 'QQQ', 'EWJ', 'FXI', 'DBC', 'LQD', 'EMB', 'TLT', 'IEF', 'GLD'
]
# TICKER_VOLATILITY_OVERRIDES = get_implied_volatilities_for_tickers(OVERRIDE_TICKERS)

VOL_WINDOW = 252*8

###############################################

print ">> Outputting to %s" % WEIGHTS_FILE