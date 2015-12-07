import datetime
import json
import redis
import threading

from dateutil.rrule import rrule, MO, TU, WE, TH, FR,MINUTELY, DAILY,WEEKLY

from feeder import Feeder,RedisFeeder,YahooLiveFeeder
from vehicle import Vehicle
from datajobs import DataJobs
from multiprocessing import Pool

POOL = redis.ConnectionPool(host='localhost', port=6379, db=0)
r = redis.Redis(connection_pool=POOL)

#def publish_afp(*o):
#    vs = []
#    o = o[0]
#    r = redis.Redis(connection_pool=POOL)
#    for v  in o:
#        try:
#            #print v.symbol, v.afp
#            if v.afp:
#                lc,td,df,rtn,minmaxy = v.afp
#                #print minmaxy
#                his = r.zrange('{0}:h:hits'.format(v.symbol),0,-1,withscores=True)
#                vs.append({'n':v.symbol,'rtn':rtn,'td':len(td),'y':minmaxy, 'his':his})
#                v.plot_file = "./webclient/img/{0}.png"
#                v.plot_df()
#            #else:
#            #    vs.append({'n':v.symbol,'rtn':0,'td':0,'y':'', 'his':0})

#        except Exception,e:
#            print v.symbol,e

#    vs = sorted(vs,key=lambda x: x['rtn'])
#    msg = {'type':'afp','data': vs }
#    r.publish('MSG:afp',json.dumps(msg))



symbols = r.smembers('SYMBOL:NSE')

#symbols = ['INFY','DIVISLAB','HCLTECH','BPCL','PNB']
#symbols =
#['VOD.L','RDSA.L','GSK.L','BP.L','STAC.L','BARC.L','LLOY.L','AV.L','NG.L']
#symbols = ['RANBAXY']
vehicle_lst = []

def on_feedend_callback():
    print '---------------------------------------------------------------------------------'
    djobs.stop()

for s in symbols:
    vehicle_lst.append(Vehicle(s,POOL))

dt = datetime.datetime.now()
rf = RedisFeeder(POOL,keymask="{0}:m:price")
rf.run(vehicle_lst,from_time=dt - datetime.timedelta(10), feeder_time=dt )

print 'hist done'
djobs = DataJobs(vehicle_lst)

djobs.run((60 * 5),'update_afp',run_this=(Vehicle.publish_afp,(vehicle_lst,POOL)))

if __name__ == '__main__':
    yf = YahooLiveFeeder(concattxt=".NS",data='l84')

    perthread = 5

    for t in xrange(0,len(vehicle_lst),perthread):
        sublst = vehicle_lst[t:t + perthread]
        thr = threading.Thread(target=yf.run, args=(sublst,), kwargs={})
        thr.start()

    print 'In live'