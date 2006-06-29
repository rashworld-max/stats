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
db = SqlSoup('mysql://root:@localhost/cc')
everything = db.simple.select() # screw you, RAM!
everything = [k for k in everything if not k.language] # need to figure out real SELECT
everything = [k for k in everything if k.timestamp] # need to figure out real SELECT
everything = [k for k in everything if k.count] # need to figure out real SELECT

from pylab import *
from matplotlib.finance import quotes_historical_yahoo
from matplotlib.dates import YearLocator, MonthLocator, DateFormatter
import datetime

years    = YearLocator()   # every year
months   = MonthLocator()  # every month
yearsFmt = DateFormatter('%Y')

dates = [date2num(k.timestamp) for k in everything]
opens = [k.count for k in everything]

ax = subplot(111)
plot_date(dates, opens, '-')

# format the ticks
ax.xaxis.set_major_locator(years)
ax.xaxis.set_major_formatter(yearsFmt)
ax.xaxis.set_minor_locator(months)
ax.autoscale_view()

# format the coords message box
ax.fmt_xdata = DateFormatter('%Y-%m-%d')

grid(True)
show()
