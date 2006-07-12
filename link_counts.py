from lxml import etree
import time
import datetime

DEBUG = 1
def debug(s):
    if DEBUG:
        print s

import simpleyahoo
import simplegoogle
import lc_util

from sqlalchemy.ext.sqlsoup import SqlSoup

## THINKME: Google and Yahoo both have different ways to encode CC license types.  Later on, it's probably worth standardizing this somehow, or else their trash gets shoved into our DB.

## FIXME: Maybe I could loop over the URIs somewhere else so that I pass a URI
## in to the search-engine-specific things

class LinkCounter:
    dumb_queries = ['license', '-license', 'work', '-work', 'html', '-html']
    ## TRYME: ccTLDs?
    def __init__(self, dburl, xmlpath):
        self.timestamp = datetime.datetime.now()
        self.db = SqlSoup(dburl) # open this with sqlsoup or something
        self.uris = self.parse(xmlpath)
        # We need to get a list of URIs to search for
        assert(self.uris) # These should not be empty.
        self.uris.extend(['http://creativecommons.org','http://www.creativecommons.org',
                          'http://creativecommons.org/licenses/publicdomain',
                          'http://creativecommons.org/licenses/publicdomain/1.0/',
                          'http://creativecommons.org/licenses/by-nc-nd/2.0/deed-music',
                          'http://creativecommons.org/licenses/by-nd-nc/2.0/']) # These were in old but not in the XML

    def parse(self, xmlpath):
        ret = []
        tree2=etree.parse(xmlpath)
        root2=tree2.getroot()
        for element in root2.getiterator('version'):
            ret.append(element.get('uri'))
        return ret # I'm not sorting.  So there.

    def record(self, cc_license_uri, search_engine, count, country = None, language = None):
        self.db.simple.insert(license_uri=cc_license_uri, search_engine=search_engine,count=count,timestamp = self.timestamp, country = country, language = language)
        self.db.flush()
        debug("%s gave us %d hits via %s" % (cc_license_uri, count, search_engine))

    def count_google(self):
        ## Once from webtrawl
        for uri in self.uris:
            try:
                count = simplegoogle.count('link:%s' % uri)
                # We record the specific uri, count pair in the DB
                self.record(cc_license_uri=uri, search_engine='Google', count=count)
            except Exception, e:
                print "Something sad happened while Googling", uri
                print e

    def count_msn(self):        
        ## Once from webtrawl
        for uri in self.uris:
            try:
                count = lc_util.msn_count("link:%s" % uri)
                # We record the specific uri, count pair in the DB
                self.record(cc_license_uri=uri, search_engine='MSN', count=count)
            except Exception, e:
                print "Something sad happened while MSNing", uri
                print e

    def count_alltheweb(self):
        # These guys seem to get mad at us if we query them too fast.
        # To avoid "HTTP Error 999" (!), let's sleep(0.1) between
        # queries.  They seem to block the IP, not just the
        # user-agent.  Oops.
        for uri in self.uris:
            try:
                self.record(cc_license_uri=uri, search_engine="All The Web", count=lc_util.atw_count("link:%s" % uri))
            except Exception, e:
                print "Something sad happened while ATWing", uri
                print e
            time.sleep(1) # "And, breathe."
                

    def count_yahoo(self):
        # No sleep here because we're APIing it up.
        for uri in self.uris:
            try:
                count = simpleyahoo.legitimate_yahoo_count(uri, 'InlinkData')
                # Country is not a valid parameter for inlinkdata :-(
		# And languages get ignored! :-(
                self.record(cc_license_uri=uri,
                            search_engine='Yahoo',
                            count = count)
            except Exception, e:
                print "Something sad happened while Yahooing", uri
                print e

    def specific_google_counter(self):
        """ Now instead of searching for links to a license URI,
        we use Google's built-in CC search.

        Unfortunately, it doesn't let you do a raw count, so we hack
        around that by adding up queries like -license and +license."""
        
        ## The is Google's idea of how to encode CC stuff.
        licenses = [["cc_publicdomain"], ["cc_attribute"], ["cc_sharealike"], ["cc_noncommercial"], ["cc_nonderived"], ["cc_publicdomain","cc_attribute","cc_sharealike","cc_noncommercial","cc_nonderived"]]
        for license in licenses:
            for dumb_query in self.dumb_queries:
                try:
                    count = simplegoogle.count(dumb_query, cc_spec=[license])
                    self.record_complex(license_specifier=license,
                                        search_engine='Google',
                                        count=count,
                                        query=dumb_query)
                except Exception, e:
                    print "Something sad happened while Googling", license, "with query", dumb_query
                    print e
    
    def specific_yahoo_counter(self):
        """ Similar deal here as for Google's specific_counter."""
        for license in simpleyahoo.licenses:
            for dumb_query in self.dumb_queries:
                # Now, let's add languages
                # FIXME: Use simpleyahoo experiment function
                # CONSIDERME: Use yield and iterators for experiment function
                for language in [None] + simpleyahoo.languages.keys():
                    for country in [None] + simpleyahoo.countries.keys():
                        try:
                            count = simpleyahoo.legitimate_yahoo_count(query=dumb_query, cc_spec=license, country=country, language=language) # Query with the terse form
                            self.record_complex(license_specifier='&'.join(license),
                                                search_engine='Yahoo',
                                                count=count,
                                                query=dumb_query,
                                                language=language,
                                                country=country) # but store the human forms
                        except Exception, e:
                            print "Something sad happened while Yahooing:", locals()
                            print e
                        

    def record_complex(self, license_specifier, search_engine, count, query, country = None, language = None):
        self.db.complex.insert(license_specifier=license_specifier, count = count, query = query, timestamp = self.timestamp, search_engine=search_engine, country=country, language=language)
        self.db.flush()
        debug("%s gave us %d hits via %s" % (license_specifier, count, search_engine))
        
def main():
    lc = LinkCounter(dburl='mysql://root:@localhost/cc', xmlpath='old/api/licenses.xml')
    lc.count_google()
    lc.count_yahoo()
    lc.count_msn()
    lc.specific_google_counter()
    lc.specific_yahoo_counter() # This makes too many queries?
    lc.count_alltheweb() # Done last because of long sleep times

if __name__ == '__main__':
    main()
