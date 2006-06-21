#!/usr/bin/python

import lxml
import string
from lxml import etree
from lxml.etree import Element
import sys

tree=etree.parse('/web/teamspace/www/stats/daily.xml')
root=tree.getroot()
tosslist=["http://creativecommons.org","http://www.creativecommons.org","http://creativecommons.org/licenses/publicdomain","http://creativecommons.org/licenses/publicdomain/1.0/","http://creativecommons.org/licenses/sampling/1.0/","http://creativecommons.org/licenses/sampling+/1.0/","http://creativecommons.org/licenses/GPL/2.0/","http://creativecommons.org/licenses/LGPL/2.1/","http://creativecommons.org/licenses/by-nd-nc/2.0/","http://creativecommons.org/licenses/devnations/2.0/","http://creativecommons.org/licenses/sampling/1.0/br/","http://creativecommons.org/licenses/sampling+/1.0/br/","http://creativecommons.org/licenses/nc-sampling+/1.0/"]
active=['by','by-nc-nd','by-nc','by-nd','by-nc-sa','by-sa']
jlist=[]

#My universal URL parser.
def urlParse(url):
    jurisdiction=''
    elements=url.split('/')
    which=elements[4]
    if which=='publicdomain':
        which='pd'
    version=elements[5]
    if version=='':
        version='1.0'
    if len(elements)>6:
        jurisdiction=elements[6]
    if jurisdiction=='' or jurisdiction=='us':
        jurisdiction='generic'
    return (which, version, jurisdiction)

#This iterates over the entire list and connects a number to each jurisdiction/license code pair.
def getData():
    masterlist=[]
    total=0
    subroot=root.find('Webtrawl').find('Yahoo')
    iterate=subroot.getiterator('Search')
    for elm in iterate:
        url=elm.get('URL')
        if url not in tosslist and (elm.get('Term')=='' or elm.get('Term')==None):
            (t,v,j)=urlParse(url)
            if elm.text=='!':
                hits=0
            else:
                hits=int(elm.text)
                total+=hits
            set=0
            for m in masterlist:
                if (m[1]==t or (t=='by-nd-nc' and m[1]=='by-nc-nd')) and (m[2]==j or (j=='deed-music' and m[2]=='generic')):
                    masterlist.remove(m)
                    masterlist.append((hits+m[0],m[1],m[2]))
                    set=1
            if set==0:
                if t=='by-nd-nc':
                    t='by-nc-nd'
                if j=='deed-music':
                    j='generic'
                masterlist.append((hits,t,j))
    return masterlist,total

#Returns the total counted for any individual license.
def getJTot(juris,mlist):
    total=0
    for (number,ty,ju) in mlist:
        if ju==juris:
            total+=number
    return total

def createPage(total,mlist,j):
#Simple little function. Given a jurisdiction create the execsum.htm...put in the necessary images, write the tables.
    handle=file('/web/teamspace/www/stats/execsum_'+j+'.htm','w')
    handle.write('<HTML><HEAD><TITLE>Executive Summary: Jurisdiction '+j+'</TITLE></HEAD><BODY>\n<IMG SRC=\"svgs/total_'+j+'_history_Numerical_Yahoo.png\"><BR>\n<IMG SRC=\"svgs/codes_'+j+'_current_Yahoo.png\"><BR>\n<IMG SRC=\"svgs/properties_'+j+'_current_Yahoo.png\"><BR>')
    if j=='all':
        handle.write('<IMG SRC=\"svgs/jurisdictions_'+j+'_current_Yahoo.png\"><BR>')
    handle.write('<IMG SRC=\"svgs/codes_'+j+'_history_Numerical_Yahoo.png\"><BR>')
    if j=='all':
        handle.write('<IMG SRC=\"svgs/jurisdictions_'+j+'_history_Logarithmic_Yahoo.png\">')
    handle.write('<TABLE><TR><TD>')
    test=0
    for code in active:
        handle.write('<TABLE BORDER=1>')
        if code=='by':
            name='Attribution'
        elif code=='by-nc':
            name='Attribution-NonCommercial'
        elif code=='by-nc-nd':
            name='Attribution-NonCommercial-NoDerivs'
        elif code=='by-nc-sa':
            name='Attribution-NonCommercial-ShareAlike'
        elif code=='by-nd':
            name='Attribution-NoDerivs'
        else:
            name='Attribution-ShareAlike'
        templist=[]
        handle.write('<TR><TH COLSPAN=2><B><CENTER>'+name+'</CENTER></B></TH></TR>')
        if j=='all':
            ljlist=jlist
        else:
            ljlist=[j]
        for jr in ljlist:
            total=getJTot(jr,mlist)
            for (number,ty,ju) in mlist:
                if ju==jr and ty==code and total!=0:
                    templist.append((float(number)/total*100,ju))
        templist.sort()
        templist.reverse()
        for n,jur in templist:
            if j=='all':
                handle.write('<TR><TD WIDTH=150>%s</TD><TD WIDTH=150>%.2f%%</TD></TR>' % (jur,n))
            else:
                handle.write('<TR><TD WIDTH=300>%.2f%%</TD></TR>' % n)
        handle.write('</TABLE></TD>')
        test+=1
        if test==3:
            handle.write('</TR><TR>')
        if test<6:
            handle.write('<TD WIDTH=300>')
    handle.write('</TABLE></BODY></HTML>')

#Gather data, sort it, organize it, make tables.
active.sort()
dlist,tot=getData()
for (number,ty,ju) in dlist:
    if ju not in jlist:
        jlist.append(ju)
jlist.sort()
jlist.insert(0,'all')
for j in jlist:
    createPage(tot,dlist,j)
