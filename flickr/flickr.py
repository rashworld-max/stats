#!/usr/bin/python

import BeautifulSoup
from sqlalchemy.ext.sqlsoup import SqlSoup
import sys
sys.path.append('..')
import argparse
import dbconfig
import datetime

flickr2license = {
    '/creativecommons/by-nd-2.0/':
        'http://creativecommons.org/licenses/by-nd/2.0/',
    '/creativecommons/by-nc-2.0/':
        'http://creativecommons.org/licenses/by-nc/2.0/',
    '/creativecommons/by-2.0/':
        'http://creativecommons.org/licenses/by/2.0/',
    '/creativecommons/by-nc-nd-2.0/':
        'http://creativecommons.org/licenses/by-nc-nd/2.0/',
    '/creativecommons/by-sa-2.0/':
        'http://creativecommons.org/licenses/by-sa/2.0/',
    '/creativecommons/by-nc-sa-2.0/':
        'http://creativecommons.org/licenses/by-nc-sa/2.0/'}

def parse(infd):
    soup = BeautifulSoup.BeautifulSoup(infd.read())
    license2count = {}
    for morecc in soup('p', {'class': 'MoreCC'}):
        number = morecc('b')[0].string.replace(',', '')
        license = morecc('a')[0]['href'] # in Flickr form, not CC form!
        assert 'by' in license # really a CC license, right?

        license2count[flickr2license[license]] = int(number)

    return license2count

def main(infd, unix_time, dry_run = False):
    # Connect to the DB; if we can't, this will fail anyway.
    db = SqlSoup(dbconfig.dburl)
    # Scrape the results we just wgetted
    license2count = parse(infd)
    # Prepare any remaining DB columns...
    utc_time_stamp = datetime.datetime.utcfromtimestamp(unix_time)
    site = 'http://www.flickr.com/'
    importable = {'utc_time_stamp': utc_time_stamp,
                  'site': site,
                  }
    importable.update(license2count)
    if dry_run:
        print importable
    else:
        db.site_specific.insert(**importable)
        db.flush()

if __name__ == '__main__':
    import sys
    parser = argparse.ArgumentParser(
        description='Take a Flickr page as stdin and store its information' +
        'the CC stats database.')
    parser.add_argument('--unix-time', type=int,
                        help='The UNIX time that indicates when the page was pulled from Flickr.')
    parser.add_argument('--dry-run', type=bool, help='Pass this if you are just testing and do not want to change the database.')

    # parse ...
    args = parser.parse_args()

    main(sys.stdin, args.unix_time, dry_run=bool(args.dry_run))
