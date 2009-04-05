#!/usr/bin/env python
import sys
import httplib
import itertools
import mwclient

import views
from utils import tries 

WIKI_HOST = 'monitor.creativecommons.org'
WIKI_PATH = '/'
BOT_NAME = 'CCStatsBot'
BOT_PASS = 'bhyccstatsbot'


class CCBot(object):
    def __init__(self):
        site = mwclient.Site(WIKI_HOST, WIKI_PATH)
        site.writeapi = False # XXX do this because api.php rewrite rule maybe problematic
        site.login(BOT_NAME, BOT_PASS)
        self.site = site
        return

    def upload(self, file_name, content, comment=''):
        if isinstance(content, unicode):
            content = content.encode('utf8')
        site = self.site
        try:
            site.upload(content, file_name, comment, ignore=True)
        except httplib.IncompleteRead:
            # The upload is success even we got an IncompleteRead
            pass
        #site.upload(content, file_name, comment, ignore=False)
        try:
            page = site.Pages['Sandbox']
        except:
            #XXX Strange... Seems this query will always be failed!
            # But we need to put it here so other queries will not failed.
            pass
        uploaded = site.Images[file_name]
        return uploaded

    def put_page(self, title, content):
        page = self.site.Pages[title]
        page.save(content)
        return page
    
    def get_page(self, title):
        page = self.site.Pages[title]
        return page

def run():
    bot = CCBot()
    view = views.View()
    filegen = view.all_files()
    for file in filegen:
        print "Uploading file: ", file.title, "...",
        sys.stdout.flush()
        uploaded = bot.upload(file.title, file.text)
        url = uploaded.imageinfo[u'url']
        print "Done. URL: ", url
        view.set_uploaded_url(file.title, url)

    pagegen = view.all_pages()
    for page in pagegen:
        print "Updating page: ", page.title, "...",
        sys.stdout.flush()
        bot.put_page(page.title, page.text)
        print "Done."
    return


def test():
    bot = CCBot()
    bot.put_page('Sandbox', 'HIHIHIHIHI')

    TEST_XML = """<?xml version="1.0" encoding="utf-8"?>
<test33>
</test33>"""
    uploaded = bot.upload('test5.xml', TEST_XML, 'testing upload.. again.')
    print "info of uploaded:", uploaded.imageinfo

    return

if __name__=='__main__':
    import sys
    if len(sys.argv)>1 and sys.argv[1].lower()=='test':
        test()
    else:
        run()

