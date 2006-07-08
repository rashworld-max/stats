import BeautifulSoup
import re
import urllib2

## They have some SOAP thing that is only documented in an MSI.  What a freaking pain.
def msn_count(query):
    APP_ID='E389A2EC44FFB3F5748A9AEF7CCFED7AD82690DA'
    from SOAPpy import WSDL
    from SOAPpy import SOAPProxy
    
    source = {'Source':'Web', 'Offset':0, 'Count':10, 'ResultFields':'All'}
    sourceRequest = {'SourceRequest':source}
    params = {'AppID':APP_ID, 'Query':query, 'CultureInfo':'en-US', 'SafeSearch':'Off', 'Requests':sourceRequest, 'Flags':'None'}
    
    n = 'http://schemas.microsoft.com/MSNSearch/2005/09/fex/Search'
    wsdlFile = 'http://soap.search.msn.com/webservices.asmx?wsdl'
    
    server = WSDL.Proxy(wsdlFile)

    results = server.Search(Request=params)
    return results.Responses.SourceResponse.Total

def str2int(s):
    s = s.replace(',', '')
    return int(s)

def atw_count(query):
    PREFIX="http://www.alltheweb.com/search?cat=web&o=0&_sb_lang=any&q=link:"
    result = urllib2.urlopen(PREFIX + query).read()
    bs = BeautifulSoup.BeautifulSoup()
    bs.feed(result)
    for p in bs('p'):
        if ' '.join(p.renderContents().split()) == "No Web pages found that match your query.":
            return 0
        # I guess it's worth looking inside then
    count = re.search(r'<span class="ofSoMany">(.+?)</span>', result).group(1)
    return str2int(count)
