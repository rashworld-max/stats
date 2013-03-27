#!/usr/bin/python

from BeautifulSoup import BeautifulSoup
from sqlalchemy.ext.sqlsoup import SqlSoup
import urllib2
import datetime
import sys
sys.path.append('..')
import dbconfig


def scrape_europeana_pdm(query):
    '''Scrape Europeana for PDM 1.0 count'''
    page = urllib2.urlopen(query).read()
    soup = BeautifulSoup(page)
    count_div = soup.find('div', 'count')
    count = count_div.find('span', 'of-bracket').text
    if count:
        return int(count.replace(',',''))
    else:
        raise Exception, "No PDM count found at Europeana!" 


def main(query):
    # Extract a UTC datetime object
    utc_datetime = datetime.datetime.utcnow()
    # Connect to the DB; if we can't, this will fail anyway.
    db = SqlSoup(dbconfig.dburl)
    # Scrape for PDM count
    count = scrape_europeana_pdm(query)

    # Build a db row
    row = {}
    row['utc_time_stamp'] = utc_datetime
    row['site'] = 'http://europeana.eu/'
    row['license_uri'] = 'http://creativecommons.org/publicdomain/mark/1.0/'
    row['count'] = count

    # Insert count into site_specific table
    db.site_specific.insert(**row)
    db.flush()


if __name__ == '__main__':
    url = 'http://europeana.eu/portal/search.html?query=*:*&qf=RIGHTS:http://creativecommons.org/publicdomain/mark/1.0/&view=table&wpfv=N'
    main(url) 
