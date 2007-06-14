from lxml import etree
import time
import datetime
import os
import threading
import sys

try:
    set
except:
    from sets import Set as set

global DEBUG
DEBUG = 1
DRYRUN = 0
def debug(s):
    if DEBUG:
        print s

import simpleyahoo
import altgoogle
import lc_util

from sqlalchemy.ext.sqlsoup import SqlSoup

## THINKME: Google and Yahoo both have different ways to encode CC license 
## types.  Later on, it's probably worth standardizing this somehow, or else 
## their trash gets shoved into our DB.

## FIXME: Maybe I could loop over the URIs somewhere 
## else so that I pass a URI in to the search-engine-specific things

## FIXME: Start using experiment functions

## FIXME: Do queries also while *not* using the CC APIs

## FIXME: Find 5 or so "seemingly non-biased" queries (e.g., "+a")

def parse_fields_from_uri(uri):
    '''parses the license_type, license_version and jurisdiction
    from the uri and returns it in a list in that order'''
    license_type = license_version = jurisdiction = None
    segments = uri.split('/')
    if len(segments) > 4:
        license_type = segments[4]
        if len(segments) > 5:
            license_version = segments[5]
            if len(segments) > 6:
                jurisdiction = segments[6]
    return [license_type, license_version, jurisdiction]

class LinkCounter:
    dumb_queries = ['license', 'license OR -license', 'work', 'work OR -work', 'html', 'html OR -html']
    ## TRYME: ccTLDs?

    def __init__(self, dburl, xmlpath):
        self.timestamp = datetime.datetime.now()
        self.db = SqlSoup(dburl)
        self.uris = self.parse(xmlpath)
        # We need to get a list of URIs to search for
        assert(self.uris) # These should not be empty.
        self.uris.extend(
            ['http://creativecommons.org','http://www.creativecommons.org',
             'http://creativecommons.org/licenses/publicdomain',
             'http://creativecommons.org/licenses/publicdomain/1.0/',
             'http://creativecommons.org/licenses/by-nc-nd/2.0/deed-music',
             'http://creativecommons.org/licenses/by-nd-nc/2.0/']) # These were in old but not in the XML
        self.uris = list(set(self.uris))  # eliminate duplicates

    def parse(self, xmlpath):
        ret = []
        tree2=etree.parse(xmlpath)
        root2=tree2.getroot()
        for element in root2.getiterator('version'):
            ret.append(element.get('uri'))
        return ret # I'm not sorting.  So there.

    def record(self, cc_license_uri, search_engine, count, 
        jurisdiction = None, language = None, timestamp = None):
        license_type, license_version, jurisdiction \
            = parse_fields_from_uri(cc_license_uri)
        if timestamp is None:
            timestamp = self.timestamp
        if not DRYRUN:
            self.db.simple.insert(
                license_uri=cc_license_uri, 
                search_engine=search_engine, 
                count=count, 
                timestamp = timestamp, 
                # language=language # no more language in DB
                jurisdiction = jurisdiction, 
                license_type = license_type, 
                license_version = license_version)
            self.db.flush()
        else:
            license_type = None
        debug("%s gave us %d hits via %s on %s with jurisdiction %s, " \
              "license_type %s and license_version %s" %               \
               (cc_license_uri, count, search_engine, timestamp,       \
                jurisdiction, license_type, license_version))
        #if DRYRUN:
        #    debug("FYI, this is a dry run.") # needlessly verbose

    def count_google(self):
        for uri in self.uris:
            try: # count the number of hits and record them
                count = altgoogle.count('link:%s' % uri)
                self.record(cc_license_uri=uri, search_engine='Google', 
                    count=count)
            except Exception, e:
                if isinstance(e, KeyboardInterrupt):
                    raise e
                print "Something sad happened while Googling", uri
                print e

    def count_msn(self):        
        ## Once from webtrawl
        for uri in self.uris:
            try:
                count = lc_util.try_thrice(lc_util.msn_count, 
                    "link:%s" % uri)
                # We record the specific uri, count pair in the DB
                self.record(cc_license_uri=uri, search_engine='MSN', 
                    count=count)
            except Exception, e:
                if isinstance(e, KeyboardInterrupt):
                    raise e
                print "Something sad happened while MSNing", uri
                print e

    def count_alltheweb(self):
        # These guys seem to get mad at us if we query them too fast.
        # To avoid "HTTP Error 999" (!), let's sleep(0.1) between
        # queries.  They seem to block the IP, not just the
        # user-agent.  Oops.
        for uri in self.uris:
            try:
                self.record(cc_license_uri=uri,search_engine="All The Web", 
                    count=lc_util.try_thrice(lc_util.atw_count, "link:%s" \
                    % uri))
            except Exception, e:
                if isinstance(e, KeyboardInterrupt):
                    raise e
                print "Something sad happened while ATWing", uri
                print e
            time.sleep(1) # "And, breathe."

    def count_yahoo(self):
        # No sleep here because we're APIing it up.
        for uri in self.uris:
            try:
                count = lc_util.try_thrice( \
                    simpleyahoo.legitimate_yahoo_count, uri, 'InlinkData')
                # Country is not a valid parameter for inlinkdata :-(
		# And languages get ignored! :-(
                self.record(cc_license_uri=uri,
                            search_engine='Yahoo',
                            count = count)
            except Exception, e:
                if isinstance(e, KeyboardInterrupt):
                    raise e
                print "Something sad happened while Yahooing", uri
                print e

    def specific_google_counter(self):
        """ Now instead of searching for links to a license URI,
        we use Google's built-in CC search.

        Unfortunately, it doesn't let you do a raw count, so we hack
        around that by adding up queries like -license and +license."""
        ## This is Google's idea of how to encode CC stuff.
        licenses = [["cc_publicdomain"], ["cc_attribute"], 
            ["cc_sharealike"], ["cc_noncommercial"], ["cc_nonderived"], 
            ["cc_publicdomain", "cc_attribute","cc_sharealike",
            "cc_noncommercial","cc_nonderived"]]
        for license in licenses:
            for dumb_query in self.dumb_queries:
                try:
                    count = altgoogle.count(dumb_query, cc_spec=[license])
                    self.record_complex(license_specifier=license,
                                        search_engine='Google',
                                        count=count,
                                        query=dumb_query)
                except Exception, e:
                    if isinstance(e, KeyboardInterrupt):
                        raise e
                    print "Something sad happened while Googling", license,\
                        "with query", dumb_query
                    print e
    
    def specific_yahoo_counter(self):
        """ Similar deal here as for Google's specific_counter."""
        for license in simpleyahoo.licenses:
            for dumb_query in self.dumb_queries:
                # Now, let's add languages
                # FIXME: Use simpleyahoo experiment function
                # CONSIDERME: Use yield + iterators for experiment function
                for language in [None] + simpleyahoo.languages.keys():
                    for jurisdiction in [None] + simpleyahoo.jurisdictions.keys():
                        try:
                            count = lc_util.try_thrice(
                                simpleyahoo.legitimate_yahoo_count, 
                                query=dumb_query, 
                                cc_spec=license, 
                                jurisdiction=jurisdiction, 
                                language=language) # Query with the 
                                                   # terse form
                            self.record_complex(license_specifier='&'.join(license),
                                                search_engine='Yahoo',
                                                count=count,
                                                query=dumb_query,
                                                language=language,
                                                country=jurisdiction) 
                        except Exception, e:
                            if isinstance(e, KeyboardInterrupt):
                                raise e
                            print "Something sad happened while Yahooing:",\
                                locals()
                            print e

    def record_complex(self, license_specifier, search_engine, count, 
        query, country = None, language = None, timestamp = None):
        if timestamp is None:
            timestamp = self.timestamp
        if not DRYRUN:
            self.db.complex.insert(
                license_specifier=license_specifier, 
                count = count, 
                query = query, 
                timestamp = timestamp, 
                search_engine=search_engine, 
                language=language,
                country = country)
            self.db.flush()
        debug("%s gave us %d hits via %s on %s with country %s, " \
              "language %s" %               \
              (license_specifier, count, search_engine, timestamp,     \
               country, language))
#        if DRYRUN:
#            debug("FYI, this is a dry run.") # needlessly verbose

class LcRunner(threading.Thread):
    def __init__(self, functions, kwargs):
        threading.Thread.__init__(self)
        self.lc = LinkCounter(**kwargs)
        print 'I made an lc to run', functions
        self.functions = functions

    def run(self):
        for function in self.functions:
            print 'going to try running function', function
            sys.stdout.flush()
            method = getattr(self.lc, function)
            method()

def main():
    import dbconfig
    lcargs = dict(dburl=dbconfig.dburl, xmlpath='old/api/licenses.xml')
    for functions in (
        ('count_google', 'specific_google_counter',),
        ('count_yahoo', 'specific_yahoo_counter',),
        ('count_msn',),
        ('count_alltheweb',)):
        working_set = LcRunner(functions, lcargs)
        working_set.start()

    # START GOOGLE TEST
    #functions = []
    #functions.append('count_google')
    #working_set = LcRunner(functions, lcargs)
    #working_set.start()
    # END GOOGLE TEST

if __name__ == '__main__':

    # set DEBUG from argv
    if 'debug' in sys.argv[1:]:
        DEBUG = 1
    else:
        DEBUG = 0

    # if log is set in argv, set stdout to a datelog
    if 'log' in sys.argv[1:]:
        todate = datetime.date.today().isoformat()
        sys.stdout = open('log.%s.%d' % (todate, os.getpid()), 'w')
        print 'Begun logging:', datetime.datetime.now().isoformat()
        sys.stdout.flush()

    # set DRYRUN from argv
    if 'dryrun' in sys.argv[1:]:
        DRYRUN = 1
    else:
        DRYRUN = 0

    # Get going!
    main()
