import datetime
import numpy as np
import pandas as pd
import os
import redis
import json
import pickle

#from matplotlib import pyplot as plt
from apf import ApfMn,PlotDateFormatter
from collections import Counter


class Vehicle(object):
    def __init__(self, symbol,POOL):
        self.symbol = symbol
        self.name = ''
        #self.r = redis.Redis(connection_pool=POOL)
        self.r = redis.Redis()
        self.values = {}
        self.dt = datetime.datetime.now()
        self.historic_data = []
        self.current_data = []
        self.afp = None
        self.plot_file = None
        self.is_Schiff = False

        #self.r.delete(('{0}:c:hits').format(self.symbol))

    def set_last(self,dt,**kwargs):
        price_key = ('{0}:c:{1:%d%m%y}:hits').format(self.symbol,datetime.datetime.now())
        local_val = dict()

        for k in kwargs:
                local_val[k] = kwargs[k]

        try:
            if self.values.has_key('price'):
                if local_val['price'] == self.values['price']:
                    return 0
            
            self.values['price'] = local_val['price']
            self.current_data.append([dt,float(self.values['price'])])
            hits = self.r.zincrby(price_key,self.values['price'],1)

            msg = {'type':'qt','data': {'n':self.symbol, 'price':self.values['price'],'hits':hits,'dt':dt.isoformat()} }

            self.r.publish('MSG:{0}:c:price'.format(self.symbol),json.dumps(msg))
        except Exception,e:
            print e

    def update_afp(self):
        try:
            combined_data = self.historic_data + self.current_data
            if len(combined_data) > 0:
                afp = ApfMn(combined_data,freq='15min')
                self.afp = afp.run() 
                self.is_Schiff = afp.is_Schiff
        except Exception, e:
            print e
        
    def plot_df(self,show=False):
        from matplotlib import pylab as plt 

        if self.afp is None:
            print 'afp not initilized. call update afp'
            return -1

        linecords,td,df,rtn,minmaxy = self.afp

        formatter = PlotDateFormatter(df.index)
        #fig = plt.figure()
        #ax = plt.addsubplot()
        fig, ax = plt.subplots()
        ax.xaxis.set_major_formatter(formatter)
    
        ax.plot(np.arange(len(df)), df['p'])

        for cord in linecords:
            plt.plot(cord[0],cord[1],color='red')

        fig.autofmt_xdate()
        plt.xlim(-10,len(df.index) + 10)
        plt.ylim(df.p.min() - 10,df.p.max() + 10)
        plt.grid(ax)
        #if show:
        #    plt.show()
        
        #"{0}{1}.png".format("./data/",datetime.datetime.strftime(datetime.datetime.now(),'%Y%M%m%S'))
        if self.plot_file:
            save_path = self.plot_file.format(self.symbol)
            if os.path.exists(os.path.dirname(save_path)):
                plt.savefig(save_path)
                
        plt.clf()
        plt.close()

    def get_last(self,**kwargs):
        if 'only_get' in kwargs:
            return self.values[kwargs['only_get']]
        else:
            self.values()

    def set_historic_data(self,lwdf,range_format):
        self.historic_data = []

        r = self.r
        key = '{0}:h:hits'.format(self.symbol)


        for h in lwdf:
            self.historic_data.append([datetime.datetime.strptime(repr(h[1]),range_format + '.0'),float(h[0].replace(',',''))])
        
        r.delete(key)

        hits = map(lambda x:x[1],self.historic_data)

        hits = Counter(hits)

        for hit in hits:
            r.zadd(key,hit,hits[hit])


        print 'hist data--', len(self.historic_data),key

    @staticmethod
    def publish_afp(args):
        o,POOL = args
        r = redis.Redis(connection_pool=POOL)
        vs = []

        print "update afp",datetime.datetime.now()
        todaysdate = "{0:%d%m%y}".format(datetime.datetime.now())
        for v  in o:
            try:
                #print v.symbol, v.afp
                if v.afp:
                    lc,td,df,rtn,minmaxy = v.afp
                    r.set('{0}:afp:df'.format(v.symbol),df.to_json())
                    r.set('{0}:afp:lc'.format(v.symbol),pickle.dumps(lc))
                    his = r.zrange('{0}:h:hits'.format(v.symbol),0,-1,withscores=True)
                    cur = r.zrange('{0}:c:{1}:hits'.format(v.symbol,todaysdate),0,-1,withscores=True)

                    vs.append({'n':v.symbol,'rtn':rtn,'td':len(td),'y':minmaxy, 'his':his, 'cur':cur})
                    #v.plot_file = "./webclient/img/{0}.png"
                    #v.plot_df()
            except Exception,e:
                print v.symbol,e

        vs = sorted(vs,key=lambda x: x['rtn'])
        msg = {'type':'afp','data': vs }
        r.publish('MSG:afp',json.dumps(msg))

    @staticmethod
    def generate_plot(args):
        o,POOL,fileformat = args
        r = redis.Redis(connection_pool=POOL)

        plot_job = r.hgetall("JOBS:GenPlot")

        plot_job = dict((k, v) for k, v in plot_job.items() if v == '0')

        if len(plot_job) > 0:
            vs = []

            print "generate plot",datetime.datetime.now()
            for v  in o:
                try:
                    if v.symbol in plot_job:
                        if v.afp:
                            lc,td,df,rtn,minmaxy = v.afp
                            v.plot_file = fileformat
                            v.plot_df()
                            r.hset("JOBS:GenPlot",v.symbol,1)
                            vs.append(v.symbol)

                except Exception,e:
                    print v.symbol,e
            if len(vs) > 0:
                msg = {'type':'plt','data': vs }
                r.publish('MSG:plt',json.dumps(msg))




class VehiclesStats(object):
    def __init__(self, *args, **kwargs):
        return super(VehiclesStats, self).__init__(*args, **kwargs)

