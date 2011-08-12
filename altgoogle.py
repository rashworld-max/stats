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
from BeautifulSoup import BeautifulSoup
import re
import socks_monkey

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

def scrape_google(query):
    '''Scrape Google for link: counts'''
    base_url = 'http://www.google.com/search?q='
    request = urllib2.Request(base_url + urllib2.quote(query))
    opener = urllib2.build_opener()
    # Setting User-Agent to Links may prompt Google to return text/html
    user_agent = 'Links (2.3pre2; Linux 3.0.0-1-686-pae i686; text)'
    request.add_header('User-Agent', user_agent)
    socks_monkey.enable_tor()
    page = opener.open(request).read()
    socks_monkey.disable_tor()
    soup = BeautifulSoup(page)
    regex = re.compile('About (.*?) results')
    links = soup.fetchText(regex)
    if links:
        link_count = regex.match(links[0]).group(1)
        return int(link_count.replace(',',''))
    else:
        # if we can't find any links part and we have no exception,
        # then just assume that there were no links and return 0.
        return 0

