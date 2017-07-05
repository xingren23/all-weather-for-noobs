from modules.implied_vol import *

WEIGHTS_FILE = "output/weights.csv"

###############################################
# INPUT HERE

TICKERS = {
	"stocks": ['SPY', 'QQQ', 'EWJ', 'FXI'],
	"commodities": ['COMMODITIES'],
	"corporate credit": ['LQD'],
	"EM credit": ['EMB'],  # empty for now, can add
	"nominal bonds": ['TLT', 'IEF'],
	"inflation-linked": []
}

OVERRIDE_TICKERS = [
]
TICKER_VOLATILITY_OVERRIDES = get_implied_volatilities_for_tickers(OVERRIDE_TICKERS)

VOL_WINDOW = 252*5

###############################################

print ">> Outputting to %s" % WEIGHTS_FILE