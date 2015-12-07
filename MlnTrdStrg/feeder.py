import threading  
import datetime
import json

from  multiprocessing import Pool

from vehicle import Vehicle


class Feeder(object):
    
    weekend = set([5,6])

    def __init__(self,source_feeder,vehicle_list,**kwargs):
        self.source_feeder = source_feeder
        self.vehicle_list = vehicle_list
        self.worker = None
        self.dt = datetime.datetime.now()
        self.canceldt = datetime.datetime.now()
        self.cancel_callback = None
        
        self.increment = 0

        if  'feeder_time' in kwargs:
            self.dt = kwargs['feeder_time']

        if  'cancel_time' in kwargs:
            self.canceldt = kwargs['cancel_time']
        else:
            self.canceldt = self.dt.replace(hour=15,minute=31)

        if  'feed_increment' in kwargs:
            self.increment = kwargs['feed_increment']

        if  'on_feed_cancel' in kwargs:
            self.cancel_callback = kwargs['on_feed_cancel']


    def validTradingTime(self,dt):
        
        def nextTrading(dt):
            dt = (dt + datetime.timedelta(1)).replace(hour=9,minute=15)
            return dt
        
        if not datetime.time(9, 15,0,0) < dt.time() < datetime.time(15, 30,0,0):
            dt = nextTrading(dt)

        while  dt.weekday() in self.weekend:
            dt = nextTrading(dt)

        return dt    

    def run(self, frequency):
        if self.increment == 0:
            self.increment = frequency

        def schedule():
            self.dt = self.validTradingTime(self.dt + datetime.timedelta(minutes=self.increment))
            if self.dt > self.canceldt:
                print 'Cancel time {0}'.format(self.canceldt)
                self.worker.cancel()
                if self.cancel_callback:
                    self.cancel_callback()
                return -1
            
            self.source_feeder.run(self.vehicle_list,feeder_time=self.dt)
            self.worker = threading.Timer(frequency,schedule)
            self.worker.start()


        schedule()
#----------------------------------------------------------------------------------------------
    def stop(self):
        if self.worker:
            self.worker.cancel()
        else:
            print 'worker not initialized'

class FeedFrequency:
    Daily1S = 1
    Daily5S = 2
    Daily10S = 3
    Daily20S = 4
    Daily30S = 5
    Daily1M = 6
    LastWeek = 7
    
import redis
class RedisFeeder(object):
    def __init__(self,POOL,**kwargs):
        #to-do handle redis instance
        self.r = redis.Redis(connection_pool=POOL)

        self.range_format = '%Y%m%d%H%M'
        self.last_max = 0


        if  'keymask' in kwargs:
            self.keymask = kwargs['keymask']
            if ':d:' in self.keymask:
                self.range_format = '%Y%m%d'
        else:
            self.keymask = None

    def run(self,vehicle_lst, **kwargs):
        r = self.r
        end_dt = datetime.datetime.now()
        start_dt = datetime.datetime.now()
        historic_date = False


        if  'feeder_time' in kwargs:
            end_dt = kwargs['feeder_time']

        max = int(datetime.datetime.strftime(end_dt,self.range_format))


        msg = {'type':'ctime','data': '{0:%d-%m-%y %H:%M}'.format(end_dt) }

        r.publish('MSG:ctime', json.dumps(msg))

        if  'from_time' in kwargs:
            start_dt = kwargs['from_time']
            min = int(datetime.datetime.strftime(start_dt,self.range_format))
            historic_date = True
        else:
            min = max

        if self.last_max != 0 : min = self.last_max

        for vhcl in vehicle_lst:
            key = vhcl.symbol
            if self.keymask is not None:
                key = self.keymask.format(key)
            tick = r.zrangebyscore(key,min,max,withscores=True)

            if tick:
                if historic_date:
                    vhcl.set_historic_data(tick,self.range_format)
                    vhcl.update_afp()
                else:
                    val = tick[-1]
                    feed_dt = datetime.datetime.strptime(repr(val[1]),self.range_format + '.0')
                    vhcl.set_last(feed_dt,price=float(val[0].replace(',','')))
      
        self.last_max = max


class MoneyControlTerminalFeeder(object):
    def __init__(self, *args, **kwargs):
        return super(MoneyControlTerminalFeeder, self).__init__(*args, **kwargs)

    def run(self,**kwargs):
        pass


import httplib
import sys
import re
import simplejson as json
import threading
import time
class YahooLiveFeeder(object):
    STREAMER_API = "streamerapi.finance.yahoo.com"
    STREAMER_URL = ("/streamer/1.0"
                    "?s=%s"
                    "&k=%s"
                    "&callback=parent.yfs_u1f"
                    "&mktmcb=parent.yfs_mktmcb"
                    "&gencallback=parent.yfs_gencb")

    last_ping = datetime.datetime.now()

    def __init__(self, data, *args, **kwargs):

        if 'concattxt' in kwargs:
            self.concattxt = kwargs['concattxt']
        else:
            self.concattxt = ''

        self.data = data

    def open(self,vehicles,data="l10,v00"):
        
        symbols = ','.join(map(lambda s:s.symbol[:9] + self.concattxt, vehicles))

        print symbols

        conn = httplib.HTTPConnection(self.STREAMER_API)
        url = self.STREAMER_URL % (symbols, self.data)
        conn.request("GET", url)
        return conn.getresponse()

    def parse_line(self,line):
        if line.find('yfs_u1f') != -1:
            #return 'data: '+line
            #{"MSFT":{l10:"25.81",v00:"108,482,336"}}
            try:
                line = re.match(r".*?\((.*?)\)",line) # grab between the parentheses
                line = line.group(1)
                line = re.sub(r"(\w\d\d):",'"\\1":',line) # line isn't valid JSON
                return json.loads(line)
            except:
                return 'ERR: ' + line
        elif line.find('yfs_mktmcb') != -1:
            line = re.match(r".*?\((.*?)\)",line) # grab between the parentheses
            line = line.group(1)
            return json.loads(line)
        else:
            return


    def listen(self,vehicles, pretty=True):
        conn = ''
        r = self.open(vehicles,self.data) 

        line = ''

        while True:
            char = r.read(1)
            if char == '>':
                line += char
                data = self.parse_line(line)
                if data:
                    if pretty:
                        try:
                            k, v = data.items()[0]
                            #print k,v

                            for vh in vehicles:
                                if vh.symbol[:9] + self.concattxt == k:
                                    #print "%s: %s" % (k, v[self.data])
                                    vh.set_last(datetime.datetime.now(),price=v[self.data])
                                    break

                            #heartbeat_delta = datetime.datetime.now() - last_ping

                            #if heartbeat_delta.seconds > 60:
                            #    last_ping = datetime.datetime.now()
                            #    print "Ping: {0} --  {1}".format(k,v)

                        except Exception,e:
                            print('EX1',e,data)
                    else:
                         print('ELSE',data)
                line = ''
            else:
                line += char

        con.close()


    def run(self,vehicles):
        self.listen(vehicles)
        pass

