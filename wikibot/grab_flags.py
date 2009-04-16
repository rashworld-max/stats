"""
Grab country flags from Wikipedia.
"""
import re
import urllib2
import mwclient
import time

SAVEDIR = 'flags/'
WIKI_HOST = 'en.wikipedia.org'
WIKI_PATH = '/w/'
ISOCDOE_PAGE = 'ISO_3166-1_alpha-2'

STRIP_PAGE_FROM = '===User-assigned code elements==='

wiki = mwclient.Site(WIKI_HOST, WIKI_PATH)

def country_pages():
    codepage = wiki.Pages[ISOCDOE_PAGE]
    text = codepage.edit()    
    text = text[:text.index(STRIP_PAGE_FROM)]

    # Find patterns like: 
    # | id="RO" | <tt>RO</tt> || [[Romania]] || 1974 ||
    rows = re.finditer(r'\| <tt>(\w*)</tt> \|\| \[\[(\w*)\]\] \|\|', text)
    for row in rows:
        code, page = row.groups()
        yield (code, page)
    yield ('UK', 'United Kingdom')
    yield ('SCOTLAND', 'Scotland')
    return

def fetch_img(url):
    r = urllib2.Request(url)
    r.add_header('User-Agent', 'CCMonitor/1.0')
    img = urllib2.urlopen(r).read()
    return img

def grab():
    pages = country_pages()
    for code, page in pages:
        wikipage = wiki.Pages[page]
        text = wikipage.edit()
        # Search for "image_flag = Flag of Yemen.svg"
        flagmatch = re.search(r'image_flag\s*=\s*(.*\.svg)', text)
        if flagmatch is None:
            print "No flag found for ", page
            continue
        flag = flagmatch.group(1)
        flagimg = wiki.Images[flag]
        url = flagimg.imageinfo[u'url']
        filename = SAVEDIR + 'Flag_%s.svg'%(code)
        img = fetch_img(url)
        open(filename, 'wb').write(img)
        print "Got flag for ", page
    return

if __name__=='__main__':
    grab()


