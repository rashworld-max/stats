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
    flickr_data = nightly_flickr_calculator.last_flickr_estimate()
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
    for uri_bunch in equivalent_uris:
        winner_val, winner_uri = max( [ (uri2value[uri], uri) for uri in uri_bunch ] )
        # that means drop the others
        for loser_uri in uri_bunch:
            if loser_uri != winner_uri:
                del uri2value[loser_uri]
    return uri2value

def write_data_to_csv_for_engine(engine, uri2value):
    filename = nightly_flickr_calculator.fname(engine, OUTPUT_BASE_PATH)
    fd = open(filename, 'w')
    csv_out = csv.writer(fd)
    sum = 0

    for uri in sorted(uri2value.keys()):
        val = uri2value[uri]
        csv_out.writerow( [uri, val] )
        sum += val
    csv_out.writerow( ['TOTAL', sum ])
    fd.close()

def generate_estimate(engine, flickr_data, date):
    '''Store an estimate of the total number of works, based on the Ankit
    implementation of the Giorgos method - combining search engine license
    distribution information and the Flickr data set'''
    # Flickr only refers to CC 2.0 licenses
    # Therefore, use their distribution
    all_as_generator = charts.get_all_most_recent(charts.db.simple, engine, debug = False)
    data_from_engine = dict( [ (data['license_uri'], data['count']) for data in all_as_generator ] )
    cleaned_data_from_engine = cleanup_dup_keys(data_from_engine)
    merged_dicts = minimum_estimate.merge_dicts_max_keys(cleaned_data_from_engine, flickr_data)
    write_data_to_csv_for_engine(engine, merged_dicts)

if __name__ == '__main__':
    import datetime
    yesterday = datetime.date.today() - datetime.timedelta(days=1)
    generate_estimates(yesterday)

