import matplotlib.pyplot as plt

from zipline.algorithm import TradingAlgorithm
from zipline.utils.factory import load_from_yahoo

# Import exponential moving average from talib wrapper
from zipline.transforms.ta import EMA

from datetime import datetime
import pytz

import urllib2
from collections import deque
from zipline.api import order_target, record, symbol

sym = ['CROMPGREA.NS','LT.NS','LUPIN.NS','RPOWER.NS','VOLTAS.NS','EXIDEIND.NS']
accum = deque()

class DualEMATaLib(TradingAlgorithm):

    def initialize(self):
        self.invested = False
       
    def handle_data(self, data):
        print data



if __name__ == '__main__':
    start = datetime(2014, 10, 1, 0, 0, 0, 0, pytz.utc)
    end = datetime(2014, 10, 29, 0, 0, 0, 0, pytz.utc)
    data = load_from_yahoo(stocks=sym, indexes={}, start=start,
                           end=end)

    # print data


    dma = DualEMATaLib()
    results = dma.run(data).dropna()
    results.plot()
    plt.show(_) 