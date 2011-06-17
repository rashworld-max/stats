#!/usr/bin/python

import BeautifulSoup
from sqlalchemy.ext.sqlsoup import SqlSoup
import sys
sys.path.append('..')
import argparse
import dbconfig
import datetime

#from lxml import etree
from lxml.html import parse

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
    # Extract a UTC datetime object
    utc_datetime = datetime.datetime.utcfromtimestamp(unix_time)
    # Connect to the DB; if we can't, this will fail anyway.
    db = SqlSoup(dbconfig.dburl)
    # Scrape the results we just wgetted
    license2count = parse(infd)
    # Prepare any remaining DB columns, and write a CSV summary file
    extra_data = {
        'utc_time_stamp': utc_datetime,
        'site': 'http://www.flickr.com/'}
    importable = []
    csv_values = {}
    license2flickr = dict((v,k) for k,v in flickr2license.items())
    for key in license2count:
        row = {}
        row.update(extra_data)
        row['count'] = license2count[key]
        row['license_uri'] = key
        importable.append(row)
        csv_values[license2flickr[key]] = row['count']
    if dry_run:
        print importable
        print csv_values
    else:
        # Write data to CSV file
        csv = open('./data/%s.csv.imported' % utc_datetime.date(), 'w')
        for license, count in csv_values.items():
            csv.write('%s,%d\n' % (license,count))
        csv.close()
        # Write data to database
        counts = {}
        for row in importable:
            db.site_specific.insert(**row)
            db.flush()
            counts[row['license_uri'].split('/')[4]] = row['count']

        # Sort by license code
        lic_sorted = sorted(counts)
        # Join counts (sorted) with a comma
        cnt_sorted = ','.join(map(str, [counts[key] for key in lic_sorted]))
        # Write csv data to big historical file.  WARNING: this presupposes
        # that license version and jurisdiction never change on Flickr
        hist = open('./data/counts-historical-Flickr.csv', 'a')
        hist.write(str(utc_datetime.date()) + ',Flickr,2.0,Unported,' + cnt_sorted + '\n')
        hist.close()

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
