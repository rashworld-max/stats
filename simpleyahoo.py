from yahoo.search.factory import create_search
from yahoo.search import SearchError

APPID = 'cc license search'

licenses = [['cc_any'],['cc_commercial'],['cc_modifiable'],['cc_commercial', 'cc_modifiable']]

languages = {'portuguese': 'pt', 'czech': 'cs', 'spanish': 'es', 'japanese': 'ja', 'persian': 'fa', 'slovak': 'sk', 'hebrew': 'he', 'polish': 'pl', 'swedish': 'sv', 'icelandic': 'is', 'estonian': 'et', 'turkish': 'tr', 'romanian': 'ro', 'serbian': 'sr', 'slovenian': 'sl', 'german': 'de', 'dutch': 'nl', 'korean': 'ko', 'danish': 'da', 'indonesian': 'id', 'hungarian': 'hu', 'lithuanian': 'lt', 'french': 'fr', 'norwegian': 'no', 'russian': 'ru', 'thai': 'th', 'finnish': 'fi', 'greek': 'el', 'latvian': 'lv', 'english': 'en', 'italian': 'it'} # Taken from http://developer.yahoo.com/search/languages.html on 2006-06-28

countries = {'Brazil': 'br', 'Canada': 'ca', 'Italy': 'it', 'France': 'fr', 'Argentina': 'ar', 'Norway': 'no', 'Australia': 'au', 'Czechoslovakia': 'cz', 'China': 'cn',  'Germany': 'de', 'Spain': 'es', 'Netherlands': 'nl', 'Denmark': 'dk', 'Poland': 'pl', 'Finland': 'fi', 'United States': 'us', 'Belgium': 'be', 'Sweden': 'se', 'Korea': 'kr', 'Switzerland': 'ch', 'United Kingdom': 'uk', 'Austria': 'at', 'Japan': 'jp', 'Taiwan': 'tw'}  # Taken from http://developer.yahoo.com/search/countries.html on 2006-06-28 ; removed Russia at the urging of pYsearch

## FIXME! rename "type" to "apimethod"
def legitimate_yahoo_count(query, type = 'Web', cc_spec=[], country=None, language=None):
    ''' cc_spec is a list of things the Yahoo module knows about '''
    assert(type in ['Web', 'InlinkData']) # known types here
    s = create_search(type, APPID, query=query, results=0)
    if cc_spec:
        s.license = cc_spec
    if country:
        if country in countries:
            country = countries[country]
        s.country = country
    if language:
        if language in languages:
            language = languages[language]
        s.language = language
    res = s.parse_results()
    return res.totalResultsAvailable
