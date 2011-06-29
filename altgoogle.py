#!/usr/bin/python

'''
A module for querying Google's JSON/Atom Custom Search API.
http://code.google.com/apis/customsearch/v1/getting_started.html
Written because the old SOAP API is retired, and even the
Web Search API is deprecated.  This appears to be the latest
API, and is even still in "labs" status as I write this.
'''

import json
import urllib2
from simplegoogle import licenses, languages, countries, google_api_num, google_cx_num

base_request = 'https://www.googleapis.com/customsearch/v1?' + \
                   'cx=' +  google_cx_num + '&key=' + google_api_num

def search(query, cc_spec=[], country=None, language=None):
    ''' Performs a Google search for a given query and 
    options and returns the result as a SearchReturnValue. '''

    # check that all the cc_spec members are valid
    if cc_spec != []:
        for cc_thing in cc_spec: 
            assert(cc_thing in licenses)

    # deal with language (if it is specified) and also
    # the restrict parameter, which includes country, and cc_spec
    result = None
    lang_flag = False
    restrict = cc_spec[:]
    if language:
        qlang = languages[language]
        lang_flag = True
    if country:
        restrict.append(countries[country])
    restrict = '|'.join(restrict)

    # query google, and hope all goes according to plan
    try:
        request = base_request + '&q=' + query
        if restrict:
            request = request + '&as_rights=%28' + restrict + '%29'
        raw_result = urllib2.urlopen(request).read()
        result = json.loads(raw_result)
    except Exception, e:
        print 'An exception occured in altgoogle.search', e
        print 'Request was: ' + request
        result = 'EXCEPTION IN ALTGOOGLE.SEARCH'
    #return request
    return result
    
def count(query, cc_spec=[], country=None, language=None):
    ''' Counts the number of queries that google produces
    for a given query and parameters. '''
    try:
        #print query, cc_spec, country, language # DEBUG
        result = search(query, cc_spec, country, language)
    except Exception, e:
        print 'An exception occured in altgoogle.count', e
        return 'EXCEPTION IN ALTGOOGLE.COUNT'
    return result['queries']['request'][0]['totalResults']
