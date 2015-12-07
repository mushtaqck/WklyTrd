import desir
import string
import datetime
import calendar
import os  
from dateutil.rrule import rrule, DAILY, MO, TU, WE, TH, FR
import nsedatadownloder as nse


class ParseCustom():
   

    def parsemoneycontroldata(self,inptxt,indices,tm, r, symbllst):
        spltlninput = inptxt.splitlines()
       

        for ln in spltlninput:
            if str(ln).startswith('Data'):
                continue

            dataln = ln.split('#!#')
            dstm = ''
            
            if tm:
                dtm = datetime.datetime.strptime(dataln[-1].replace('"','').replace(',','')[:19],
                                                 "%Y-%m-%d %H:%M:%S")
                dstm = dtm.strftime('%Y%m%d')
                if tm == 'h': 
                    dstm = dtm.strftime('%Y%m%d%H')
                if tm == 'm':
                    dstm = dtm.strftime('%Y%m%d%H%M')

            if indices:
                r.zadd('{0}:{1}:price'.format(indices,tm),dstm,dataln[0].split('~')[0])

            for dln in dataln[1:-1]:
                datadln = dln.split('~')
                nsesymbl = symbllst.get('MC:{0}'.format(datadln[0]))

                if nsesymbl is not None:
                     r.zadd('{0}:{1}:price'.format(nsesymbl,tm),dstm,float(datadln[1].replace(',','')))
                     #r.zadd('{0}:{1}:full'.format(nsesymbl,tm),dstm,dln)
                #else:
                    #print datadln[0]


                #symbl = r.get('MC:{0}'.format(datadln[0]))

                #if symbl is None:
                    #r.zadd('{0}:{1}:price'.format(symbl,tm),dstm,datadln[1])
                    #r.zadd('{0}:{1}:full'.format(symbl,tm),dstm,dln)
                    #print dln
                    #print 'MC:{0}'.format(datadln[0])


        return 0

    def parseyahoocsv(self,inptxt,symbol,tm, r):
        #2010-12-31,1077.00,1085.50,1056.20,1075.60,333900,976.82
        #symbol:d:price yymmdd value
        spltlninput = inptxt.splitlines()[1:-1]
        for ln in spltlninput:
            dataln = ln.split(',')
            dstm = ''
            if tm:
                dtm = datetime.datetime.strptime(dataln[0], "%Y-%m-%d")
                dstm = dtm.strftime('%Y%m%d')

            r.zadd('{0}:{1}:price'.format(symbol,tm),dstm,dataln[-1])

        return 0

    def parsensecsv(self,inptxt,tm, r):
        # SYMBOL,SERIES,OPEN,HIGH,LOW,CLOSE,LAST,PREVCLOSE,TOTTRDQTY,TOTTRDVAL,TIMESTAMP,TOTALTRADES,ISIN,
        #ZENITHINFO,EQ,3.5,3.65,3.5,3.65,3.65,3.5,4669,16959.35,01-JAN-2014,13,INE899A01017,
        #symbol:d:price yymmdd value
        # print inptxt
        spltlninput = inptxt.splitlines()[1:-1]
        for ln in spltlninput:
            dataln = ln.split(',')
            dstm = ''
            if tm:
                dtm = datetime.datetime.strptime(dataln[10], "%d-%b-%Y")
                dstm = dtm.strftime('%Y%m%d')

            r.zadd('{0}:{1}:price'.format(dataln[0],tm),dstm,dataln[5])
            #r.zadd('{0}:{1}:full'.format(dataln[0],tm),dstm,'{0[2]},{0[3]},{0[4]},{0[5]},{0[6]},{0[7]},{0[8]},{0[9]},{0[11]},'.format(dataln))



        return 0


if __name__ == '__main__':
    #tstr =
    #'3260.20~7.35~0.23~1#!#MPS~296.35~4.85~1.66~296.35~200~296.55~20~121060#!#IC8~166.65~1.65~1.00~166.55~630~166.65~321~14132#!#CES~691.70~5.35~0.78~691.45~6~691.70~40~5472#!#GI27~20.50~0.15~0.74~20.45~9,727~20.50~8,006~66477#!#TPC~94.10~0.55~0.59~94.00~1,725~94.10~700~54166#!#VSN~439.80~2.40~0.55~439.35~68~439.80~65~1026#!#JE02~78.60~0.40~0.51~78.55~150~78.60~3,000~5783#!#RCV02~108.50~0.55~0.51~108.25~1,065~108.35~167~40391#!#BSE~646.30~3.05~0.47~646.30~76~646.75~98~25978#!#V~256.65~1.20~0.47~256.40~26~256.65~57~15514#!#PTC01~93.20~0.35~0.38~93.15~2,349~93.30~1,278~7393#!#BTV~386.40~1.40~0.36~386.40~91~386.45~404~23927#!#JHP01~14.55~0.05~0.34~14.55~34,990~14.60~58,650~40287#!#RP~76.05~0.25~0.33~76.00~2,256~76.05~4,816~64361#!#BHE~246.00~0.70~0.29~245.85~482~246.00~276~37657#!#N07~21.05~0.05~0.24~21.00~47,026~21.05~30,457~14423#!#S~873.60~1.15~0.13~873.55~16~874.85~22~448#!#CG~195.95~0.15~0.08~195.95~217~196.00~1,679~13843#!#IID01~274.20~0.20~0.07~274.30~218~274.40~57~21088#!#LT~1,638.00~0.80~0.05~1638.00~7~1638.35~20~8839#!#JA02~33.65~0.00~0.00~33.60~1,884~33.65~47,761~130150#!#NTP~145.75~-0.05~-0.03~145.70~488~145.75~22~16827#!#PGC~146.65~-1.00~-0.68~146.70~53~146.75~850~66422#!#,2014-11-12
    #09:15:51.580000'
    t = ParseCustom()

    r = desir.Redis()


    mclst = r.keys('MC:*')
    mcdictn = {}

    for index, item in enumerate(mclst):
        nsesymbl = r.get(item)
        mcdictn[item] = nsesymbl
    
    #print mcdictn


    for root, dirs, files in os.walk('C:\\nsedata\\NSE Data\\RUN\\'):
        for name in files:
             print os.path.join(root, name)
             with open(os.path.join(root, name), 'r') as f:
                 t.parsemoneycontroldata(f.read(),'','m',r,mcdictn)




 

    #start_date = datetime.datetime.strptime('2014-12-15', '%Y-%m-%d')
    #end_date = datetime.datetime.strptime('2015-01-10', '%Y-%m-%d')    
    #for dt in rrule(DAILY, dtstart=start_date, until=end_date, byweekday=(MO,TU,WE,TH,FR)):
    #    # print dt.strftime('%b')
    #    try:
    #        csv = nse.getCSVFile(dt.strftime('%b').upper(),dt.year,dt.day)
    #        if csv is not None:
    #            t.parsensecsv(csv,'d',r)
    #    except e:
    #        print e 




    # file = open('C:\\nsedata\NSE Data\\20141118\CNXIT.txt',    'r')
    # t.parsemoneycontroldata(file.read(),'CNXINFRA2','m',r)
    # file.close()
   
    # for root, dirs, files in os.walk('C:\SB\Yahoo\\'):
    #     for name in files:
    #         if name.endswith((".csv")):
    #             print os.path.join(root, name)
    #             with open(os.path.join(root, name), 'r') as f:
    #                 t.parseyahoocsv(f.read() ,name.split('-')[0],'d',r)



               


