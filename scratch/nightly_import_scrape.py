#!/usr/bin/python

from BeautifulSoup import BeautifulSoup
from sqlalchemy.ext.sqlsoup import SqlSoup
import urllib2
import re
import datetime
import sys
sys.path.append('..')
import dbconfig


def scrape_scratch(query):
    '''Scrape scratch.mit.edu for project count'''
    page = urllib2.urlopen(query).read()
    soup = BeautifulSoup(page)
    regex = re.compile('([0-9,]+)\s+projects\s+uploaded,')
    count_part = soup.firstText(regex)
    if count_part:
        count = regex.match(count_part.strip()).group(1)
        return int(count.replace(',',''))
    else:
        raise Exception, "No project count found at Scratch!" 


def main(query):
    # Extract a UTC datetime object
    utc_datetime = datetime.datetime.utcnow()
    # Connect to the DB; if we can't, this will fail anyway.
    db = SqlSoup(dbconfig.dburl)
    # Scrape for PDM count
    count = scrape_scratch(query)

    # Build a db row
    row = {}
    row['utc_time_stamp'] = utc_datetime
    row['site'] = 'http://stats.scratch.mit.edu/community/'
    row['license_uri'] = 'http://creativecommons.org/licenses/by-sa/2.0/'
    row['count'] = count

    # Insert count into site_specific table
    db.site_specific.insert(**row)
    db.flush()


if __name__ == '__main__':
    url = 'http://stats.scratch.mit.edu/community/'
    main(url) 
