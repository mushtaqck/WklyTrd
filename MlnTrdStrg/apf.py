import numpy as np
import pandas as pd
import datetime

from numpy import NaN, Inf, arange, isscalar, asarray, array
from peakdetc import peakdet

from matplotlib import pyplot as plt
from matplotlib.ticker import Formatter

class PlotDateFormatter(Formatter):
    def __init__(self, dates, fmt='%Y-%m-%d %H:%M'):
        self.dates = dates
        self.fmt = fmt

    def __call__(self, x, pos=0):
        'Return the label for time x at position pos'
        ind = int(round(x))
        if ind >= len(self.dates) or ind < 0: return ''

        return self.dates[ind].strftime(self.fmt)


class ApfMn(object):
    """description of class"""
    delta = [55,34,21,13,8,5,3,2,1]

    def __init__(self,df,**kwargs):
        self.freq = '15min'
        self.is_Schiff = False


        if 'freq' in kwargs:
            self.freq = kwargs['freq']

        df = pd.DataFrame(df,columns=['d','p'])
        df.index = df['d']
        df = df.ix[1:,['p']]
        df = df.resample(self.freq,how='first')

        df = df.between_time('9:14','15:30')
        #drop na
        df = df.dropna()
        self.df = df

    def basic_linear_regression(self,x, y):
        # Basic computations to save a little time.
        length = len(x)
        sum_x = sum(x)
        sum_y = sum(y)

        # ?x^2, and ?xy respectively.
        sum_x_squared = sum(map(lambda a: a * a, x))
        sum_of_products = sum([x[i] * y[i] for i in range(length)])

        # Magic formulae!
        a = (sum_of_products - (sum_x * sum_y) / length) / (sum_x_squared - ((sum_x ** 2) / length))
        b = (sum_y - a * sum_x) / length
        return a, b

    def cpeaks2(self,cdf,sidx,linecords):
        cpeak_out = []
        cxrange = np.arange(len(cdf) - sidx,len(cdf))

        lst_regression = [] 
        for cor in linecords:
            regression = self.basic_linear_regression(cor[0],cor[1])
            lst_regression.append(regression)

        c_cords = [ [cxrange[x],y] for x,y in enumerate(cdf[-sidx:])]

        for c in c_cords:
            for i,r in enumerate(lst_regression):
                a = linecords[i][0]
                b = linecords[i][1]

                if c[1] >= a[1] and c[1] <= b[1]:
                    new_y = r[0] * c[0] + r[1]
                    if (new_y - (new_y * 0.0005)) <= c[1] <= (new_y + (new_y * 0.0005)):
                        cpeak_out.append([i,linecords[i],c])
        return cpeak_out

    def array_series(self,first,second,sets):
        combi = []
        for s in range(0,len(first)):
            try:
                combi.append(first[s])
                combi.append(second[s])
            except Exception,e:
                a = e

        return combi[sets:]


    def gen_afp(self, bothpeak,Schiff=False):

        linecords = []
        touch_down = []
        percent_return = 0
        curmaxY = 0
        curminY = 0

        apoint = bothpeak[0]
        bpoint = bothpeak[1]
        cpoint = bothpeak[2]
        
        if Schiff:
            spointx = (apoint[0] - bpoint[0]) / 2
            spointy = (apoint[1] - bpoint[1]) / 2
            apoint = [spointx,spointy]

        mnmidx = (cpoint[0] - bpoint[0]) / 2
        mnmidy = (cpoint[1] - bpoint[1]) / 2
        
        mnpoint = [mnmidx + bpoint[0],mnmidy + bpoint[1]]
        slope, intercept = np.polyfit([apoint[0],mnpoint[0]],[apoint[1],mnpoint[1]],1)
        prdictY = slope * apoint[1] + intercept
        
        mnline = [[apoint[1],apoint[0]],[prdictY,apoint[1]]]
        linecords.append(mnline)
        
        bmnline = [[bpoint[0],apoint[1] - mnmidx],[bpoint[1],prdictY - mnmidy]]
        linecords.append(bmnline)
        
        cmnline = [[cpoint[0],apoint[1] + mnmidx],[cpoint[1],prdictY + mnmidy]]
        linecords.append(cmnline)
        
        mn2midx = (mnpoint[0] - bpoint[0]) / 2
        mn2midy = (mnpoint[1] - bpoint[1]) / 2
        
        mnbline = [[mn2midx + bpoint[0],apoint[1] - mn2midx],[mn2midy + bpoint[1],prdictY - mn2midy]]
        linecords.append(mnbline)
        
        mncline = [[mn2midx + mnpoint[0],apoint[1] + mn2midx],[mn2midy + mnpoint[1],prdictY + mn2midy]]
        linecords.append(mncline)
        touch_down = self.cpeaks2(self.df['p'],int(len(self.df['p']) - cpoint[0]),linecords)
        percent_return = 100 * ((bpoint[1] - cpoint[1]) / 2) / apoint[1]
        
        max_x = len(self.df['p'])
        regre = self.basic_linear_regression(bmnline[0],bmnline[1])
        curmaxY = regre[0] * max_x + regre[1]        
        regre = self.basic_linear_regression(cmnline[0],cmnline[1])
        curminY = regre[0] * max_x + regre[1]

        curY = self.df['p'].tail(1)
        if curmaxY < int(curY) < curminY:
            return linecords,touch_down,self.df,percent_return,[curmaxY,curminY]
        else:
            return 0

    def run(self):
        deltastop = 55
        linecords = []
        touch_down = []
        percent_return = 0


        for d in self.delta:
            maxtab, mintab = peakdet(self.df['p'],d)
            if len(maxtab) > 2 and len(mintab) > 2 :
                #print 'delta stop -- {0}'.format(d)
                deltastop = d
                break
        
        bothpeak = []


        if len(maxtab) > 0 and len(mintab) > 0 :
            if maxtab[0][1] > mintab[0][1]:
                bothpeak = self.array_series(maxtab,mintab,-3)
            else:
                bothpeak = self.array_series(mintab,maxtab,-3)
        
            if len(bothpeak) == 3:
               rtn = self.gen_afp(bothpeak)
               if rtn == 0:
                   rtn = self.gen_afp(bothpeak,Schiff = True)
                   if rtn <> 0:
                       self.is_Schiff = True
               return rtn

        return 0


       









