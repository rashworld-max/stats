#!/usr/bin/env python
"""
Show how to make date plots in matplotlib using date tick locators and
formatters.  See major_minor_demo1.py for more information on
controlling major and minor ticks

All matplotlib date plotting is done by converting date instances into
days since the 0001-01-01 UTC.  The conversion, tick locating and
formatting is done behind the scenes so this is most transparent to
you.  The dates module provides several converter functions date2num
and num2date

This example requires an active internet connection since it uses
yahoo finance to get the data for plotting
"""

# Set up data
from sqlalchemy.ext.sqlsoup import SqlSoup
from sqlalchemy import *
db = SqlSoup('mysql://root:@localhost/cc')
everything = db.simple.select(
    and_(db.simple.c.timestamp != None))
for thing in everything:
    if thing.timestamp == None:
        print "BUG!"
        print thing

from pylab import *
from matplotlib.finance import quotes_historical_yahoo
from matplotlib.dates import YearLocator, MonthLocator, DateFormatter
import datetime

months   = MonthLocator()  # every month
days     = DayLocator()    # daily?
monthsFmt = DateFormatter('%m')

dates = [date2num(k.timestamp) for k in everything]
opens = [k.count for k in everything]

ax = subplot(111)
plot_date(dates, opens, '-')

# format the ticks
ax.xaxis.set_major_locator(months)
ax.xaxis.set_major_formatter(monthsFmt)
ax.xaxis.set_minor_locator(days)
ax.autoscale_view()

# format the coords message box
ax.fmt_xdata = DateFormatter('%Y-%m-%d')

grid(True)
show()
