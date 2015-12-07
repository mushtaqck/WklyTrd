import csv
import pandas as pd
import numpy as np
import os  

from numpy import NaN, Inf, arange, isscalar, asarray, array
from matplotlib import pyplot as plt
from matplotlib.ticker import Formatter
from peakdetc import peakdet

class MyFormatter(Formatter):
    def __init__(self, dates, fmt='%Y-%m-%d %H:%M'):
        self.dates = dates
        self.fmt = fmt

    def __call__(self, x, pos=0):
        'Return the label for time x at position pos'
        ind = int(round(x))
        if ind >= len(self.dates) or ind < 0: return ''

        return self.dates[ind].strftime(self.fmt)

def line_prepender(filename,line):
    with open(filename,'r+') as f:
        content = f.read()
        fstln = content.splitlines()[0]

        if fstln != line:
            f.seek(0,0)        
            f.write(line.rstrip('\r\n') + '\n' + content)

def array_series(first,second,sets):
    combi = []
    for s in range(0,len(first)):
        try:
            combi.append(first[s])
            combi.append(second[s])
        except Exception,e:
            a = e

    return combi[sets:]
    #return combi
def apf_draw(fn):
    #fn = ".\\data\\lastweek\\HHM_20141219.csv"

    #line_prepender(fn,"d,t,p,na")
    df = pd.read_csv(fn,parse_dates={'Timestamp':['d','t']},index_col='Timestamp')

    df = df.ix[1:,['p']]

    #resample to 15 min
    df = df.resample('20min',how='first')

    #drop na
    df = df.dropna()
#price min, max
    pmin = df.p.min()
    pmax = df.p.max()

    formatter = MyFormatter(df.index)


    fig, ax = plt.subplots()
    ax.xaxis.set_major_formatter(formatter)
    ax.plot(np.arange(len(df)), df.p)

    #detect peak
    # 1 1 2 3 5 8 13 21 34
    maxtab = []
    mintab = []
    delta = [34,21,13,8,5,3,2,1]

    for d in delta:
        maxtab, mintab = peakdet(df['p'],d)
        if len(maxtab) > 1 and len(mintab) > 1 :
            print 'delta stop -- {0}'.format(d)
            break
        else:
            print 'min delta -- {0}'.format(d)

    #draw APF
    if maxtab.any() and mintab.any():
        #plot peak
        plt.scatter(array(maxtab)[:,0], array(maxtab)[:,1], color = 'black')
        plt.scatter(array(mintab)[:,0], array(mintab)[:,1], color='red')
        
        sets = -3
        if maxtab[0][1] > mintab[0][1]:
            bothpeak = array_series(maxtab,mintab,sets)
        else:
            bothpeak = array_series(mintab,maxtab,sets)


        for i,apoint in enumerate(bothpeak):
           try:
               if (i + 2) < len(bothpeak):
                    bpoint = bothpeak[i + 1]
                    cpoint = bothpeak[i + 2]
                
                    mnmidx = (cpoint[0] - bpoint[0]) / 2
                    mnmidy = (cpoint[1] - bpoint[1]) / 2

                    plt.plot([bpoint[0],cpoint[0]],[bpoint[1],cpoint[1]],color='yellow')

                    mnpoint = [mnmidx + bpoint[0],mnmidy + bpoint[1]]

                    mnline = [[apoint[0],mnpoint[0]],[apoint[1],mnpoint[1]]]
                    plt.plot(mnline[0],mnline[1],color='orange')

                    slope, intercept = np.polyfit(mnline[0],mnline[1], 1)
                    prdictY = slope * apoint[1] + intercept
                    plt.plot(apoint[1],prdictY,'om')

                    mnline = [[mnpoint[1],mnpoint[0]],[prdictY,mnpoint[1]]]
                    plt.plot(mnline[0],mnline[1],color='orange')

                    bmnline = [[bpoint[0],mnpoint[1] - mnmidx],[bpoint[1],prdictY - mnmidy]]
                    plt.plot(bmnline[0],bmnline[1],color='blue')
                    
                    cmnline = [[cpoint[0],mnpoint[1] + mnmidx],[cpoint[1],prdictY + mnmidy]]
                    plt.plot(cmnline[0],cmnline[1],color='purple')


                    mn2midx = (mnpoint[0] - bpoint[0]) / 2
                    mn2midy = (mnpoint[1] - bpoint[1]) / 2

                    plt.plot(mn2midx + bpoint[0],mn2midy + bpoint[1],'om')
                    plt.plot(mn2midx + mnpoint[0],mn2midy + mnpoint[1],'om')
                    
                    mnbline = [[mn2midx + bpoint[0],mnpoint[1] - mn2midx],[mn2midy + bpoint[1],prdictY - mn2midy]]
                    plt.plot(mnbline[0],mnbline[1],'--',color='black')

                    mncline = [[mn2midx + mnpoint[0],mnpoint[1] + mn2midx],[mn2midy + mnpoint[1],prdictY + mn2midy]]
                    plt.plot(mncline[0],mncline[1],'--',color='black')

                    break
           except Exception, e:
                print e
    fig.autofmt_xdate()
    plt.xlim(-10,len(df.index) + 10)
    plt.ylim(pmin - 10,pmax + 10)
    #plt.savefig(fn.replace('.csv','.png'))
    plt.show()
if __name__ == '__main__':

    apf_draw('.\\data\\lastweek27\\CHC_20141227.csv')


    #for root, dirs, files in os.walk('.\\data\\lastweek27\\'):
    #    for name in files:
    #        if name.endswith('.csv'):
    #            print os.path.join(root, name)
    #            try:
    #                apf_draw(os.path.join(root, name))
    #            except Exception, e:
    #                print e






   