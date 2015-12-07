import httplib
import zipfile
import datetime
import StringIO
from dateutil.rrule import rrule, DAILY, MO, TU, WE, TH, FR

   

# def downloadnsedata(self,start_date, end_date,download_path):
#     urlptrn = 'http://www.nseindia.com/content/historical/EQUITIES/{0}/{1}/cm{2}{1}{0}bhav.csv.zip'
#     for dt in rrule(DAILY, dtstart=start_date, until=end_date, byweekday=(MO,TU,WE,TH,FR)):
#         csv = self.getCSVFile(dt.strftime('%b').upper(),dt.year,dt.day)
#         print csv

def getCSVFile(month='JUL', year=2010, dd=07, save_file=False):
    """ Downloads the CSV Bhavcopy for the date given. If save_file is True
    saves the csv file locally as well"""

    # conn = httplib.HTTPConnection('10.23.28.130', '8080')
    conn = httplib.HTTPConnection("www.nseindia.com")
    # conn.set_tunnel("www.nseindia.com")
    reqstr = "/content/historical/EQUITIES/%d/%s/cm%02d%s%dbhav.csv.zip" % (year, month, dd, month, year) 
    print reqstr
    headers = {   'User-Agent':'Mozilla/5.0 (Windows; U; Windows NT 6.0; en-US) AppleWebKit/534.7 (KHTML, like Gecko) Chrome/7.0.517.44 Safari/534.7',
                    'Accept':'application/xml,application/xhtml+xml,text/html;q=0.9,text/plain;q=0.8,image/png,*/*;q=0.5',
                    'Accept-Encoding':'gzip,deflate,sdch',
                    'Referer':'http://www.nseindia.com/archives/archives.htm'}
    # print reqstr
    conn.request("GET", reqstr, None, headers)
    response = conn.getresponse()

    if response.status != 200:
        return None
    
    data = response.read()

    sdata = StringIO.StringIO(data)

    z = zipfile.ZipFile(sdata)

    csv = z.read(z.namelist()[0])

    return csv


# if __name__ == '__main__':
#     n = nsedatadownloder()
#     start_date = datetime.datetime.strptime('2014-01-01', '%Y-%m-%d')
#     end_date = datetime.datetime.strptime('2014-01-01', '%Y-%m-%d')
#     n.downloadnsedata(start_date,end_date,'.')


        






