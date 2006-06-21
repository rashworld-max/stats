#!/usr/bin/python

#Simple enough to make. This script takes the daily.xml results and creates a tab-delimited output.
import lxml
import string
from lxml import etree
from lxml.etree import Element
tosslist=["http://creativecommons.org",
          "http://www.creativecommons.org",
          "http://creativecommons.org/licenses/publicdomain",
          "http://creativecommons.org/licenses/publicdomain/1.0/",
          "http://creativecommons.org/licenses/sampling/1.0/",
          "http://creativecommons.org/licenses/sampling+/1.0/",
          "http://creativecommons.org/licenses/GPL/2.0/",
          "http://creativecommons.org/licenses/LGPL/2.1/",
          "http://creativecommons.org/licenses/by-nd-nc/2.0/",
          "http://creativecommons.org/licenses/devnations/2.0/",
          "http://creativecommons.org/licenses/sampling/1.0/br/",
          "http://creativecommons.org/licenses/sampling+/1.0/br/",
          "http://creativecommons.org/licenses/nc-sampling+/1.0/"]

gurl=""
gnum=""
ynum=""
anum=""
gtotal=0
ytotal=0
atotal=0
tree=etree.parse('/web/teamspace/www/stats/daily.xml')
root=tree.getroot()
#Get date, create node pointers and iterators...
date=root.get('Date')
g=root.find('Webtrawl').find('Google')
y=root.find('Webtrawl').find('Yahoo')
a=root.find('Webtrawl').find('AllTheWeb')
giterate=g.getiterator('Search')
yiterate=y.getiterator('Search')
aiterate=a.getiterator('Search')

print date
print "Google\tYahoo\tAllTheWeb\tURI"
#For each URL in the Google list, find the matching URLs in the Yahoo and AllTheWeb lists; get the numbers, print the numbers along with the URL.
for git in giterate:
    gurl=git.get('URL')
    if gurl not in tosslist:
        gnum=git.text
        if gnum!='!':
            gtotal+=int(gnum)
        for yit in yiterate:
            ytemp=yit.get('URL')
            yterm=yit.get('Term')
            if ytemp==gurl and yterm=="":
                ynum=yit.text
                if ynum!='!':
                    ytotal+=int(ynum)
        for ait in aiterate:
            atemp=ait.get('URL')
            aterm=ait.get('Term')
            if atemp==gurl and aterm=="":
                anum=ait.text
                if anum!='!':
                    atotal+=int(anum)
        print gnum+"\t"+ynum+"\t"+anum+"\t\t"+gurl
print "SUM\n"+str(gtotal)+"\t"+str(ytotal)+"\t"+str(atotal)

#Now, do the printing for the GoogleCC search.
print "\nGoogle CC\n"
g=root.find('GoogleCC')
giterate=g.getiterator('Search')
print "Number\tTerm\tRestrictions"
for git in giterate:
    print git.text+"\t"+git.get('Term')+"\t"+git.get('Rest')

#Now the YahooCC search.
print "\nYahoo CC\n"
g=root.find('YahooCC')
giterate=g.getiterator('Search')
print "Number\tTerm\tRestrictions"
for git in giterate:
    print git.text+"\t"+git.get('Term')+"\t"+git.get('Rest')
