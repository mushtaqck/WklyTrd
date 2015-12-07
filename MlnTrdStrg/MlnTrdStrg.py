import datetime
import json
import redis

from dateutil.rrule import rrule, MO, TU, WE, TH, FR,MINUTELY, DAILY,WEEKLY

from feeder import Feeder,RedisFeeder
from vehicle import Vehicle
from datajobs import DataJobs





start_date = datetime.datetime.now() - datetime.timedelta(107)
end_date = datetime.datetime.now() - datetime.timedelta(40)


POOL = redis.ConnectionPool(host='localhost', port=6379, db=0)
r = redis.Redis(connection_pool=POOL)


symbols = r.smembers('SYMBOL:NSE')

#symbols = ['INFY','DIVISLAB','HCLTECH','BPCL','PNB']
for dt in rrule(DAILY, dtstart=start_date, until=end_date, byweekday=(MO,TU,WE,TH,FR)):
    vehicle_lst = []

    def on_feedend_callback():
        print '---------------------------------------------------------------------------------'
        djobs.stop()

    for s in symbols:
        vehicle_lst.append(Vehicle(s,POOL))

    dt = dt.replace(hour=9,minute=15)
    rf = RedisFeeder(POOL,keymask="{0}:m:price")
    rf.run(vehicle_lst,from_time=dt - datetime.timedelta(20), feeder_time=dt - datetime.timedelta(1))

    print 'hist done'

    rf = RedisFeeder(POOL,keymask="{0}:m:price")
    djobs = DataJobs(vehicle_lst)
    fd = Feeder(rf,vehicle_lst,feeder_time=dt, feed_increment=(1),on_feed_cancel=on_feedend_callback)
    fd.run(1)
    djobs.run(75,'update_afp',run_this=(Vehicle.publish_afp,(vehicle_lst,POOL)))

    #djobplot = DataJobs(vehicle_lst)
    #djobs.run(30,run_this=(Vehicle.generate_plot,(vehicle_lst,POOL,'./webclient/img/{0}.png')))

    break


