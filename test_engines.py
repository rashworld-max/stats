## What API parameters do the engines ignore?
import link_counts # This sets up the Google API for us
import simpleyahoo

sample_queries = 'license', '-license', 'watermelon', 'cantaloupe'
sample_links = 'http://www.cthuugle.com/'

yahoo_results = [] # a list of dicts of {'query': query, 'language': ..., 'count': count}
google_reslut = [] # the kind of typo you don't fix

def yahoo_test():
    for query in sample_queries:
        for license in [None] + simpleyahoo.licenses:
            for language in [None] + simpleyahoo.languages.keys():
                for country in [None] + simpleyahoo.countries.keys():
                    count = simpleyahoo.legitimate_yahoo_count(query=query, cc_spec=license, country=country, language=language)
                    result = {'query': query, 'license': license, 'language': language, 'country': country, 'count': count}
                    yahoo_results.append(result)
    return yahoo_results # In case you think I do functional programming.

def google_test():
    licenses = ["cc_publicdomain", "cc_attribute", "cc_sharealike", "cc_noncommercial", "cc_nonderived", "cc_publicdomain|cc_attribute|cc_sharealike|cc_noncommercial|cc_nonderived"]
    for license in licenses:
        for query in sample_queries:
            google_reslut.append(
                {'license': license, 'query': query,
                 'count': link_counts.google.doGoogleSearch(query, restrict=license.meta.estimatedTotalResultsCount)})
    return google_reslut # In case you think...


