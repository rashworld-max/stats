#!/usr/bin/python

'''
A module for easy querying to Google... written because
simplegoogle.py was broken! (This module still imports
some constants from simplegoogle, however.)

Differences from simplegoogle:
- Once this gets a valid result, it stops throttling the google server (don't really understand why simplegoogle chose to keep requesting the same info over and over...)
- Pass in the language parameter as a seperate argument to doGoogleSearch, not as part of restrict
- No timeouts
- More obvious that an exception occurs
- It actually works! :)

Questions:
- Currently, altgoogle requests all queries with no language parameter passed to google, which means all hits are recorded with all languages able be potentially returned... is this correct, or should altgoogle infer the language to search in from the jurisdiction in the query (which contains the license uri)?
'''

import google
from simplegoogle import licenses, languages, countries, google_api_num

google.setLicense(google_api_num)

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
    restrict = '.'.join(restrict)

    # query google, and hope all goes according to plan
    try:
        #print query, qlang, restrict # DEBUG
        if lang_flag:
            result = google.doGoogleSearch(q=query, 
                language=qlang, restrict=restrict)
        else:
            result = google.doGoogleSearch(q=query,
                restrict=restrict)
    except Exception, e:
        print 'An exception occured in altgoogle.search', e
        result = 'EXCEPTION IN ALTGOOGLE.SEARCH'
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
    return result.meta.estimatedTotalResultsCount
