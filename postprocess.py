#!/usr/bin/python

import lxml
import string
from lxml import etree
from lxml.etree import Element
import SVGdraw
from SVGdraw import *
import math
import common

tree=etree.parse('/web/teamspace/www/stats/daily.xml')
root=tree.getroot()
tosslist=["http://creativecommons.org","http://www.creativecommons.org","http://creativecommons.org/licenses/publicdomain","http://creativecommons.org/licenses/publicdomain/1.0/","http://creativecommons.org/licenses/sampling/1.0/","http://creativecommons.org/licenses/sampling+/1.0/","http://creativecommons.org/licenses/GPL/2.0/","http://creativecommons.org/licenses/LGPL/2.1/","http://creativecommons.org/licenses/by-nd-nc/2.0/","http://creativecommons.org/licenses/devnations/2.0/","http://creativecommons.org/licenses/sampling/1.0/br/","http://creativecommons.org/licenses/sampling+/1.0/br/","http://creativecommons.org/licenses/nc-sampling+/1.0/"]

#Based on a formula I found online. Short form...given a percentage and a starting point, produce a slice of the circle of given radius.
def slicePie(percent,linex,liney,color,half,Ox,Oy,radius,s,name,n):
    if int(percent)==0:
        return linex,liney
    else:
        radians=(percent/100)*2*math.pi
        arcx=int(Ox-math.cos(radians)*radius)
        arcy=int(Oy-math.sin(radians)*radius)
        pd=pathdata()
        pd.move(Ox,Oy)
        pd.line(linex,liney)
        pd.ellarc(radius,radius,0,int(abs(math.ceil((half/100)-.5))),1,arcx,arcy)
        pathdata.closepath(pd)
        c=path(pd,fill=color,stroke='black')
        s.addElement(c)
        r=rect(width=10,height=10,x=2*Ox,y=(90+25*n),fill=color,stroke='black')
        s.addElement(r)
        t=text(2*Ox+20,25*(n+4),name)
        s.addElement(t)
        return arcx,arcy

#Standard URL parser--an earlier version than in sumgen.py.
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

#Creates a master list of all data from a given search engine, returns the list and the total number of results.
def getData(string):
    masterlist=[]
    total=0
    subroot=root.find('Webtrawl').find(string)
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
            masterlist.append((hits,t,v,j))
    return masterlist,total


def gatherStats(total,alist,mlist,index,cin,name,title):
    tlist=[]
    plist=[]
    colors=common.getColors()
    for a in alist:
        count=0
        for item in mlist:
            if cin==1 and a in item[index]:
                count+=item[0]
            elif cin==0 and item[index]==a:
                count+=item[0]
        print("%s\t%d\t%.1f"%(a,count,float(count)/total*100))
        tlist.append((a,count))
        plist.append((a,float(count)/total*100))
    if cin==0:
        Ox=300
        Oy=350
        radius=270
        d=drawing()
        s=svg(None,800,700)
        linex=Ox-radius
        liney=Oy
        rest=0.0
        n=0
        title=text(100,50,title,24)
        s.addElement(title)
        for (a,p) in plist:
            if p==100.0:
                c=circle(Ox,Oy,r=radius,fill=colors[0],stroke='black')
                s.addElement(c)
                r=rect(width=10,height=10,x=2*Ox,y=90,fill=colors[0],stroke='black')
                s.addElement(r)
                t=text(2*Ox+20,100,a+": 100%")
                s.addElement(t)
            elif p>0.01:
                strin="%s: %.2f%%"%(a,p)
                x,y=slicePie(p+rest,linex,liney,colors.pop(0),p,Ox,Oy,radius,s,strin,n)
                linex=x
                liney=y
                rest+=p
                n+=1                
        d.setSVG(s)
        d.toXml('/web/teamspace/www/stats/svgs/'+name+'.svg')
    else:
        d=drawing()
        s=svg(None,800,700)
        Ox=100
        Oy=600
        yroom=500
        xroom=600
        place=0
        yline=line(Ox,Oy,Ox,Oy-yroom,stroke='black')
        xline=line(Ox,Oy,Ox+xroom,Oy,stroke='black')
        s.addElement(xline)
        s.addElement(yline)
        for (a,p) in plist:
            r=rect(width=100, height=float(yroom*p/100), x=Ox+25+150*place,y=Oy-float(yroom*p/100),fill=colors[place])
            newa=a+": %.1f"%p+'%'
            t=text(x=Ox+25+150*place,y=Oy-float(yroom*p/100)-10,text=newa,font_size=24)
            place+=1
            s.addElement(r)
            s.addElement(t)
        titular=text(100,50,title,font_size=24)
        s.addElement(titular)
        d.setSVG(s)
        d.toXml('/web/teamspace/www/stats/svgs/'+name+'.svg')
    return tlist
#Removes the "deed-music" jurisdiction, folding it into 'us'.
def yankDeed(datalist):
    holder=None
    for item in datalist:
        if item[3]=='deed-music':
            holder=item
    for item in datalist:
        if item[3]=='generic' and item[2]==holder[2] and item[1]==holder[1]:
            datalist.remove(holder)
            datalist.remove(item)
            datalist.insert(0,(holder[0]+item[0],holder[1],holder[2],'generic'))

def processList(total,mlist,name):
    jlist=[]
    vlist=[]
    clist=[]
    proplist=['by','nc','nd','sa']
    yankDeed(mlist)
    for (number,ty,ve,ju) in mlist:
        if ju not in jlist:
            jlist.append(ju)
        if ve not in vlist:
            vlist.append(ve)
        if ty not in clist:
            clist.append(ty)
    jlist.sort()
    vlist.sort()
    clist.sort()
    proplist.sort()
    print "Jurisdictions\nName\tNumber\t%"
    nj=gatherStats(total,jlist,mlist,3,0,'jurisdictions_all_current_'+name,name+" Linkbacks, Jurisdiction Breakdown")
    print "Versions\nName\tNumber\t%"
    gatherStats(total,vlist,mlist,2,0,'versions_all_current_'+name,name+" Linkbacks, Version Breakdown")
    print "Codes\nName\tNumber\t%"
    gatherStats(total,clist,mlist,1,0,'codes_all_current_'+name,name+" Linkbacks, Code Breakdown")
    print "Properties\nName\tNumber\t%"
    gatherStats(total,proplist,mlist,1,1,'properties_all_current_'+name,name+' Linkbacks, Property Percentages')
    for (j,t) in nj:
        if t!=0:
            slist=[]
            for m in mlist:
                if m[3]==j:
                    slist.append(m)
            print "Per jurisdiction: "+j+": Version\nName\tNumber\t%"
            gatherStats(t,vlist,slist,2,0,'versions_'+j+'_current_'+name,name+" Linkbacks, "+j+" Jurisdiction, Version Breakdown")
            print "Per jurisdiction: "+j+": Code\nName\tNumber\t%"
            gatherStats(t,clist,slist,1,0,'codes_'+j+'_current_'+name,name+" Linkbacks, "+j+" Jurisdiction, Code Breakdown")
            print "Per jurisdiction: "+j+": Property\nName\tNumber\t%"
            gatherStats(t,proplist,slist,1,1,'properties_'+j+'_current_'+name,name+' Linkbacks, '+j+' Jurisdiction, Property Percentages')

#Given an engine, gathers data, writes output, creates graphs.
def activate(which):
    nlist,total=getData(which)
    print which+" Stats: "+str(total)+" Total"
    processList(total,nlist,which)

activate('Google')
activate('Yahoo')
activate('AllTheWeb')
