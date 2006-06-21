#!/usr/bin/python

# $Id: link-counts.py,v 1.26 2006/06/20 23:26:36 ml Exp $

import lxml
import google
import re
import string
import urllib
import commands
from lxml import etree
from lxml.etree import Element
from time import localtime, strftime

#These are the hardcoded values. I know, we shold move them (and we will, eventually, I imagine.)
urls=["http://creativecommons.org",
      "http://www.creativecommons.org",
      "http://creativecommons.org/licenses/publicdomain",
      "http://creativecommons.org/licenses/publicdomain/",
      "http://creativecommons.org/licenses/publicdomain/1.0/",
      "http://creativecommons.org/licenses/sampling/1.0/",
      "http://creativecommons.org/licenses/sampling+/1.0/",
      "http://creativecommons.org/licenses/GPL/2.0/",
      "http://creativecommons.org/licenses/LGPL/2.1/",
      "http://creativecommons.org/licenses/by-nc-nd/2.0/deed-music",
      "http://creativecommons.org/licenses/by-nd-nc/2.0/",
      "http://creativecommons.org/licenses/devnations/2.0/",
      "http://creativecommons.org/licenses/sampling/1.0/br/",
      "http://creativecommons.org/licenses/sampling+/1.0/br/",
      "http://creativecommons.org/licenses/nc-sampling+/1.0/"]
terms=["","license","-license","work","-work","html","-html"]
grest=["cc_publicdomain", "cc_attribute", "cc_sharealike", "cc_noncommercial", "cc_nonderived", "cc_publicdomain|cc_attribute|cc_sharealike|cc_noncommercial|cc_nonderived"]
grest.sort()
yrest=["","&ccs=c","&ccs=e","&ccs=c&ccs=e"]
google.LICENSE_KEY = '8cJjiPdQFHK2T3LGWq+Ro04dyJr0fyZs'

#Here I initialize the XML tree with the root and subroot nodes.

date=strftime("%Y-%m-%d",localtime())
root=Element("Dataset")
tree=etree.ElementTree(element=root)
root.set("Date",date)
trawl=etree.SubElement(root,"Webtrawl")
yahoocc=etree.SubElement(root,"YahooCC")
googlecc=etree.SubElement(root,"GoogleCC")
gmain=etree.SubElement(trawl,"Google")
amain=etree.SubElement(trawl,"AllTheWeb")
ymain=etree.SubElement(trawl,"Yahoo")
run=root.getiterator()
for r in run:
  r.text='\n'
  r.tail='\n'

#This is the original webtrawling app. It used to make up the whole of the application.
def webtrawl():
  alltheweb_prefix = "http://www.alltheweb.com/search?cat=web&o=0&_sb_lang=any&q=link:"
  yahoo_prefix = "http://search.yahoo.com/search?p=link:"
  start = strftime("%Y-%m-%d %H:%M:%S", localtime())
  
  alltheweb_total = 0
  yahoo_total = 0
  google_total = 0
  for url in urls:
    try:
      #You can't use any other search terms when you use "link:" in Google.
      google_results = google.doGoogleSearch("link:"+url)
      google_count = google_results.meta.estimatedTotalResultsCount
      google_total += int(google_count)
    except:
      google_count = '!'
      
    goog=etree.SubElement(gmain,"Search")
    goog.set("URL",url)
    goog.text=str(google_count)
    goog.tail="\n"

    for term in ['']:
      print term
      print url
      start_time = strftime("%Y-%m-%d %H:%M:%S", localtime())
      try:
        alltheweb_results = urllib.urlopen(alltheweb_prefix+url+"+"+term).read()
        alltheweb_count = re.search('<span class="ofSoMany">(.+?)</span>',alltheweb_results).group(1)
        alltheweb_count = string.replace(alltheweb_count,',','')
        alltheweb_total += int(alltheweb_count)
      except:
        alltheweb_count = '!'
      atw=etree.SubElement(amain,"Search")
      atw.set("URL",url)
      atw.set("Term",term)
      atw.text=alltheweb_count
      atw.tail="\n"

      try:
        yahoo_results = urllib.urlopen(yahoo_prefix+url+"+"+term).read()
        yahoo_count = re.search('of about (\S+)',yahoo_results).group(1)
        yahoo_count = string.replace(yahoo_count,',','')
        yahoo_total += int(yahoo_count)
      except:
        yahoo_count = '!'

      yah=etree.SubElement(ymain,"Search")
      yah.set("URL",url)
      yah.set("Term",term)
      yah.text=yahoo_count
      yah.tail="\n"
      
      print start_time+"\t"+url+"\n"+alltheweb_count+"\n"+`google_count`+"\n"+yahoo_count+"\n"

#Nice and simple parser.
def parse():
  tree2=etree.parse('api/licenses.xml')
  root2=tree2.getroot()
  for element in root2.getiterator('version'):
    urls.append(element.get('uri'))

#Google-cc searcher.
def google2():
  terms.remove("")
  for term in terms:
    for g in grest:
      start_time = strftime("%Y-%m-%d %H:%M:%S", localtime())
      try:
        results=google.doGoogleSearch(term, restrict=g)
        count=results.meta.estimatedTotalResultsCount
      except:
        count='!'
      print start_time+"\t"+term+"\t"+g+"\n"+`count`+"\n"
      goog=etree.SubElement(googlecc,"Search")
      goog.set("Term",term)
      goog.set("Rest",g)
      goog.text=str(count)
      goog.tail="\n"

  terms.append("")
  terms.sort()

#Yahoo-cc searcher.
def yahoo():
  terms.remove("")
  ypre1="http://search.yahoo.com/search?ei=UTF-8&fr=sfp-cc&p="
  ypre2="&y=Search+CC&cc=1"
  for term in terms:
    for y in yrest:
      count=0
      start_time = strftime("%Y-%m-%d %H:%M:%S", localtime())
      try:
        results = urllib.urlopen(ypre1+term+ypre2+y).read()
        count = re.search('of about <.*?>(\S+?)<',results).group(1)
        count = string.replace(count,',','')
      except:
        yahoo_count = '!'
      print start_time+"\t"+term+"\t"+y+"\n"+str(count)+"\n"
      yah=etree.SubElement(yahoocc,"Search")
      yah.set("Term",term)
      yah.set("Rest",y)
      yah.text=str(count)
      yah.tail="\n"

  terms.append("")
  terms.sort()

#Checkout, grabs the api from cvs. Nice one-liner--with a catch.
#I hope the anonymous setup for cvs is reliable...
def checkout():
    #commands.getoutput("cvs -z3 -d:pserver:anonymous@cvs.sourceforge.net:/cvsroot/cctools co -P api")
    commands.getoutput("svn co https://svn.sourceforge.net/svnroot/cctools/license_xsl/trunk api")

#And, finally, main.
checkout()
parse()
urls.sort()
webtrawl()
google2()
yahoo()

fileopen=open('/web/teamspace/www/stats/daily.xml','w')
tree.write(fileopen)
