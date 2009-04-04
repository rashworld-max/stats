#!/usr/bin/env python
import itertools
import mwclient 

import views

WIKI_HOST = 'monitor.creativecommons.org'
WIKI_PATH = '/'
BOT_NAME = 'CCStatsBot'
BOT_PASS = 'bhyccstatsbot'

def run():
    site = wikipedia.getSite()
    view = views.View()
    pagegen = view.all_pages()
    for page in pagegen:
        print "Updating page: ", page.title, "...",
        sys.stdout.flush()
        wikipage = wikipedia.Page(site, page.title)
        oldpage = wikipage.get()
        if page.text <> oldpage:
            wikipage.put(page.text, "Updated by ccbot.py - testing.")
            print "Done."
        else:
            print "Same as old page, skipped."
    return

class CCBot(object):
    def __init__(self):
        site = mwclient.Site(WIKI_HOST, WIKI_PATH)
        #site.writeapi = False # XXX do this because api.php rewrite rule maybe problematic
        site.login(BOT_NAME, BOT_PASS)
        self.site = site
        return

    def upload(self, file_name, content, comment=''):
        site = self.site
        site.upload(content, file_name, comment, ignore=True)
        #site.upload(content, file_name, comment, ignore=False)
        try:
            page = site.Pages['Sandbox']
        except:
            #XXX Strange... Seems this query will always be failed!
            # But we need to put it here so other queries will not failed.
            pass
        uploaded = site.Pages['File:'+file_name]
        return uploaded

    def put_page(self, title, content):
        page = self.site.Pages[title]
        page.save(content)
        return page
    
    def get_page(self, title):
        page = self.site.Pages[title]
        return page

def test():
    bot = CCBot()
    #bot.put_page('Sandbox', 'HIHIHI')

    TEST_XML = """<?xml version="1.0" encoding="utf-8"?>
<test33>
</test33>"""
    uploaded = bot.upload('Test44.xml', TEST_XML, 'testing upload.. again.')
    print "info of uploaded:", uploaded.imageinfo

    return

if __name__=='__main__':
    test()
    #run()

