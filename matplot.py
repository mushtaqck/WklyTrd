
from __future__ import print_function
import numpy
from matplotlib.mlab import csv2rec
import matplotlib.pyplot as plt
import matplotlib.cbook as cbook
from matplotlib.ticker import Formatter

datafile = cbook.get_sample_data('C:\\Users\\u0141496\\Source\\Workspaces\\Workspace\\wlkyQT\\data\\lastweek\\CG_20141219.csv', asfileobj=False)
print ('loading %s' % datafile)
r = csv2rec(datafile)[-40:]


class MyFormatter(Formatter):
    def __init__(self, dates, fmt='%Y-%m-%d'):
        self.dates = dates
        self.fmt = fmt

    def __call__(self, x, pos=0):
        'Return the label for time x at position pos'
        ind = int(round(x))
        if ind>=len(self.dates) or ind<0: return ''

        return self.dates[ind].strftime(self.fmt)

formatter = MyFormatter(r.date)

fig, ax = plt.subplots()
ax.xaxis.set_major_formatter(formatter)
ax.plot(numpy.arange(len(r)), r.price, 'o-')
fig.autofmt_xdate()
plt.show()