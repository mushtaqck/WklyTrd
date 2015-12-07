import requests
import json




txt = open('C:\\nsedata\\cmpname.txt','r')
url = 'https://www.google.com/finance/match?matchtype=matchall&ei=9iZ6VJGqDIiTlAW_v4E4&q={0}'
ln = txt.read().splitlines()

for l in ln:
    response =  requests.get(url.format(l.replace(' ','%20')))
    jsondata = json.loads(response.text)
    symbol = ''
    for itm in jsondata['matches']:
        if itm['e'] == 'NSE':
            symbol = itm['t']
    

    print symbol


