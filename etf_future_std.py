import pandas as pd
import modules.util as util


future_ticker = 'ZNU17'
tick_df = util.get_future_returns('ZNU17')
tick_df.to_csv("data/barchart/%s.csv" % future_ticker)

zun17 = pd.read_csv('data/barchart/ZNU17.csv', index_col = 'date')
tlt = pd.read_csv('data/barchart/TLT.csv', index_col = 'date')

result = pd.DataFrame()
result['zun17-std-60'] = zun17['Standard Deviation (60d)']
result['tlt-std-60'] = tlt['Standard Deviation (60d)']

print result.tail(10)

print result['tlt-std-60'].mean() / result['zun17-std-60'].mean()