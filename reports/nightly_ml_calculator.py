#!/usr/bin/python

## CONFIG:
FLICKR_DATA_BASE_PATH = '/home/paulproteus/stats/flickr/data/'
OUTPUT_BASE_PATH = '/home/paulproteus/public_html/stats/ml-minimum-estimate/'

## CODE

import datetime
import nightly_flickr_calculator
import charts
import sys
sys.path.append('..')
import minimum_estimate

# in general,
def generate_estimates():
    '''Loop over the search engines and run generate_estimate.'''
    flickr_data = nightly_flickr_calculator.last_flickr_estimate()
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

