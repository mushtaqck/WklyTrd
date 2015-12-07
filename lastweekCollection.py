# http://www.moneycontrol.com/mccode/common/autosuggesion.php?query=techm&type=1&format=json&callback=suggest1

import Queue
import requests
import json
import datetime
import threading
import os


from multiprocessing import Pool




url = 'http://www.moneycontrol.com/mccode/common/autosuggesion.php?query={0}&type=1&format=json&callback=suggest1'
urldata = 'http://www.moneycontrol.com/tech_charts/nse/week/{0}.csv'
urldata2 = 'http://www.moneycontrol.com/tech_charts/bse/int/{0}.csv' 

tdydt = datetime.datetime.now()
base_path = ('.\\data\\lw{0:%m%d}'.format(tdydt))

if not os.path.exists(base_path):
    os.makedirs(base_path)


def downloadcsv(mcsymbol,url,fn):
    try:
        #print mcsymbol,fn
        csvresponse = requests.get(url.format(mcsymbol.lower()),proxies=None)  
        if len(csvresponse.text) > 0:
            output = open('{3}\{0}_{1}_{2:%Y%m%d}_w.csv'.format(mcsymbol,fn,tdydt,base_path),'wb')
            output.write(csvresponse.text)
            output.close()
    except Exception, e:
        print mcsymbol,fn
        #raise e

def getweeksdata(l):
    #print l
    #l = ln[i]
    #print response.text
    try:
        response = requests.get(url.format(l.replace(' ','%20')))

        resp = response.text.replace('suggest1(','').replace('])',']')
        jsondata = json.loads(resp.decode('utf8'))       

        for j in jsondata:
            if l in j['pdt_dis_nm']:
                #print j['link_src']
                mcsymbol = j['link_src'].split('/')[-1]
                if mcsymbol is not None:
                     try:
                         downloadcsv(mcsymbol,urldata,l)
                         #downloadcsv(mcsymbol,urldata2,'t')
                     except Exception,c:
                         #downloadcsv(mcsymbol[:-2],urldata,l)
                         #downloadcsv(mcsymbol[:-2],urldata,'w')
                         pass
                         #downloadcsv(mcsymbol[:-2],urldata2,'t')
            break
    except Exception, e:
        print e
    return l


if __name__ == '__main__':

    #ln = "PERSISTENT\nJUBLFOOD".splitlines()
    #for l in ln:
    #    getweeksdata(l)
    
    srcfile = "C:\\redis\\nsesymbl.csv"
    txt = open(srcfile,'r')
    ln = txt.read().splitlines()



    for l in ln:
        t = threading.Thread(target=getweeksdata,args=(l,))
        t.daemon = True
        t.start()
        #break
    
    #pool = Pool()

    #pool.map(getweeksdata,['PERSISTENT'])
    #pool.start()
    #pool.join()
   





#ln = "WHIRLPOOL\n".splitlines()
#for l in ln:
#    print l
#    response = requests.get(url.format(l.replace(' ','%20')))
#    #print response.text
#    try:
#        resp = response.text.replace('suggest1(','').replace('])',']')
#        jsondata = json.loads(resp.decode('utf8'))       

#        for j in jsondata:
#            if l in j['pdt_dis_nm']:
#                #print j['link_src']
#                mcsymbol = j['link_src'].split('/')[-1]
#                if mcsymbol is not None:
#                     try:
#                         downloadcsv(mcsymbol,urldata,'w')da
#                         downloadcsv(mcsymbol,urldata2,'t')
#                     except Exception,c:
#                         downloadcsv(mcsymbol[:-2],urldata,'w')
#                         downloadcsv(mcsymbol[:-2],urldata2,'t')                                              
#    except Exception, e:
#        print e
    #break

