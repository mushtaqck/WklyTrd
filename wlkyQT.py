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

sym = symbol('CROMPGREA.NS')
accum = deque()

class DualEMATaLib(TradingAlgorithm):

    def initialize(self):
               # To keep track of whether we invested in the stock or not
        self.invested = False
       
    def handle_data(self, data):
        hdata = data[sym].price
        # print hdata
        
        accum.append(hdata)

        if len(accum) > 4:
            currentbar = accum.popleft()
            wkday = data[sym].dt.strftime('%A')
            self.record(CEATNS=data[sym].price,wkday=wkday,
                        buy_price= currentbar,
                        sell_price= hdata,
                        PL=hdata - currentbar,
                        PLP=((hdata - currentbar) * 100) /currentbar )




if __name__ == '__main__':
    proxy_support = urllib2.ProxyHandler({"http":"10.23.28.130:8080"})
    opener = urllib2.build_opener(proxy_support)
    urllib2.install_opener(opener)

    start = datetime(2014, 1, 1, 0, 0, 0, 0, pytz.utc)
    end = datetime(2014, 10, 29, 0, 0, 0, 0, pytz.utc)
    data = load_from_yahoo(stocks=[sym], indexes={}, start=start,
                           end=end)

    # print data


    dma = DualEMATaLib()
    results = dma.run(data).dropna()
    
    results['daten'] = results.index

    df = results.pivot('daten','wkday','PLP').fillna(0)

    df.plot()
      # Three subplots sharing both x/y axes
    #f, (mo, tu, we,th,fr) = plt.subplots(5, sharex=True, sharey=True)

    #mo.plot( df.Monday.dropna())    
    #tu.plot( df.Tuesday.dropna())
    #we.plot( df.Wednesday.dropna())
    #th.plot( df.Thursday.dropna())
    #fr.plot( df.Friday.dropna())


  
    #f.subplots_adjust(hspace=0)
    #plt.setp([a.get_xticklabels() for a in f.axes[:-1]], visible=False)
    plt.show(_) 