#!/usr/bin/python

## CONFIG:
FLICKR_DATA_BASE_PATH = '/home/cronuser/stats/flickr/data/'
OUTPUT_BASE_PATH = '/home/cronuser/public_html/stats/flickr-based-estimate/'

## CODE

import charts
import csv
import datetime
import os.path
import sys
sys.path.append('../ankit')
import cc_total_estimate_with_comments

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

def last_flickr_estimate(as_of = None):
    '''Returns a dictionary mapping URLs to counts of photos, based
    on today's Flickr data on-disk'''
    if as_of is None:
        as_of = datetime.date.today()
    ret = {}
    try:
        flickr_csv_fd = csv.reader(
            open(os.path.join(FLICKR_DATA_BASE_PATH,
                              as_of.isoformat() + '.csv')))
    except IOError, e:
        if e.errno == 2: # file not found
            return None
        raise # what the heck IO Error was that?
    for flickr_lic, flickr_num in flickr_csv_fd:
        ret[flickr2license[flickr_lic]] = int(flickr_num)
    return ret

def fname(engine, OUTPUT_BASE_PATH=OUTPUT_BASE_PATH, date = None):
    if date is None:
        date = datetime.date.today()
    '''Returns a filename for data generated for this project and this
    search engine.'''
    date_dir = os.path.join(OUTPUT_BASE_PATH,
			    date.isoformat())
    if not os.path.isdir(date_dir):
	os.makedirs(date_dir, mode=0755)
    return os.path.join(date_dir, engine + '.txt')

# in general,
def generate_estimates():
    '''Loop over the search engines and run generate_estimate.'''
    flickr_data = last_flickr_estimate()
    for engine in charts.search_engines:
	generate_estimate(engine, flickr_data)

def generate_estimate(engine, flickr_data):
    '''Store an estimate of the total number of works, based on the Ankit
    implementation of the Giorgos method - combining search engine license
    distribution information and the Flickr data set'''
    # Flickr only refers to CC 2.0 licenses
    # Therefore, use their distribution
    all = charts.get_all_most_recent(charts.db.simple, engine, debug = False)
    license2num = {}
    all_we_care_about = [ thing for thing in all if thing.license_uri in
			  flickr2license.values() ]
    license2num = dict(
	[ (thing.license_uri, thing.count) for thing in all_we_care_about ])

    sorted_licenses = sorted(flickr2license.values())
    flickr_list = [ flickr_data[lic] for lic in sorted_licenses ]
    engine_list = [ license2num[lic] for lic in sorted_licenses ]

    scaled_list = cc_total_estimate_with_comments.cc_total_estimate(
	community_list=flickr_list, search_engine_list=engine_list)
    fd = open(fname(engine), 'w')
    csv_out = csv.writer(fd)
    sum = 0
    for index, lic in enumerate(sorted_licenses):
	csv_out.writerow([lic, scaled_list[index] ])
	sum += scaled_list[index]
    csv_out.writerow(['TOTAL', sum ])
    fd.close()

if __name__ == '__main__':
    generate_estimates()

