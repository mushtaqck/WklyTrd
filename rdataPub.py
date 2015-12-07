import redis
import datetime
import calendar
import os  
from dateutil.rrule import rrule, DAILY, MO, TU, WE, TH, FR
from time import sleep 


r = redis.StrictRedis(host='localhost', port=6379, db=0)
symbols = r.zrangebyscore('SYMBOL',2,10)

start_date = datetime.datetime.strptime('2014-10-08', '%Y-%m-%d')
end_date = datetime.datetime.strptime('2014-11-18', '%Y-%m-%d')    
for dt in rrule(DAILY, dtstart=start_date, until=end_date, byweekday=(MO,TU,WE,TH,FR)):
    sdt = int(dt.strftime('%Y%m%d'))
    msg = '{0}:'.format(sdt)
    for s in symbols:
        ar = r.zrangebyscore('{0}:d:price'.format(s),sdt,sdt,withscores=False)
        if(len(ar) > 0):
            msg += '{0},{1}:'.format(s,ar[0]);    
    print msg
    r.publish('nse',msg)
    sleep(1)


