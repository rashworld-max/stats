"""
Read linkback CSV data.
"""
import urllib2
import csv
import datetime
import re
import gzip
import StringIO

DAILY_CSV_NAME = 'linkbacks-daily-Yahoo.csv'
CSV_DUMPS_URL = "http://a6.creativecommons.org/~paulproteus/csv-dumps/"
if CSV_DUMPS_URL[-1] <> '/':
    CSV_DUMPS_URL += '/'

_ONEDAY = datetime.timedelta(days=1)

#_TODAY = datetime.date.today()
_TODAY = datetime.date(2009,3,23)

def read_csv(csvfile):
    """
    Read CSV from remote URL or local file.
    >>> r = read_csv('http://a6.creativecommons.org/~paulproteus/csv-dumps/2009-03-23/00:05:18/linkbacks-daily-ALL.csv')
    >>> r # doctest: +ELLIPSIS
    <_csv.reader object at ...>
    """
    if '://' in csvfile:
        # is URL
        f = urlopen(csvfile)
        f = StringIO.StringIO(f.read()) # So we can feed it to gzip.GzipFile
    else:
        f = open(csvfile)
    f = open_even_if_gzipped(f)
    r = csv.reader(f)
    return r

def most_recent():
    """
    Read the most recent daily data.

    >>> most_recent() # doctest: +ELLIPSIS
    <_csv.reader object at ...>
    """    
    day = _TODAY
    tries = 0
    while True:
        dayurl = CSV_DUMPS_URL + day.strftime("%Y-%m-%d") + '/'
        try:
            daypage = urlopen(dayurl, ntries=1)
            break
        except urllib2.HTTPError:
            tries += 1
            if tries > 7:
                raise
            day = day - _ONEDAY

    # Find out the link with is a timestamp like this:
    # <td><a href="./00:05:18/">00:05:18/</a>
    page = daypage.read()
    m=re.search('\<a href="\./(?P<time>\d\d:\d\d:\d\d/)"\>', page)
    time = m.groupdict()['time'] # time is like '00:05:18/'

    csvurl = dayurl + time + DAILY_CSV_NAME
    r = read_csv(csvurl)
    return r
    

def open_even_if_gzipped(fileobj):
    '''Input: file object
    Output: Read-only file object, undoing gzip compression if necessary'''
    try:
        plaintext_fd = gzip.GzipFile(mode='r', fileobj=fileobj)
        plaintext_fd.seek(1)
        plaintext_fd.seek(0)
    except IOError:
        plaintext_fd = fileobj

    return plaintext_fd

def urlopen(url, ntries=3):
    #import sys
    #print >>sys.stderr, url
    return try_thrice(ntries, urllib2.urlopen, url)

def try_thrice(ntries, fn, *arglist, **argdict):
    """
    Borrowed from Asheesh.
    """
    tries = 0
    while tries < ntries:
        try:
            return fn(*arglist, **argdict)
        except Exception, e:
            if isinstance(e, KeyboardInterrupt):
               raise e
            print "Huh, while doing %s(%s, %s), %s happened." % (fn, arglist, argdict, e)
            tries += 1
            sleeptime = 2 ** tries * 10
            print 'trying again after sleeping for %d' % sleeptime
            import time
            time.sleep(sleeptime)
            raise e


