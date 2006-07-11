## What API parameters do the engines ignore?
import link_counts # This sets up the Google API for us
import simpleyahoo
import simplegoogle
from snippets import *

sample_queries = 'license', '-license', 'watermelon', 'cantaloupe'
sample_links = 'http://www.cthuugle.com/'

yahoo_results = [] # a list of dicts of {'query': query, 'language': ..., 'count': count}
google_reslut = [] # the kind of typo you don't fix

def yahoo_test():
    global yahoo_results
    yahoo_results = []
    for query in sample_queries:
        for license in [None] + simpleyahoo.licenses:
            for language in [None] + simpleyahoo.languages.keys():
                for country in [None] + simpleyahoo.countries.keys():
                    count = simpleyahoo.legitimate_yahoo_count(query=query, cc_spec=license, country=country, language=language)
                    result = {'query': query, 'license': license, 'language': language, 'country': country, 'count': count}
                    yahoo_results.append(result)
    return yahoo_results # In case you think I do functional programming.

def google_test():
    global google_reslut
    google_reslut = []
    licenses = ["cc_publicdomain", "cc_attribute", "cc_sharealike", "cc_noncommercial", "cc_nonderived", "cc_publicdomain|cc_attribute|cc_sharealike|cc_noncommercial|cc_nonderived"]
    for lang in [None] + simplegoogle.languages.keys():
        for country in [None] + simplegoogle.countries.keys():
            for license in [None] + licenses:
                pass # Should use google_experiment
    return google_reslut # In case you think...

def google_experiment(query, countries = 'all', languages = 'all', cc_license = []):
    ''' This runs some query on Google with various country and language values. '''
    # This is the wrong place for this function.  Perhaps
    # simplegoogle.py would be better.  I'm going to want to refactor
    # the license_stats.py code to use this excellent function.

    # FIXME: Some smart iteration across CC license specs?  I don't
    # understand them yet.

    # FIXME: I'd like to actually do this with results, not results counts.  Maybe another day.
    if countries == 'all':
        countries = [None] + simplegoogle.countries.keys()
    if languages == 'all':
        languages = [None] + simplegoogle.languages.keys()
    ret = []
    for country in countries:
        for language in languages:
            reslut = {'query': query, 'license': license,
                          'count': simplegoogle.count(query, cc_spec=license,
                                                      country=country, language=lang),
                          'country':country}
            ret.append(reslut)
    return ret

def google_experiments():
    # Here is where I document some facts of the Google API.
    
    # FIXME: I should do this with a unit testing framework so one
    # deadbeat assert doesn't break the whole thing.

    # link:http://whatever ignores language and country
    link_searches = google_experiment('link:http://www.google.com/')
    assert(link_searches[0] != 0) # Uninteresting if the first count is 0
    assert(allthesame(link_searches))

    # But regular searches do vary across languages and countries
    for args in ( ('United States', None), (None, 'Portuguese')):
        regular_search = google_experiment("Cthuugle", countries = 'United States')
        assert(regular_search[0] != 0) # Uninteresting if the first count is 0
        assert(somedifferent(regular_search))

def yahoo_experiments():
    pass
