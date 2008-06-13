#!/usr/bin/python

## CONFIG:
FLICKR_DATA_BASE_PATH='/home/paulproteus/stats/flickr/data/'
OUTPUT_BASE_PATH='/home/paulproteus/public_html/stats/flickr-based-estimate/'

## CODE

import charts
import csv
import datetime
import os.path

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

def last_flickr_estimate():
    ret = {}
    flickr_csv_fd = csv.reader(
        open(os.path.join(FLICKR_DATA_BASE_PATH,
			  datetime.date.today().isoformat() + '.csv')))
    for flickr_lic, flickr_num in flickr_csv_fd:
        ret[flickr2license[flickr_lic]] = int(flickr_num)
    return ret

def fname(engine):
    return os.path.join(OUTPUT_BASE_PATH, engine + '.txt')

# in general,
def generate_estimates():
    flickr_data = last_flickr_estimate()
    for engine in charts.search_engines:
	generate_estimate(engine, flickr_data)

def generate_estimate(engine, flickr_data):
    # Flickr only refers to CC 2.0 licenses
    # Therefore, use their distribution
    all = charts.get_all_most_recent(charts.db.simple, engine)
    license2num = {}
    all_we_care_about = [ thing for thing in all if thing.license_uri in
			  flickr2license.values() ]
    license2num = dict(
	[ (thing.license_uri, thing.count) for thing in all_we_care_about ])

    fd = open(fname(engine), 'w')
    fd.write('wtf')
    fd.close()

    print license2num

if __name__ == '__main__':
    generate_estimates()

