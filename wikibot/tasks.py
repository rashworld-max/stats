#!/usr/bin/env python
import json
import sys

import config
import views
import ccbot
import ccquery

def change_flag_to_infobox(dry=True):
    query = ccquery.CCQuery(config.DB_FILE)
    view = views.View(query) 
    links_dict = json.load(open('related_links.txt'))

    bot = ccbot.WikiBot()

    for code in query.all_juris() + [u'GB']:
        if not code:
            continue
        name = query.juris_code2name(code)
        flag = 'Flag_%s.svg'%(code)
        links = links_dict[code]
        wikipage = bot.get_page(name)
        text = wikipage.edit()

        wikilinks = '\n\n'.join('[%s %s]'%(url, site) for site, url in links)

        infobox = """{{Infobox Jurisdiction
|flag = %s
|linkshead = %s
|links =
%s
<!-- You can put more additional resources related to this jurisdiction at here.-->
}}"""%(flag, name, wikilinks)
        
        oldtag = '{{Robot/%s/Flag}}'%(name)

        text = text.replace(oldtag, infobox)
        title = name

        if dry:
            print '== %s =='%title
            print text
            print
        else:
            print "Updating page: ", title, "...",
            sys.stdout.flush()
            wikipage.save(text)
            print "Done."
    return

def add_comment_on_robot_template(dry=True):
    query = ccquery.CCQuery(config.DB_FILE)
    view = views.View(query) 
    bot = ccbot.WikiBot()
    pages = view.all_userpages()

    for page in pages:
        title = page.title
        wikipage = bot.get_page(title)
        text = wikipage.edit()
        text = text.replace('{{Robot/', """{{<!-- NOTE: This is used to embed automatically generated content, please do not change or remove! -->
Robot/""")
        
        if dry:
            print '== %s =='%title
            print text
            print
        else:
            print "Updating page: ", title, "...",
            sys.stdout.flush()
            wikipage.save(text)
            print "Done."
    return

if __name__=='__main__':
    #change_flag_to_infobox(dry=False)
    add_comment_on_robot_template(dry=False)
