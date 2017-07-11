import requests
import pandas as pd
from modules.util import get_distribution, get_history
import fix_yahoo_finance as yf


def get_histories_from_yahoo():
    cefs = pd.read_csv('data/cef/CEFConnect.csv')
    for key, item in cefs.iterrows():
        ticker = item['TICKER']
        data = yf.download(ticker, start="2000-01-01", end="2017-07-30")
        data.to_csv('data/cef/%s_YAHOO_HISTORY.csv' % item['TICKER'])


if __name__ == "__main__":
    get_histories_from_yahoo()