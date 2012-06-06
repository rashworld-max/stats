#!/usr/bin/python

from BeautifulSoup import BeautifulSoup
from sqlalchemy.ext.sqlsoup import SqlSoup
import urllib2
import re
import datetime
import sys
sys.path.append('..')
import dbconfig

license_codes = ('by','by-nc','by-nc-nd','by-nc-sa','by-nd','by-sa')

def scrape_vimeo(query):
    # Extract a UTC datetime object
    utc_datetime = datetime.datetime.utcnow()
    # Connect to the DB; if we can't, this will fail anyway.
    db = SqlSoup(dbconfig.dburl)

    page = urllib2.urlopen(query).read()
    soup = BeautifulSoup(page)
    count_regex = re.compile('\+ Browse all ([0-9.]+)K videos')

    for license_code in license_codes:
        license = 'http://creativecommons.org/licenses/%s/3.0/' % license_code
        count_href = '/creativecommons/' + license_code
        count_text = soup.find('a', 'more', href=count_href).string
        count = count_regex.match(count_text).group(1)
        if count:
	    # Vimeo notates number of videos as [N]K, where N may be a floating
	    # point number, but the true number will never be floating, so just
	    # do the multiplication, then convert it to an integer.
	    real_count = int(float(count) * 1000)
            # Build a db row
            row = {}
            row['utc_time_stamp'] = utc_datetime
            row['site'] = 'http://vimeo.com/'
            row['license_uri'] = license
            row['count'] = real_count
            # Insert count into site_specific table
            db.site_specific.insert(**row)
            db.flush()
        else:
            raise Exception, "No count found at Vimeo for license: " + license


if __name__ == '__main__':
    scrape_vimeo('http://vimeo.com/creativecommons')
