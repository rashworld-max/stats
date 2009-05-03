"""
Grab related links for jurisdictions.
"""
import re
import json
import urllib2
import hashlib
import StringIO
from os import path
from xml.etree import ElementTree

import ccquery
import grab_flags
from utils import log

DB_FILE = 'ccdata.sqlite'
PAGE_GLOBALVOICE = 'http://globalvoicesonline.org/'
PAGE_OPENNET = 'http://map.opennet.net/filtering-pol.xml'

class FuzzyDict(dict):
    """
    Provides a dictionary that performs fuzzy lookup.
    Got from here with some modification:
    http://code.activestate.com/recipes/475148/
    """
    def __init__(self, items = None, cutoff = .6):
        """Construct a new FuzzyDict instance

        items is an dictionary to copy items from (optional)
        cutoff is the match ratio below which mathes should not be considered
        cutoff needs to be a float between 0 and 1 (where zero is no match
        and 1 is a perfect match)"""
        super(FuzzyDict, self).__init__()

        if items:
            self.update(items)
        self.cutoff =  cutoff

        # short wrapper around some super (dict) methods
        self._dict_contains = lambda x: dict.__contains__(self, x)
        self._dict_getitem = lambda x: dict.__getitem__(self, x)
        return

    def _match(self, u, v):
        """
        Caculate match radio for two given object.
        """
        u = u.lower()
        v = v.lower()
        spacechars = '(),-'
        for c in spacechars:
            u = u.replace(c, ' ')
            v = v.replace(c, ' ')
        
        u_words = set(u.split())
        v_words = set(v.split())
        null = set()

        if null.issuperset(u_words - v_words) or \
            null.issuperset(v_words - u_words):
                return 1.0

        diffsize = len(u_words.symmetric_difference(v_words))
        total = len(u_words) + len(v_words)
        radio = 1.0 - float(diffsize) / float(total)
        return radio

    def _search(self, lookfor, stop_on_first = False):
        """Returns the value whose key best matches lookfor

        if stop_on_first is True then the method returns as soon
        as it finds the first item
        """
        # if the item is in the dictionary then just return it
        if self._dict_contains(lookfor):
            return True, lookfor, self._dict_getitem(lookfor), 1

        # test each key in the dictionary
        best_ratio = 0
        best_match = None
        best_key = None
        for key in self:
            try:
            # calculate the match value
                ratio = self._match(key, lookfor)
            except TypeError:
                break

            # if this is the best ratio so far - save it and the value
            if ratio > best_ratio:
                best_ratio = ratio
                best_key = key
                best_match = self._dict_getitem(key)

            if stop_on_first and ratio >= self.cutoff:
                break

        return (
            best_ratio >= self.cutoff,
            best_key,
            best_match,
            best_ratio)

    def __contains__(self, item):
        "Overides Dictionary __contains__ to use fuzzy matching"
        if self._search(item, True)[0]:
            return True
        else:
            return False

    def __getitem__(self, lookfor):
        "Overides Dictionary __getitem__ to use fuzzy matching"
        matched, key, item, ratio = self._search(lookfor)

        if not matched:
            raise KeyError(
                "'%s'. closest match: '%s' with ratio %.3f"%
                    (str(lookfor), str(key), ratio))

        return item

def cached_urlread(url):
    """
    urlopen with local disk cache support, and retry 5 times if we get connection error.
    """
    log("Querying...")
    page = None
    cache_fn = path.join('/tmp/',  hashlib.md5(url).hexdigest())
    try:
        page = open(cache_fn).read()
        log("Got from cache.\n")
    except IOError:
        #no cache
        pass
    
    if page is None:
        page = urllib2.urlopen(url).read()

        open(cache_fn, 'w').write(page)
        log("OK.\n")
    return page

class LinksGrabber(object):
    def __init__(self):
        self.query = ccquery.CCQuery(DB_FILE)

        matching_dict = FuzzyDict()
        code_dict = {}

        for code, name in self.jurisiter():
            links = list()
            if code:
                code_dict[code] = links
            if name:
                matching_dict[name] = links
        # Some more alias
        matching_dict['usa'] = code_dict['US']

        self.matching_dict = matching_dict
        self.code_dict = code_dict

        return

    def jurisiter(self):
        q = self.query
        for code in q.all_juris(ported_only=False):
            name = q.juris_code2name(code)
            # convert from unicode to string
            code = str(code)
            name = str(name)
            yield (code, name)
        return

    def grab_globalvoices(self):
        print "Grabing Global Voices links..."
        page = cached_urlread(PAGE_GLOBALVOICE)
        # Match HTML tags like:
        #   <option value="/-/world/central-asia-caucasus/afghanistan/" >
        matches = re.finditer(r'<option value="/-/world/(.*)/(.*)/" >', page)
        for match in matches:
            region, country = match.group(1,2)
            url = "http://globalvoicesonline.org/-/world/%s/%s/"%(region, country)
            try:
                links = self.matching_dict[country]
                links.append(('Global Voices', url))
            except KeyError:
                print "No juris for:", url

        return

    def grab_opennet(self):
        print "Grabing OpenNet links..."
        page = cached_urlread(PAGE_OPENNET)
        t = ElementTree.parse(StringIO.StringIO(page))
        for state in t.findall('state'):
            urle = state.find('url')
            if urle is None:
                continue
            fips = state.get('id')
            url = urle.text
            
            code = self.query.juris_fips2code(fips)
            code = str(code)
            links = self.code_dict[code]
            links.append(('OpenNet Profile', url))
        return

    def grab_wikipedia(self):        
        # Just reuse the Wikipedia country page grabber in grab_flags.py
        print "Grabing Wikipedia links..."
        for code, page in grab_flags.country_pages():
            links = self.code_dict[code]
            page = page.replace(' ', '_')
            url = 'http://en.wikipedia.org/wiki/' + page
            links.append(('Wikipedia Article', url))
        return

    def gen_cci(self):
        " Generate urls like http://creativecommons.org/international/cn/"
        for code, links in self.code_dict.iteritems():
            url = 'http://creativecommons.org/international/%s/'%(code.lower())
            links.append(('CCI Page', url))
        return

    def gen_herdict(self):
        " Generate urls like http://www.herdict.org/web/explore/country/CN"
        for code, links in self.code_dict.iteritems():
            url = 'http://www.herdict.org/web/explore/country/%s'%(code)
            links.append(('Herdict Web', url))
        return

    def __call__(self):
        self.gen_cci()
        self.grab_wikipedia()
        self.grab_globalvoices()
        self.grab_opennet()
        self.gen_herdict()
        return

    def check(self):
        for code, links in self.code_dict.iteritems():
            sites = [l[0] for l in links]
            if len(set(sites)) < len(sites):
                print 'Please check:', code
        return

    def dump(self, filename):
        json.dump(self.code_dict, open(filename, 'w'), indent=4)
        return

def main():
    g = LinksGrabber()
    g()
    g.check()
    g.dump('related_links.txt')


if __name__=='__main__':
    main()


    
        



