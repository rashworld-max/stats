## What API parameters do the engines ignore?
import simpleyahoo
import simplegoogle
import unittest
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
                pass #Should use google_experiment
    return google_reslut # In case you think...

def google_experiment(query, countries = 'all', languages = 'all', cc_spec = []):
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
                          'count': simplegoogle.count(query, cc_spec=cc_spec,
                                                      country=country, language=language),
                          'country':country}
            ret.append(reslut)
    return ret

def yahoo_experiment(query, apimethod = 'Web', countries = 'all', languages = 'all', cc_spec = []):
    ''' This runs some query on the Yahoo API. '''
    if countries == 'all':
        countries = [None] + simpleyahoo.countries.keys()
    if languages == 'all':
        languages = [None] + simpleyahoo.languages.keys()
    ret = []
    for country in countries:
        for language in languages:
            reslut = {'query': query, 'apimethod': apimethod, 'cc_spec': cc_spec,
                      'country': country, 'language': language,
                      'count': simpleyahoo.legitimate_yahoo_count(query, apimethod, cc_spec, country, language)}
            ret.append(reslut)
    return ret

class GoogleExperiments(unittest.TestCase):
    # Here is where I document some facts of the Google API.
    # Trivia: Should these fail or succeed for the cases where Google is broken? ;-)

    def setUp(self):
        # link:http://whatever ignores language and country
        self.link_searches = google_experiment('link:http://www.google.com/', countries=['United States', 'Poland'], languages=[None, 'English', 'French'])
        self.regular_search = google_experiment("Cthuugle", countries = [None, 'United States', 'Iceland'], languages = [None, 'Greek', 'Arabic'])
        self.work = google_experiment("work", cc_spec=["cc_attribution"], countries=[None], languages=[None])[0] # Work everywhere
        self.us_work = google_experiment("work", cc_spec=["cc_attribution"], countries=['United States'], languages=[None])[0] # in the US
        self.english_work = google_experiment("work", cc_spec=["cc_attribution"], countries=[None], languages=['English'])[0] # in English
        self.us_english_work = google_experiment("work", cc_spec=["cc_attribution"], countries=['United States'], languages=['English'])[0] # in English
    
    def test_link_search_is_broken(self):
        self.assertNotEqual(self.link_searches[0]['count'], 0) # Uninteresting if the first count is 0
        assert(allthesame([k['count'] for k in self.link_searches]))

    def test_regular_searches_vary_across_languages_and_countries(self):
        # But regular searches do vary across languages and countries
        self.assertNotEqual(self.regular_search[0], 0) # Uninteresting if the first count is 0
        assert(somedifferent([k['count'] for k in self.regular_search]))

    def test_broken_cc_searches_vary_across_countries(self):
        # should be >, but is ==
        self.assertEqual(self.work['count'], self.us_work['count'])
    def test_broken_cc_searches_vary_across_languages(self):
        # should be <, but is ==
        self.assertEqual(self.work['count'], self.english_work['count'])
    def test_broken_cc_language_and_country_smaller_than_language(self):
        # should be <, but is ==
        self.assertEqual(self.us_english_work['count'], self.english_work['count'])
    def test_broken_cc_language_and_country_smaller_than_country(self):
        # should be <, but is ==
        self.assertEqual(self.us_english_work['count'], self.us_work['count'])

class YahooExperiments(unittest.TestCase):
    def test_inlinkdata_is_bigger_than_link_colon(self):
        pass

    # First experiment: InlinkData vs. link: InlinkData gives more results
    colon = yahoo_experiment('link:http://www.google.com/', countries = [None], languages = [None])[0]
    inlink = yahoo_experiment('http://www.google.com/', apimethod = 'InlinkData', countries = [None], languages = [None])[0]
    assert(colon['count'] < inlink['count']) # /me rolls his eyes
    # Furthermore, the colon one is always is a multiple of 10 whereas the InlinkData isn't always (1/10 chance the inlinkdata assert will fail...)
    assert(colon['count'] % 10 == 0)
    assert(not(inlink['count'] % 10 == 0))

def yahoo_experiments():
    pass

if __name__ == '__main__':
    unittest.main()
