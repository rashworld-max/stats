import google
from lxml import etree
import urllib2
import urllib

def yahoo_count(query, cc_spec=''):
    url = 'http://search.yahoo.com/search?'
    args = {}
    if cc_spec:
        args['fr'] = 'sfp-cc'
        args['p'] = cc_spec
        args['y'] = 'Search CC'
    args['q'] = query
    url += urllib.urlencode(args)

    data = urllib2.urlopen(url).read()
    count = re.search(r'of about <.*?>(\S+?)<', data).group(1)
    return str2int(count)
    
def str2int(s):
    s = s.replace(',', '')
    return int(s)

## Q: Why do the *rest lists always include "" ?

## FIXME: Maybe I could loop over the URIs somewhere else so that I pass a URI
## in to the search-engine-specific things

## The count_* functions could totally be turned into a "templated" function

## FIXME: The bigger Yahoo and Google query stuff seems fairly separate from
## the count_* functions.  Maybe jam it into a different class?

class LinkCounter:
    dumb_queries = ['license', '-license', 'work', '-work', 'html', '-html']
    def __init__(self, dburl, xmlpath):
        self.db = dburl # open this with sqlsoup or something
        self.uris = self.parse(xmlpath)
        # We need to get a list of URIs to search for
        assert(self.uris) # These should not be empty.

    def parse(self, xmlpath):
        ret = []
        tree2=etree.parse(xmlpath)
        root2=tree2.getroot()
        for element in root2.getiterator('version'):
            ret.append(element.get('uri'))
        return ret # I'm not sorting.  So there.

    def record(self, cc_license_uri, search_engine, count):
        print "Recorded", count,"many hits for", cc_license_uri
        # FIXME: Obviously, do something with a DB.

    def count_google(self):
        ## Once from webtrawl
        google.setLicense('8cJjiPdQFHK2T3LGWq+Ro04dyJr0fyZs')
        total = 0
        for uri in self.uris:
            result = google.doGoogleSearch("link:%s" % uri)
            count = result.meta.estimatedTotalResultsCount

            # We record the specific url, count pair in the DB
            self.record(cc_license_uri=uri, search_engine='Google', count=count)

            # The old code would sum up for a count,
            # But we can do that with SQL later anyway.

    def count_alltheweb(self):
        PREFIX="http://www.alltheweb.com/search?cat=web&o=0&_sb_lang=any&q=link:"
        for uri in self.uris:
            result = urllib2.urlopen(PREFIX + url).read()
            count = re.search(r'<span class="ofSoMany">(\d+?)</span>', results).group(1)
            self.record(cc_license_uri=uri, search_engine="All The Web", count=str2int(count))
            # Not going to save the sum; we can do that with SQL.

    def count_yahoo(self):
        PREFIX = "http://search.yahoo.com/search?p=link:"
        for uri in self.uris:
            result = urllib2.uropen(PREFIX + url).read()
            count = re.search(r'of about (\S+)', result).group(1)
            self.record(cc_license_uri=uri, search_engine='Yahoo', count=str2int(count))

    def specific_google_counter(self):
        """ Now instead of searching for links to a license URI,
        we use Google's built-in CC search.

        Unfortunately, it doesn't let you do a raw count, so we hack around that by adding
        up queries like -license and +license. """
        
        ## The idea here is
        licenses = ["cc_publicdomain", "cc_attribute", "cc_sharealike", "cc_noncommercial", "cc_nonderived", "cc_publicdomain|cc_attribute|cc_sharealike|cc_noncommercial|cc_nonderived"]
        for license in licenses:
            for dumb_query in self.dumb_queries:
                result = google.doGoogleSearch(term, restrict=license)
                count = result.meta.estimatedTotalResultsCount
                self.record_complex(license_specifier=license,
                                    search_engine='Google',
                                    count=count,
                                    query=dumb_query)

    def specific_yahoo_counter(self):
        """ Similar deal here as for Google's specific_counter.
        FIXME: Abstract Yahoo queries. """
        licenses=["ccs=c","ccs=e","ccs=c&ccs=e"]
        for license in licenses:
            for dumb_query in self.dumb_queries:
                count = yahoo_count(query=dumb_query, cc_spec=license)
                self.record_complex(license_specifier=license,
                                    search_engine='Yahoo',
                                    count=count,
                                    query=dumb_query)

    def record_complex(self, license_specifier, search_engine, count, dumb_query):
        print 'huh, okay.'
        
        
                                    

        
            
        

def main():
    lc = link_counts.LinkCounter(dburl='', xmlpath='old/api/licenses.xml')
    return lc
    
