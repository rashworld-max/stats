import BeautifulSoup
import re
import urllib2
import time
import json

def msn_count(query):
    # This is CC's shiny, new Bing API 2.0 AppID
    APP_ID='7DCFCDFFF9BE925B6E553A7AD6E3F2606A774C5C'

    api_base_uri = 'http://api.search.live.net/json.aspx'
    query_params = '?appid=' + APP_ID + '&sources=web&web.count=1&query=' + query

    raw_result = urllib2.urlopen(api_base_uri + query_params).read()
    result = json.loads(raw_result)

    return result['SearchResponse']['Web']['Total']

def str2int(s):
    s = s.replace(',', '')
    return int(s)

def atw_count(query):
    PREFIX="http://www.alltheweb.com/search?cat=web&o=0&cs=utf-8&_sb_lang=any&q="
    result = unicode(urllib2.urlopen(PREFIX + query).read(), 'utf-8')
    bs = BeautifulSoup.BeautifulSoup()
    bs.feed(result)
    for p in bs('p'):
        if ' '.join(p.renderContents().split()) == "No Web pages found that match your query.":
            return 0
        # I guess it's worth looking inside then
    count = re.search(r'<span class="ofSoMany">(.+?)</span>', result).group(1)
    return str2int(count)

def try_thrice(fn, *arglist, **argdict):
    tries = 0
    while tries < 3:
        try:
            return fn(*arglist, **argdict)
        except Exception, e:
            if isinstance(e, KeyboardInterrupt):
               raise e
            print "Huh, while doing %s(%s, %s), %s happened." % (fn, arglist, argdict, e)
            tries += 1
            sleeptime = 2 ** tries * 10
            print 'trying again after sleeping for %d' % sleeptime
            time.sleep(sleeptime)
    raise e
