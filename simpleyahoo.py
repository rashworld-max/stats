from yahoo.search.factory import create_search
from yahoo.search import SearchError, ParameterError

from BeautifulSoup import BeautifulSoup
import re
import urllib2

# Discussion of rate limits:
# http://developer.yahoo.com/search/siteexplorer/V1/inlinkData.html says we are limited to 5,000 queries per day.
# However, http://developer.yahoo.com/search/rate.html explains that it's not really 5,000 per day but one per 17.28 seconds
# Given that, we attempt to guarantee a sleep of 20s between queries to Yahoo.
QUERY_TIME_DELTA = 20
import time
import socks_monkey
last_query_time = 0

APPID = 'cc license search'

licenses = [['cc_any'],['cc_commercial'],['cc_modifiable'],['cc_commercial', 'cc_modifiable']]

languages = {'portuguese': 'pt', 'czech': 'cs', 'spanish': 'es', 'japanese': 'ja', 'persian': 'fa', 'slovak': 'sk', 'hebrew': 'he', 'polish': 'pl', 'swedish': 'sv', 'icelandic': 'is', 'estonian': 'et', 'turkish': 'tr', 'romanian': 'ro', 'serbian': 'sr', 'slovenian': 'sl', 'german': 'de', 'dutch': 'nl', 'korean': 'ko', 'danish': 'da', 'indonesian': 'id', 'hungarian': 'hu', 'lithuanian': 'lt', 'french': 'fr', 'norwegian': 'no', 'russian': 'ru', 'thai': 'th', 'finnish': 'fi', 'greek': 'el', 'latvian': 'lv', 'english': 'en', 'italian': 'it'} # Taken from http://developer.yahoo.com/search/languages.html on 2006-06-28

jurisdictions = {'Brazil': 'br', 'Canada': 'ca', 'Italy': 'it', 'France': 'fr', 'Argentina': 'ar', 'Norway': 'no', 'Australia': 'au', 'Czechoslovakia': 'cz', 'China': 'cn',  'Germany': 'de', 'Spain': 'es', 'Netherlands': 'nl', 'Denmark': 'dk', 'Poland': 'pl', 'Finland': 'fi', 'United States': 'us', 'Belgium': 'be', 'Sweden': 'se', 'Korea': 'kr', 'Switzerland': 'ch', 'United Kingdom': 'uk', 'Austria': 'at', 'Japan': 'jp', 'Taiwan': 'tw'}  # Taken from http://developer.yahoo.com/search/countries.html on 2006-06-28 ; removed Russia at the urging of pYsearch

def legitimate_yahoo_count(query, apimethod = 'Web', cc_spec=[], jurisdiction=None, language=None):
    ''' cc_spec is a list of things the Yahoo module knows about '''
    assert(apimethod in ['Web', 'InlinkData']) # known types here
    if cc_spec: # Enable Tor for cc_spec queries...
        socks_monkey.enable_tor() # In theory, creates a race for multithreaded use
    s = create_search(apimethod, APPID, query=query, results=0)
    if cc_spec:
        s.license = cc_spec
    if jurisdiction:
        if jurisdiction in jurisdictions:
            jurisdiction = jurisdictions[jurisdiction]
        s.country = jurisdiction
    if language:
        language = language.lower()
        if language in languages:
            language = languages[language]
        s.language = language
#    global last_query_time
#    now = time.time()
#    if (now - last_query_time < QUERY_TIME_DELTA):
#        # not safe to proceed
#        time.sleep(QUERY_TIME_DELTA - (now - last_query_time))
#        # now safe to proceed
    res = s.parse_results()
#    last_query_time = time.time()
    socks_monkey.disable_tor() # it's always safe to disable Tor
    return res.totalResultsAvailable

def scrape_siteexplorer_inlinks(license_uri):
    '''Scrape the Yahoo! SiteExplorer page for Inlinks count'''
    base_url = 'http://siteexplorer.search.yahoo.com/search?p='
    url = base_url + license_uri[7:-1]
    page = urllib2.urlopen(url).read()
    soup = BeautifulSoup(page)
    regex = re.compile('Inlinks \((.*)\)')
    inlink_part = soup.fetchText(regex).pop()
    inlink_count = regex.match(inlink_part).group(1)
    return inlink_count.replace(',','')
