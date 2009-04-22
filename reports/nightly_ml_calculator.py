#!/usr/bin/python

## CONFIG:
FLICKR_DATA_BASE_PATH = '/home/paulproteus/stats/flickr/data/'
OUTPUT_BASE_PATH = '/home/paulproteus/public_html/stats/ml-minimum-estimate/'

## CODE
import csv
import datetime
import nightly_flickr_calculator
import charts
import sys
sys.path.append('..')
import minimum_estimate

# in general,
def generate_estimates(date):
    '''Loop over the search engines and run generate_estimate.'''
    # MAJOR FIXME: Grab  Flickr content for date
    flickr_data = nightly_flickr_calculator.last_flickr_estimate(date)
    for engine in charts.search_engines:
	generate_estimate(engine, flickr_data, date)

def cleanup_dup_keys(uri2value):
    '''returns a copy of uri2value that doesn't have "duplicate" keys'''
    uri2value = dict(uri2value)
    # FIXME: Is this a good place for this sort of cleanup?
    # when we crawl, we count linkbacks to /licenses/publicdomain *and*
    # /licenses/publicdomain/ ! Those are "equivalent", so I take whichever
    # is the max. Same with http://creativecommons.org/licenses/zero/1.0/
    # and http://creativecommons.org/publicdomain/zero/1.0/
    equivalent_uris = [
        ('http://creativecommons.org/licenses/zero/1.0/', 'http://creativecommons.org/publicdomain/zero/1.0/'),
        ('http://creativecommons.org/licenses/publicdomain', 'http://creativecommons.org/licenses/publicdomain/'),
        ]

    # Filter down the equivalent_uris list to only contain URIs actually in the desired
    # data set
    for (i, bunch) in enumerate(equivalent_uris):
        useful_bunch = tuple([uri for uri in bunch if uri in uri2value])
        if bunch != useful_bunch:
            equivalent_uris[i] = useful_bunch
            print 'turned', bunch, 'into', useful_bunch

    for uri_bunch in equivalent_uris:
        if not uri_bunch: 
            continue
        winner_val, winner_uri = max( [ (uri2value[uri], uri) for uri in uri_bunch ] )
        # that means drop the others
        for loser_uri in uri_bunch:
            if loser_uri != winner_uri:
                del uri2value[loser_uri]
    return uri2value

def write_data_to_csv_for_engine(engine, date, uri2value, methods):
    filename = nightly_flickr_calculator.fname(engine, OUTPUT_BASE_PATH, date)
    fd = open(filename, 'w')
    csv_out = csv.writer(fd)
    sum = 0

    iso_date = datetime.date(date.year, date.month, date.day).isoformat()

    for uri in sorted(uri2value.keys()):
        val = uri2value[uri]
        csv_out.writerow( [iso_date, uri, val, methods] )
        sum += val
    csv_out.writerow( [iso_date, 'TOTAL', sum, methods ])
    fd.close()

def generate_estimate(engine, flickr_data, date):
    '''Store an estimate of the total number of works, based on the Ankit
    implementation of the Giorgos method - combining search engine license
    distribution information and the Flickr data set'''
    # Flickr only refers to CC 2.0 licenses
    # Therefore, use their distribution
    methods = []
    all_as_generator = charts.get_all_most_recent(charts.db.simple, engine, debug = False,
                                                  recent_stamp = date)
    data_from_engine = dict( [ (data['license_uri'], data['count']) for data in all_as_generator ] )
    if data_from_engine:
        methods.append('Linkback')
    if flickr_data:
        methods.append('Flickr')
    good_data_sets = [k for k in (data_from_engine, flickr_data) if k is not None]
    if good_data_sets: # only do this work if we actually have any data worth using
        cleaned_data_from_engine = cleanup_dup_keys(data_from_engine)
        merged_dicts = minimum_estimate.merge_dicts_max_keys(*good_data_sets)
        write_data_to_csv_for_engine(engine, date, merged_dicts, methods=','.join(methods))

if __name__ == '__main__':
    import sys
    if len(sys.argv) == 1:
        # then operate on yesterday
        yesterday = datetime.date.today() - datetime.timedelta(days=1)
    else:
        yesterday = datetime.date(*map(int, sys.argv[1].split('-')))
    # always generate estimates
    generate_estimates(yesterday)

