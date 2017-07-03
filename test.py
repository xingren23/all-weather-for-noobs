import pandas as pd


zun17 = pd.read_csv('output/ZNU17.csv', index_col = 'date')
tlt = pd.read_csv('output/TLT.csv', index_col = 'date')

result = pd.DataFrame()
result['zun17-std-60'] = zun17['Standard Deviation (60d)']
result['tlt-std-60'] = tlt['Standard Deviation (60d)']

print result.tail(10)

print result['tlt-std-60'].mean() / result['zun17-std-60'].mean()