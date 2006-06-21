#!/usr/bin/python

#With luck this script will never be needed again; it was created to update a now gone history.txt file into the history.xml we now use.

import lxml
import re
import string
from lxml import etree
from lxml.etree import Element
urroot=Element("Data")
tree=etree.ElementTree(element=urroot)
urroot.text='\n'
actdate=""
url="http://www.creativecommons.org"
acount=0
gcount=0
ycount=0

source=open('history.txt','r')

def initialize(date):
    root=etree.SubElement(urroot,"Dataset")
    root.set("Date",date)
    trawl=etree.SubElement(root,"Webtrawl")
    amain=etree.SubElement(trawl,"AllTheWeb")
    gmain=etree.SubElement(trawl,"Google")
    ymain=etree.SubElement(trawl,"Yahoo")
    run=root.getiterator()
    for r in run:
        r.text='\n'
        r.tail='\n'
    return (amain,gmain,ymain)

def getdata(string):
    y='!'
    date=re.search('^(.*) .*',string).group(1)
    a=re.search('(.*)\t(.*)\t(.*)\t(.*)',string).group(2)
    g=re.search('(.*)\t(.*)\t(.*)\t(.*)',string).group(3)
    if re.search('(.*)\t(.*)\t(.*)\t(.*)\t(.*)',string)!=None:
        y=re.search('(.*)\t(.*)\t(.*)\t(.*)\t(.*)',string).group(4)
    url=re.search('.*\t(.*)$',string).group(1)
    if g==')':
        g='!'
    if y==')':
        y='!'
    if a==')':
        a='!'
    return (date,a,g,y,url)

line="new"
line=source.readline()
while line!="":
    (date,acount,gcount,ycount,url)=getdata(line)
    if date!=actdate:
        actdate=date
        (amain,gmain,ymain)=initialize(actdate)
    if url!='SUM':
        if acount!='!':
            adata=etree.SubElement(amain,"Search")
            adata.set("URL",url)
            adata.set("Term","")
            adata.text=str(acount)
            adata.tail="\n"
        if gcount!='!':
            gdata=etree.SubElement(gmain,"Search")
            gdata.set("URL",url)
            gdata.set("Term","")
            gdata.text=str(gcount)
            gdata.tail="\n"
        if ycount!='!':
            ydata=etree.SubElement(ymain,"Search")
            ydata.set("URL",url)
            ydata.set("Term","")
            ydata.text=str(ycount)
            ydata.tail="\n"
    line=source.readline()

output=open('history.xml','w')
tree.write(output)
