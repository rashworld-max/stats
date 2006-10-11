import simpleyahoo
import simplegoogle
import unittest
from snippets import *

sample_queries = 'license', '-license', 'watermelon', 'cantaloupe'
sample_links = 'http://www.cthuugle.com/'

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
            reslut = {'query': query, 'license': cc_spec,
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
    """ These experiments make the following lessons:
    * Google's CC searches break language or country subsearching if you use 'cc_attribution', but work fine for real values accepted by their restrict parameter (like cc_attribute)
    * Google's link: ignores language and country
    * TESTME: Google's -zomg queries are broken?
    * NOTEST (but true on Jul 11 2006): Google's SOAP Java junk blows up for count > 2^32 """
    # Here is where I document some facts of the Google API.
    # Trivia: Should these fail or succeed for the cases where Google is broken? ;-)

    def setUp(self):
        # FIXME: Does this run once per test?  If so, oops.
        # link:http://whatever ignores language and country
        self.link_searches = google_experiment('link:http://www.google.com/', countries=['United States', 'Poland'], languages=[None, 'English', 'French'])
        self.regular_search = google_experiment("Cthuugle", countries = [None, 'United States', 'Iceland'], languages = [None, 'Greek', 'Arabic'])
        self.work = google_experiment("work", cc_spec=["cc_attribute"], countries=[None], languages=[None])[0] # Work everywhere
        self.us_work = google_experiment("work", cc_spec=["cc_attribute"], countries=['United States'], languages=[None])[0] # in the US
        self.english_work = google_experiment("work", cc_spec=["cc_attribute"], countries=[None], languages=['English'])[0] # in English
        self.us_english_work = google_experiment("work", cc_spec=["cc_attribute"], countries=['United States'], languages=['English'])[0] # in English

        ## Test usefulness of not
        self.not_work = google_experiment("-work", cc_spec=["cc_attribute"], countries=[None], languages=[None])[0] # Work everywhere
        self.week = google_experiment("work", cc_spec=["cc_attribute"], countries=[None], languages=[None])[0] # Work everywhere
        self.week_not_work = google_experiment("week -work", cc_spec=["cc_attribute"], countries=[None], languages=[None])[0] # Work everywhere
        self.week_and_work = google_experiment("week work", cc_spec=["cc_attribute"], countries=[None], languages=[None])[0] # Work everywhere

    def test_link_search_is_broken(self):
        self.assertNotEqual(self.link_searches[0]['count'], 0) # Uninteresting if the first count is 0
        assert(allthesame([k['count'] for k in self.link_searches]))

    def test_regular_searches_vary_across_languages_and_countries(self):
        # Regular searches do vary across languages and countries
        self.assertNotEqual(self.regular_search[0], 0) # Uninteresting if the first count is 0
        assert(somedifferent([k['count'] for k in self.regular_search]))

    def test_broken_cc_searches_vary_across_countries(self):
        assert(self.work['count'] > self.us_work['count'])
    def test_broken_cc_searches_vary_across_languages(self):
        assert(self.work['count'] > self.english_work['count'])
    def test_broken_cc_language_and_country_smaller_than_language(self):
        assert(self.us_english_work['count'] < self.english_work['count'])
    def test_broken_cc_language_and_country_smaller_than_country(self):
        assert(self.us_english_work['count'] <  self.us_work['count'])

class YahooExperiments(unittest.TestCase):
    ''' These experiments make the following lessons:
    * Use InlinkData, not link:
    * For CC searches, Yahoo ignores language but respects country  '''
    def test_inlinkdata_is_bigger_than_link_colon(self):
        # First experiment: InlinkData vs. link: InlinkData gives more results
        colon = yahoo_experiment('link:http://www.google.com/', countries = [None], languages = [None])[0]
        inlink = yahoo_experiment('http://www.google.com/', apimethod = 'InlinkData', countries = [None], languages = [None])[0]
        assert(colon['count'] < inlink['count']) # /me rolls his eyes
        # Furthermore, the colon one is always is a multiple of 10 whereas the InlinkData isn't always (1/10 chance the inlinkdata assert will fail...)
        assert(colon['count'] % 10 == 0)
        assert(not(inlink['count'] % 10 == 0))

    def test_link_colon_language(self):
        all = yahoo_experiment('link:http://www.google.com/', countries = [None], languages = [None])[0]
        french = yahoo_experiment('link:http://www.google.com/', countries = [None], languages = ['French'])[0]
        assert(french['count'] != 0)
        assert(all['count'] > french['count'])
        
    def test_link_colon_country(self):
        all = yahoo_experiment('link:http://www.google.com/', countries = [None], languages = [None])[0]
        france = yahoo_experiment('link:http://www.google.com/', countries = ['France'], languages = [None])[0]
        assert(france['count'] != 0)
        assert(all['count'] > france['count'])

    def test_broken_inlinkdata_language(self):
        all = yahoo_experiment('http://www.google.com/', apimethod='InlinkData',
                               countries = [None], languages = [None])[0]
        self.assertRaises(simpleyahoo.ParameterError,  yahoo_experiment, 'http://www.google.com/', 'InlinkData', countries = [None], languages = ['French'])
        # Yeah, right. assert(french['count'] < all['count'])

    def test_broken_inlinkdata_country(self):
        all = yahoo_experiment('http://www.google.com/', apimethod='InlinkData',
                               countries = [None], languages = [None])[0]
        self.assertRaises(simpleyahoo.ParameterError, yahoo_experiment, 'http://www.google.com/', 'InlinkData', ['France'], [None])
        # I wish. assert(france['count'] < all['count'])

    def setUp(self):
        
        self.work = yahoo_experiment("+a", cc_spec=["cc_any"], countries=[None], languages=[None])[0] # Work everywhere
        self.fr_work = yahoo_experiment("+a", cc_spec=["cc_any"], countries=['France'], languages=[None])[0] # in France!
        self.english_work = yahoo_experiment("+a", cc_spec=["cc_any"], countries=[None], languages=['English'])[0] # in English
        self.fr_english_work = yahoo_experiment("+a", cc_spec=["cc_any"], countries=['France'], languages=['English'])[0] # in English
        assert(self.work['count'])
        assert(self.fr_work['count'])
        assert(self.english_work['count'])
        assert(self.fr_english_work['count'])
        
    def test_cc_searches_vary_across_countries(self):
        assert(self.work['count'] > self.fr_work['count'])
    def test_broken_cc_searches_vary_across_languages(self):
        # Should be <, but is ==
        self.assertEqual(self.work['count'], self.english_work['count'])
    def test_broken_cc_language_and_country_smaller_than_language(self):
        assert(self.fr_english_work['count'] < self.english_work['count'])
    def test_broken_cc_language_and_country_smaller_than_country(self):
        # should be <, but is ==
        self.assertEqual(self.fr_english_work['count'], self.fr_work['count'])

if __name__ == '__main__':
    unittest.main()
