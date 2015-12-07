#from __future__ import print_function

import os
import uuid
import json
from random import choice

import tornado.httpserver
import tornado.web
import tornado.websocket
import tornado.ioloop
import tornado.gen

import redis
import tornadoredis
import tornadoredis.pubsub
import pandas as pd
import pickle
import numpy as np
import io


from matplotlib import pyplot as plt
from matplotlib.ticker import Formatter



try:
    import sockjs.tornado
except:
    print('Please install the sockjs-tornado package to run this demo.')
    exit(1)


# Use the synchronous redis client to publish messages to a channel
redis_client = redis.Redis()
# Create the tornadoredis.Client instance
# and use it for redis channel subscriptions
subscriber = tornadoredis.pubsub.SockJSSubscriber(tornadoredis.Client())
root = os.path.dirname(__file__) 
#C:\Users\u0141496\Source\Workspaces\Workspace\MlnTrdStrg\webclient\app.py
#root =
#'C:\\Users\\u0141496\\Source\\Workspaces\\\Workspace\\MlnTrdStrg\\webclient\\'




class PlotDateFormatter(Formatter):
    def __init__(self, dates, fmt='%Y-%m-%d %H:%M'):
        self.dates = dates
        self.fmt = fmt

    def __call__(self, x, pos=0):
        'Return the label for time x at position pos'
        ind = int(round(x))
        if ind >= len(self.dates) or ind < 0: return ''

        return self.dates[ind].strftime(self.fmt)


def genPlot(symbol):
    rdata = redis_client.get('{0}:afp:df'.format(symbol))
    lcdata = redis_client.get('{0}:afp:lc'.format(symbol))

    linecords = pickle.loads(lcdata)
    df = pd.read_json(rdata)

    formatter = PlotDateFormatter(df.index)
    
    fig, ax = plt.subplots()
    ax.xaxis.set_major_formatter(formatter)
    ax.plot(np.arange(len(df)), df['p'])

    for cord in linecords:
        plt.plot(cord[0],cord[1],color='red')

    fig.autofmt_xdate()
    plt.xlim(-10,len(df.index) + 10)
    plt.ylim(df.p.min() - 10,df.p.max() + 10)
    plt.grid(ax)

    memdata = io.BytesIO()
    plt.savefig(memdata, format='png')
    image = memdata.getvalue()
    plt.close()
    return image
        
    #t = np.linspace(0, 10, 500)
    #y = np.sin(t * freq * 2 * 3.141)
    #fig1 = plt.figure()
    #plt.plot(t, y)
    #plt.xlabel('Time [s]')
    #memdata = io.BytesIO()
    #plt.grid(True)
    #plt.savefig(memdata, format='png')
    #image = memdata.getvalue()
    #return image




class IndexPageHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("index.html", title="------(_'_)------")





class PlotHandler(tornado.web.RequestHandler):

    def get(self):
        symbol = self.get_query_argument('s')
        image = genPlot(symbol)
        self.set_header('Content-type', 'image/png')
        self.set_header('Content-length', len(image))
        self.write(image)

class GetSymbolList(tornado.web.RequestHandler):
    def get(self):
        r = redis.Redis()
        symbollst = r.keys('NSENAME:*')
        mclst = []
        for index, item in enumerate(symbollst):
            nsesymbl = r.get(item)
            mclst.append({"symbol":item.replace('NSENAME:',''),"name":nsesymbl})

        self.write(json.dumps(mclst))

class MessageHandler(sockjs.tornado.SockJSConnection):
    """
    SockJS connection handler.

    Note that there are no "on message" handlers - SockJSSubscriber class
    calls SockJSConnection.broadcast method to transfer messages
    to subscribed clients.
    """
    def on_open(self, request):      
        subscriber.subscribe(['MSG:afp','MSG:ctime','MSG:plt'],
                             self)

    def on_message(self, msg):
        print msg
        try:
            symbol,event,extra = msg.split('|')

            if event == 'q':
                chnl = 'MSG:{0}:c:price'.format(symbol.strip())
                if extra == 'true':
                    subscriber.subscribe(chnl,self)
                else:
                    subscriber.unsubscribe(chnl,self)

            if event == 'p':
                 r = redis.Redis()
                 r.hset("JOBS:GenPlot",symbol.strip(),0)

        except Exception,e:
            pass


    def on_close(self):
        pass


application = tornado.web.Application([(r'/', IndexPageHandler),
                                       (r'/plot',PlotHandler)] + sockjs.tornado.SockJSRouter(MessageHandler, '/sockjs').urls,
    template_path=root,static_path=root)


if __name__ == '__main__':
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(8888)
    print('Demo is running at 0.0.0.0:8888\n'
          'Quit the demo with CONTROL-C')
    tornado.ioloop.IOLoop.instance().start()
