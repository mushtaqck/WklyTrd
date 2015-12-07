import urllib2
import requests
from bs4 import BeautifulSoup




txt = open('C:\\nsedata\\cmpname.txt','r')
url = 'http://www.nseindia.com/live_market/dynaContent/live_watch/get_quote/ajaxCompanySearch.jsp?search={0}'
ln = txt.read().splitlines()

for l in ln:
    response =  requests.get(url.format(l.replace(' ','%20')))
    soup = BeautifulSoup(response.text)
    spans = soup.find_all('span', attrs={'class':'symbol'})
    if len(spans) > 0:
        print spans[0].get_text()
    else:
        print ''
    #break

