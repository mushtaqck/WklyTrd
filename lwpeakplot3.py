import csv
import pandas as pd
import numpy as np
import os  
import redis
import datetime
import requests


from numpy import NaN, Inf, arange, isscalar, asarray, array
from matplotlib import pyplot as plt
from matplotlib.ticker import Formatter
from peakdetc import peakdet
from cStringIO import StringIO
from sys import float_info 
from math import sqrt

urldata = 'http://www.moneycontrol.com/tech_charts/nse/int/{0}.csv'
tdydt = datetime.datetime.now()

class MyFormatter(Formatter):
    def __init__(self, dates, fmt='%Y-%m-%d %H:%M'):
        self.dates = dates
        self.fmt = fmt

    def __call__(self, x, pos=0):
        'Return the label for time x at position pos'
        ind = int(round(x))
        if ind >= len(self.dates) or ind < 0: return ''

        return self.dates[ind].strftime(self.fmt)

def todays_data(mcsymbol,fn):
    try:
        print mcsymbol
        #fn =
        #'.\\data\\lastweek31\\{0}_{1}_{2}.csv'.format(mcsymbol,datetime.datetime.strftime(datetime.datetime.now(),'%Y%m%d'),'d')

        csvln = ''

        #if not os.path.exists(fn):
        csvresponse = requests.get(urldata.format(mcsymbol.lower()))          
        output = open(fn,'wb')
        output.write(csvresponse.text)
        output.close()       
        csvln = csvresponse.text.splitlines()
        #else:
        #     with open(fn,'r+') as f:
        #         csvln = f.read().splitlines()
            

        dt = csvln[0].split(',')[0]

        if dt == 'd':
            csvln = csvln[1:]
            dt = csvln[0].split(',')[0]

        for i in range(1,len(csvln)):
            csvln[i] = '{0} {1}'.format(dt,csvln[i])            
        
        csvln[0] = 'd,p,v'

        print csvln[-1]

        return csvln
    except Exception, e:
        raise 'todays_date',e
    return []

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
def basic_linear_regression(x, y):
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

def cpeaks(cdf,sidx,linecords):
    cpeak_out = []
    maxtab, mintab = peakdet(cdf[-sidx:],1)
    cxrange = np.arange(len(cdf) - sidx,len(cdf))

    lst_regression = [] 
    for cor in linecords:
        regression = basic_linear_regression(cor[0],cor[1])
        lst_regression.append(regression)


    if maxtab.any() or mintab.any():
        for m in enumerate(np.vstack((maxtab,mintab))):
            m[1][0] = cxrange[m[1][0]]
            for i,r in enumerate(lst_regression):
                #new_y = r[1][0] * m[1][0] + r[1][1]
                new_y = r[0] * m[1][0] + r[1]
                #print (new_y - (new_y * 0.001)), m[1][1],(new_y + (new_y *
                #0.001))
                if (new_y - (new_y * 0.001)) <= m[1][1] <= (new_y + (new_y * 0.001)):
                    plt.scatter(m[1][0], m[1][1], color = 'green')
                    cpeak_out.append([m[1],linecords[i]])
        
    #print cpeak_out
    return cpeak_out



def cpeaks2(cdf,sidx,linecords):
    cpeak_out = []
    cxrange = np.arange(len(cdf) - sidx,len(cdf))

    lst_regression = [] 
    for cor in linecords:
        regression = basic_linear_regression(cor[0],cor[1])
        lst_regression.append(regression)

    c_cords = [ [cxrange[x],y] for x,y in enumerate(cdf[-sidx:])]

    for c in c_cords:
        for i,r in enumerate(lst_regression):
            a = linecords[i][0]
            b = linecords[i][1]

            if c[1] >= a[1] and c[1] <= b[1]:
                new_y = r[0] * c[0] + r[1]
                if (new_y - (new_y * 0.0005)) <= c[1] <= (new_y + (new_y * 0.0005)):
                    plt.scatter(c[0], c[1], color = 'green')
                    cpeak_out.append([i,linecords[i],c])
    return cpeak_out

def apf_draw(df,symbol):
    pmin = df.p.min()
    pmax = df.p.max()
    formatter = MyFormatter(df.index)
    touch_down = []
    percent_return = 0

    fig, ax = plt.subplots()
    ax.xaxis.set_major_formatter(formatter)
    
    ax.plot(np.arange(len(df)), df['p'])

    #detect peak
    # 1 1 2 3 5 8 13 21 34
    maxtab = []
    mintab = []
    delta = [55,34,21,13,8,5,3,2,1]
    #delta = [5,3,2,1]
    deltastop = 55

    for d in delta:
        maxtab, mintab = peakdet(df['p'],d)
        if len(maxtab) > 1 and len(mintab) > 1 :
            print 'delta stop -- {0}'.format(d)
            deltastop = d
            break

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
                    linecords = []
                    bpoint = bothpeak[i + 1]
                    cpoint = bothpeak[i + 2]
                
                    mnmidx = (cpoint[0] - bpoint[0]) / 2
                    mnmidy = (cpoint[1] - bpoint[1]) / 2

                    percent_return = 100 * ((bpoint[1] - cpoint[1]) / 2) / apoint[1]

                    plt.plot([bpoint[0],cpoint[0]],[bpoint[1],cpoint[1]],color='yellow')

                    mnpoint = [mnmidx + bpoint[0],mnmidy + bpoint[1]]
                    plt.plot(mnpoint[0],mnpoint[1],'om')
                    
                    slope, intercept = np.polyfit([apoint[0],mnpoint[0]],[apoint[1],mnpoint[1]],1)
                    prdictY = slope * apoint[1] + intercept
                    
                    plt.plot(apoint[1],prdictY,'om')

                    print slope, intercept
                    mnline = [[apoint[1],apoint[0]],[prdictY,apoint[1]]]
                    plt.plot(mnline[0],mnline[1],color='orange')
                    linecords.append(mnline)

                    plt.plot(apoint[1] - mnmidx,prdictY - mnmidy,'om')
                    bmnline = [[bpoint[0],apoint[1] - mnmidx],[bpoint[1],prdictY - mnmidy]]
                    plt.plot(bmnline[0],bmnline[1],color='blue')
                    linecords.append(bmnline)
                    
                    plt.plot(apoint[1] + mnmidx,prdictY + mnmidy,'om')
                    cmnline = [[cpoint[0],apoint[1] + mnmidx],[cpoint[1],prdictY + mnmidy]]
                    plt.plot(cmnline[0],cmnline[1],color='purple')
                    linecords.append(cmnline)

                    mn2midx = (mnpoint[0] - bpoint[0]) / 2
                    mn2midy = (mnpoint[1] - bpoint[1]) / 2

                    plt.plot(mn2midx + bpoint[0],mn2midy + bpoint[1],'om')
                    plt.plot(mn2midx + mnpoint[0],mn2midy + mnpoint[1],'om')
                    
                    mnbline = [[mn2midx + bpoint[0],apoint[1] - mn2midx],[mn2midy + bpoint[1],prdictY - mn2midy]]
                    plt.plot(mnbline[0],mnbline[1],'--',color='black')
                    linecords.append(mnbline)

                    mncline = [[mn2midx + mnpoint[0],apoint[1] + mn2midx],[mn2midy + mnpoint[1],prdictY + mn2midy]]
                    plt.plot(mncline[0],mncline[1],'--',color='black')
                    linecords.append(mncline)

                    plt.xlabel('slope:{0} intercept:{1} delta:{2} '.format(slope,intercept,deltastop))
                    #print cpoint
                    #touch_down = cpeaks(df['p'],int(len(df['p']) -
                    #cpoint[0]),linecords)

                    touch_down = cpeaks2(df['p'],int(len(df['p']) - cpoint[0]),linecords)
                    #print 'touch down',touch_down

                    #break
           except Exception, e:
                print e
    fig.autofmt_xdate()
    plt.xlim(-10,len(df.index) + 10)
    plt.ylim(pmin - 10,pmax + 10)
    plt.grid(ax)
    plt.ylabel(symbol)

    try:
        tccnt = len(touch_down)
        grp_path = ".\\data\\{1:%d%m}\\{0}\\".format(tccnt,tdydt)
        
        if tccnt > 0:
            if not os.path.exists(grp_path):
                os.makedirs(grp_path)
            plt.savefig("{0}{1}.png".format(grp_path,symbol))
            print "{0}{1}.png".format(grp_path,symbol)
    except Exception,e:
        print 'write file',e

    #plt.show()
    plt.close()
   
    return touch_down
    


if __name__ == '__main__':
  #r = redis.Redis()
  #symbols = r.smembers('SYMBOL:NSE')
  ##print symbols

  #Daily chart
  #symbols = ['WHIRLPOOL','IFBIND']
  #for s in symbols:
  #    data =
  #    r.zrangebyscore('{0}:d:price'.format(s),20140101,20141227,withscores =
  #    True)
  #    pdformt = []
  #    for d in data:
  #        dt = datetime.datetime.strptime(str(d[1]),'%Y%m%d.0')
  #        pdformt.append([dt,float(d[0])])

  #    df = pd.DataFrame(map(lambda x: x[1],pdformt),index=map(lambda x:
  #                               x[0],pdformt),columns=['p'])
  #    apf_draw(df,s)
  
  #symbols = ['DIVISLAB']

  ##Minute Chart
  #freqs = '15min'
  #for s in symbols:
  #    data =
  #    r.zrangebyscore('{0}:m:price'.format(s),201412120915,201412261531,withscores=True)
  #    pdformt = []
  #    for d in data:
  #        dt = datetime.datetime.strptime(repr(d[1]),'%Y%m%d%H%M.0')
  #        pdformt.append([dt,float(d[0].replace(',',''))])
  #    if len(pdformt) > 0:
  #        df = pd.DataFrame(map(lambda x: x[1],pdformt),index=map(lambda x:
  #        x[0],pdformt),columns=['p'])
  #        df = df.resample(freqs,how='first')
  #        df = df.dropna()
  #        apf_draw(df,s)

  fltr = [ 'TC_TATACHEM_20150105_w.csv']
  stopw = datetime.datetime.now()
  print '.\\data\\lw{0:%d%m}\\'.format(tdydt)
  for root, dirs, files in os.walk('.\\data\\lw{0:%m%d}\\'.format(tdydt)):
     for name in files:
         if name.endswith('_w.csv'):
         #if name in fltr:
             fn = os.path.join(root, name)
             print fn
             try:              
                line_prepender(fn,"d,t,p,na")
                df = pd.read_csv(fn,parse_dates={'Timestamp':['d','t']},index_col='Timestamp')
                df = df.ix[1:,['p']]

                td = todays_data(name.split('_')[0],fn.replace('_w','_d'))
                if len(td) > 0:
                    tds = "\n".join(item for item in td)
                    tdf = pd.read_csv(StringIO(tds),parse_dates={'Timestamp':['d']},index_col='Timestamp')
                    df = df.append(tdf.ix[:,['p']])
                    #print tdf
                
                #resample to 15 min
                df = df.resample('15min',how='first')

                df = df.between_time('9:14','15:30')
                #drop na
                df = df.dropna()

                touchdown = apf_draw(df,name)

             except Exception, e:
                 print 'main--',e

  

               

   

 

   