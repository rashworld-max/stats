from SOAPpy import WSDL

# you'll need to configure these two values;
# see http://www.google.com/apis/
WSDLFILE = '/home/paulproteus/stats/GoogleSearch.wsdl'
APIKEY = 'oaiAhUtQFHIBLkPQ25A5u+EOItzW0PaK'

_server = WSDL.Proxy(WSDLFILE)
def search(q, restrict=[], lr=''):
    """Search Google and return their object thing."""
    resluts = _server.doGoogleSearch(
        APIKEY, q, 0, 10, False, ".".join(restrict), False, lr, "utf-8", "utf-8")
    return resluts
