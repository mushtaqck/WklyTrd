import desir
import datetime
from detect_peaks  import detect_peaks


r = desir.Redis(host='localhost', port=6379, db=0)



#x =  r.zrangebyscore('ONGC:m:price',201411010000,201411200000)
quotes = r.eval("return redis.call('zrangebyscore','VOLTAS:m:price','201410010915','201411010915', 'withscores')",0)


quotelst = []

for p,dt in zip(quotes[0::2], quotes[1::2]):
    d = datetime.datetime.strptime(dt, "%Y%m%d%H%M%S") 
    quotelst.append([float(p.replace(',','')),d])

#x = map(lambda v: v.replace(',',''),x)  

x = map(lambda v: v[0],quotelst)  

print x

ind = detect_peaks(x,valley=False,mpd=30, show=True)

#xA = map(lambda v: quotelst[v], ind)

#print xA