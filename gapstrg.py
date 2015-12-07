import matplotlib
import datetime
import redis
from dateutil.rrule import rrule, DAILY, MO, TU, WE, TH, FR,MINUTELY
import matplotlib.pyplot as plt


r = redis.StrictRedis(host='localhost', port=6379, db=0)


start_date = datetime.datetime.strptime('2014-10-10', '%Y-%m-%d')
end_date = datetime.datetime.strptime('2014-12-02', '%Y-%m-%d')   
symbols = r.smembers('SYMBOL:NSE')
#symbols = r.zrangebyscore('SYMBOL:NSE',2,3000)
gaplst = {}


for dt in rrule(DAILY, dtstart=start_date, until=end_date, byweekday=(MO,TU,WE,TH,FR)):
    sdt = int(dt.strftime('%Y%m%d'))
    for s in symbols:
        ar = r.zrangebyscore('{0}:d:full'.format(s),sdt,sdt,withscores=False)
        if len(ar) > 0:
            #print ar
            v = ar[0].split(',')[:-1]
            if len(v) > 0:
                prev_close = float(v[5])
                open = float(v[0])
                gap = prev_close - open
                dif_per = (gap * 100) / prev_close
                #print dif_per
                if dif_per > 2 or dif_per < -2:
                    print '[x] {0} , {1}, {2} '.format(sdt, s ,dif_per)
                    gaplst[sdt] = s
                    mar = r.zrangebyscore('{0}:m:price'.format(s), int(str(sdt) + '0915')
                          ,int(str(sdt) + '1000')
                          ,withscores=True)
                    print mar


#for g in enumerate(gaplst):
#    print '[>>] {0}  {1}'.format(gaplst[g[1]], g[1])
#    mar = r.zrangebyscore('{0}:m:price'.format(s), int(str(g[1]) + '0915')
#                          ,int(str(g[1]) + '1115')
#                          ,withscores=True)
#    print mar
 


