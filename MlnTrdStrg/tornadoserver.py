from datetime import date
import tornado.gen
import tornado.escape
import tornado.ioloop
import tornado.web
import redis
import os
import datetime
import calendar

import json



root = os.path.dirname(__file__) + '\webclient'
 
class VersionHandler(tornado.web.RequestHandler):
    def get(self):
        response = { 'version': '1.0.0',
                     'last_build':  date.today().isoformat() }
        self.write(response)
 
class GetSymbolList(tornado.web.RequestHandler):
    def get(self):
        r = redis.Redis()
        symbollst = r.keys('NSENAME:*')
        mclst = []
        for index, item in enumerate(symbollst):
            nsesymbl = r.get(item)
            mclst.append({"symbol":item.replace('NSENAME:',''),"name":nsesymbl})

        #self.write(json.dumps(mcdictn))
        self.write(json.dumps(mclst))

class GetQuotes(tornado.web.RequestHandler):
    def get(self):
        r = redis.Redis()
        q = self.get_query_argument('q')
        t = self.get_query_argument('t')
        s = self.get_query_argument('s')
        e = self.get_query_argument('e')
        print '{0}:{1}:price'.format(q,t)
        #r.zrangebyscore('{0}:{1}:price'.format(q,t),int(s),int(e),withscores=True)
        #quotes = r.eval("return redis.call('zrangebyscore','VOLTAS:m:price','201410010915','201411010915', 'withscores')",0)

        quotes = r.eval("return redis.call('zrangebyscore','{0}:{1}:price',{2},{3},'withscores')".format(q,t,s,e),0)

        quotelst = []

        for p,dt in zip(quotes[0::2], quotes[1::2]):

            d = datetime.datetime.strptime(dt, "%Y%m%d")
            if t == 'm':
                d = datetime.datetime.strptime(dt, "%Y%m%d%H%M%S")
           

            dtm = calendar.timegm(d.utctimetuple()) * 1000 
            quotelst.append([dtm ,float(p.replace(',',''))])

       
        #self.write(json.dumps(quotelst))
        self.write(json.dumps(quotelst))


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        print root
        self.render("index.html")



application = tornado.web.Application([(r"/", MainHandler),
    (r"/version", VersionHandler),
     (r"/symbollst", GetSymbolList),
     (r"/quotes", GetQuotes)],template_path=root,static_path=root)
 
if __name__ == "__main__":
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()