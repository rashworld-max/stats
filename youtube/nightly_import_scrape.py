#!/usr/bin/python

from BeautifulSoup import BeautifulSoup
from sqlalchemy.ext.sqlsoup import SqlSoup
import urllib2
import re
import datetime
import sys
sys.path.append('..')
import dbconfig


def scrape_youtube(query):
    '''Scrape YouTube for CC content (BY 3.0)'''
    page = urllib2.urlopen(query).read()
    soup = BeautifulSoup(page)
    regex = re.compile('About <strong>(.*?)</strong> results')
    count = soup.find('p', 'num-results').strong.string
    if count:
        return int(count.replace(',',''))
    else:
        raise Exception, "No count found at YouTube for: " + query


def main(license,query):
    # Extract a UTC datetime object
    utc_datetime = datetime.datetime.utcnow()
    # Connect to the DB; if we can't, this will fail anyway.
    db = SqlSoup(dbconfig.dburl)
    # Scrape for CC-BY and all count.
    count = scrape_youtube(query)

    # Build a db row
    row = {}
    row['utc_time_stamp'] = utc_datetime
    row['site'] = 'http://www.youtube.com/'
    row['license_uri'] = license
    row['count'] = count

    # Insert count into site_specific table
    db.site_specific.insert(**row)
    db.flush()


if __name__ == '__main__':
    # Fetches count for CC-BY content on YouTube
    search_ccby = { 'license' : 'http://creativecommons.org/licenses/by/3.0/',
        'query' : 'https://www.youtube.com/results?creativecommons=1'}
    # Fetches count for ALL content on YouTube
    search_all = { 'license' : 'Count of ALL YouTube videos, not just CC',
        'query' : 'https://www.youtube.com/results'}
    main(**search_ccby)
    main(**search_all)
