#!/usr/bin/python

## CONFIG:
FLICKR_DATA_BASE_PATH='/home/paulproteus/stats/flickr/data/'

## CODE

import charts
import csv

flickr2license = {
    '/creativecommons/by-nd-2.0/': 'http://creativecommons.org/licenses/by-nd/2.0/',
    '/creativecommons/by-nc-2.0/': 'http://creativecommons.org/licenses/by-nc/2.0/',
    '/creativecommons/by-2.0/': 'http://creativecommons.org/licenses/by/2.0/',
    '/creativecommons/by-nc-nd-2.0/': 'http://creativecommons.org/licenses/by-nc-nd/2.0/',
    '/creativecommons/by-sa-2.0/': 'http://creativecommons.org/licenses/by-sa/2.0/',
    '/creativecommons/by-nc-sa-2.0/': 'http://creativecommons.org/licenses/by-nc-sa/2.0/'}

# charts.search_engines
# charts.db

def last_flickr_estimate():
    pass

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

    print license2num

if __name__ == '__main__':
    generate_estimates()

