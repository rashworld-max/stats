#!/usr/bin/python

import lxml
import string
from lxml import etree
from lxml.etree import Element
import SVGdraw
from SVGdraw import *
import math
import common

#Root components. Gets the history tree, finds the root. Tosslist urls are
#urls we search but don't want to gather history graph data on--like the
#home page, the GPL, etc.

tree=etree.parse('/web/teamspace/www/stats/history.xml')
print tree
root=tree.getroot()
print root
tosslist=["http://creativecommons.org","http://www.creativecommons.org","http://creativecommons.org/licenses/publicdomain","http://creativecommons.org/licenses/publicdomain/1.0/","http://creativecommons.org/licenses/sampling/1.0/","http://creativecommons.org/licenses/sampling+/1.0/","http://creativecommons.org/licenses/GPL/2.0/","http://creativecommons.org/licenses/LGPL/2.1/","http://creativecommons.org/licenses/by-nd-nc/2.0/","http://creativecommons.org/licenses/devnations/2.0/","http://creativecommons.org/licenses/sampling/1.0/br/","http://creativecommons.org/licenses/sampling+/1.0/br/","http://creativecommons.org/licenses/nc-sampling+/1.0/"]

#The totals dictionary contains the total number of hits for any date, per
#engine and per juirisdiction. The jlist is simply a list of jurisdictions.
totals={}
jlist=[]

#Removes any data sets with bad dat--defined as incomplete searches or searches
#that have zeros. This helps get rid of the odd spiking.
def excise():
    print 'in excise()'
    active=root.getiterator('Dataset')
    for day in active:
        subact=day.find('Webtrawl').find('Yahoo')
        l=subact.__len__()
        if l<30:
            root.remove(day)
        else:
            subit=subact.getiterator('Search')
            daytot=0
            for s in subit:
                if s.text!='!':
                    daytot+=int(s.text)
            if daytot==0:
                root.remove(day)
    print 'out excise()'

#Extracts a list of jurisdictions from the data, using the most recent dataset
#for a source.
def getJuris():
    print 'in getJuris()'
    active=root.getiterator('Dataset')
    root2=active[len(active)-1]
    iterate=root2.getiterator('Search')
    for leaf in iterate:
        url=leaf.get('URL')
        if url not in tosslist and url!=None:
            w,v,j=urlParse(url)
            if j not in jlist and j!='deed-music':
                jlist.append(j)
    print 'out getJuris()'

#Given a node, assumed to be a search engine's node for a certain day, return
#the total number of hits within that node.
def getTotal(cereal):
    #print 'in getTotal()'
    spoon=0
    bowl=cereal.getiterator('Search')
    for flake in bowl:
        words=flake.get('URL')
        term=flake.get('Term')
        if words not in tosslist:
            if flake.text!='!' and (term=='' or term==None):
                spoon+=int(flake.text)
    #print 'out getTotal()'
    return spoon

#Same as above, but only count those whose jurisdiction matches what we're
#searching on.
def getJTotal(cereal,j):
    #print 'in getJTotal()'
    spoon=0
    bowl=cereal.getiterator('Search')
    for flake in bowl:
        words=flake.get('URL')
        term=flake.get('Term')
        if words not in tosslist and words !=None:
            w,v,uj=urlParse(words)
            if flake.text!='!' and uj==j and (term=='' or term==None):
                spoon+=int(flake.text)
    #print 'out getJTotal()'
    return spoon

#For every possibly date, every engine, every jurisdiction: get totals, insert
#into dictionary.
def gatherTotals():
    print 'in gatherTotals()'
    history=root.getiterator('Dataset')
    for day in history:
        date=day.get('Date')
        trawl=day.find('Webtrawl')
        for string in common.getEngines():
            index=trawl.find(string)
            tot=getTotal(index)
            totals[(date,string)]=tot
            for j in jlist:
                jtot=getJTotal(index,j)
                totals[(date,string,j)]=jtot
    print 'out gatherTotals()'

#Ah, this one is fun. Given a URL, extract from it the elements that we need:
#Which type of license, which version, and which jurisdiction (with a special
#condition that US, deed-music, and no jurisdiction are 'generic').
def urlParse(url):
    #print 'in urlParse()'
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
    if jurisdiction=='' or jurisdiction=='us' or jurisdiction=='deed-music':
        jurisdiction='generic'
    #print 'out urlParse()'
    return (which, version, jurisdiction)

#Given a node, a jurisdiction, a total number of links from the totals
#dictionary, and a criterion--which is either '' or a specific jurisdiction--
#return a list of pure numbers, one of percentages, and one of the different
#data--that is, the list of different labels (different versions, or codes,
#etc.).
def gatherAmount(node,crit,total,juris):
    #print 'in gatherAmount()'
    locallist=[]
    rlist=[]
    nlist=[]
    plist=[]
    options=node.getiterator('Search')
    if total==0:
        return [],[],[]
    for leaf in options:
        if leaf.get('URL') not in tosslist and (leaf.get('Term')=='' or leaf.get('Term')==None):
            (w,v,j)=urlParse(leaf.get('URL'))
            if leaf.text!='!':
                amount=int(leaf.text)
            else:
                amount=0
            if juris=='' or j==juris:
                locallist.append((amount,w,v,j))
    for tup in locallist:
        if tup[crit] not in rlist:
            rlist.append(tup[crit])
            nlist.append(tup[0])
            plist.append(float(tup[0])/total*100)
        else:
            place=rlist.index(tup[crit])
            oldnum=nlist.pop(place)
            nlist.insert(place,oldnum+tup[0])
            plist.pop(place)
            plist.insert(place,float(oldnum+tup[0])/total*100)
    #print 'out gatherAmount()'
    return rlist,nlist,plist

#Create a master list...for all dates, given an engine and criterion
#(jurisdiction or version or code), and possibly which jurisdiction we're
#looking at, create a list of dates wedded to totals and datasets.
def getMList(criterion,engine,juris):
    print 'in getMList()'
    mlist=[]
    siter=root.getiterator('Dataset')
    for dataset in siter:
        date=dataset.get('Date')
        if juris=='':
            temp=(date,engine)
        else:
            temp=(date,engine,juris)
        if criterion==0 and totals[temp]!=0:
            r=[totals[temp]]
            n=[totals[temp]]
            p=[totals[temp]]
        elif totals[temp]==0:
            r=[]
            n=[]
            p=[]
        else:
           r,n,p=gatherAmount(dataset.find('Webtrawl').find(engine),criterion,totals[temp],juris)
        mlist.append((date,r,n,p))
    print 'out getMList()'
    return mlist

#Based on the more complex graph generation functions below it, this creates
#a line for the total number of hits every day. It's pretty much a mini-script
#which only lacks some of the svg details.
def makeTotal(svg,color,engine,maxy,length,j):
    print 'in makeTotal()'
    Ox=100
    Oy=550
    xroom=800
    yroom=500
    xinterval=float(xroom)/length
    oldx=Ox
    oldy=Oy
    x=1
    totlist=[]
    siter=root.getiterator('Dataset')
    for dataset in siter:
        date=dataset.get('Date')
        if j=='':
            actnum=totals[(date,engine)]
        else:
            actnum=totals[(date,engine,j)]
        if oldx==Ox:
            oldx=Ox+x*xinterval
            oldy=Oy-float(actnum)*yroom/maxy
        newx=Ox+x*xinterval
        newy=Oy-float(actnum)*yroom/maxy
        nlin=line(oldx,oldy,newx,newy,stroke=color,stroke_width=1)
        svg.addElement(nlin)
        oldy=newy
        oldx=newx
        x+=1
    print 'out makeTotal()'
        
#Given a set of data--as a list of (date, label, number, percentage) tuples,
#the three svg files, a color, the max y, the logarithmic max y, and a flag
#for whether we should worry about starting dates, create the line

#The flag is for whether we can skip any data that's zeros--that is, whether
#this is a local graph (like jurisdictions) or a wider one, like cross-juris.
def makeLine(datalist,sp,sn,sl,color,maxy,logmaxy,all):
    print 'in makeLine()'
    Ox=100
    Oy=550
    xroom=800
    yroom=500
    xinterval=float(xroom)/len(datalist)
    oldx=Ox
    oldyp=Oy
    oldyn=Oy
    oldyl=Oy
    x=1
    begun=0
    skipped=0
    for (date,l,n,y) in datalist:
        if n!=0 and maxy!=0:
            begun=1
            if oldx==Ox:
                oldx=Ox+x*xinterval
                oldyp=Oy-y*yroom/100
                oldwyn=Oy-float(n)*yroom/maxy
                if n!=0:
                    oldyl=Oy-math.log10(n)*yroom/logmaxy
                else:
                    oldyl=Oy
            newx=Ox+x*xinterval
            newyp=Oy-y*yroom/100
            newyn=Oy-float(n)*yroom/maxy
            if n!=0:
                newyl=Oy-math.log10(n)*yroom/logmaxy
            else:
                newyl=Oy
            plin=line(oldx,oldyp,newx,newyp,stroke=color,stroke_width=1)
            sp.addElement(plin)
            nlin=line(oldx,oldyn,newx,newyn,stroke=color,stroke_width=1)
            sn.addElement(nlin)
            llin=line(oldx,oldyl,newx,newyl,stroke=color,stroke_width=1)
            sl.addElement(llin)
            oldyp=newyp
            oldyn=newyn
            oldyl=newyl
            oldx=newx
        elif begun==0 and all==1:
            newx=Ox+x*xinterval
            newyp=Oy
            newyl=Oy
            newyn=Oy
            plin=line(oldx,oldyp,newx,newyp,stroke=color,stroke_width=1)
            sp.addElement(plin)
            nlin=line(oldx,oldyn,newx,newyn,stroke=color,stroke_width=1)
            sn.addElement(nlin)
            llin=line(oldx,oldyl,newx,newyl,stroke=color,stroke_width=1)
            sl.addElement(llin)
            oldyp=newyp
            oldyn=newyn
            oldyl=newyl
            oldx=newx
            x+=1
        if begun==1:
            x+=1
        elif all==0:
            skipped+=1
            if skipped==len(datalist):
                xinterval=0
            else:
                xinterval=float(xroom)/(len(datalist)-skipped)
    print 'out makeLine()'

def genGraphs(engine,llist,which,jurisdiction,mlist):
    print 'in genGraphs()'
    colors=common.getColors()
    drp=drawing()
    drn=drawing()
    drl=drawing()
    svp=svg(None,1050,700)
    svn=svg(None,1050,700)
    svl=svg(None,1050,700)
    Ox=100
    Oy=550
    xroom=800
    yroom=500
    yline=line(Ox,Oy,Ox,Oy-yroom,stroke='black')
    xline=line(Ox,Oy,Ox+xroom,Oy,stroke='black')
    svp.addElement(xline)
    svp.addElement(yline)
    svn.addElement(xline)
    svn.addElement(yline)
    svl.addElement(xline)
    svl.addElement(yline)
    total=0
    spaces=0
    xinterval=float(xroom)/len(mlist)
    oldday=50
    oldyear='02'
    begun=0
    skipped=0
    for (d,l,n,p) in mlist:
        if l!=[] or begun==1:
            begun=1
            ed=d.split('-')
            if int(ed[2])<oldday:
                if ed[0][2:]!=oldyear:
                    ny=text(Ox+(spaces*xinterval),Oy+40,ed[0])
                    svp.addElement(ny)
                    svn.addElement(ny)
                    svl.addElement(ny)
                    oldyear=ed[0][2:]
                else:
                    string=ed[1]
                da=text(Ox+(spaces*xinterval)-10,Oy+20,ed[1])
                svp.addElement(da)
                svl.addElement(da)
                svn.addElement(da)
            spaces+=1
            oldday=int(ed[2])
        if begun==0:
            skipped+=1
            if skipped==len(mlist):
                xinterval=0
            else:
                xinterval=float(xroom)/(len(mlist)-skipped)
    for (d,l,n,p) in mlist:
        for number in n:
            if number>total:
                total=number
    if total!=0:
        logtotal=math.log10(total)
    else:
        logtotal=0
    for num in range(5):
        ptext=str(25*num)+'%'
        ntext="%.0f"%(total*.25*num)
        if total*.25*num==0:
            ltext="0"
        else:
            ltext="%.0f"%(math.pow(10,logtotal*.25*num))
        py=text(Ox-75,int(Oy-.25*num*yroom),ptext)
        ny=text(Ox-75,int(Oy-.25*num*yroom),ntext)
        ly=text(Ox-75,int(Oy-.25*num*yroom),ltext)
        ll=line(Ox,int(Oy-.25*num*yroom),Ox+xroom,int(Oy-.25*num*yroom),stroke_width=1,stroke='grey')
        svp.addElement(py)
        svn.addElement(ny)
        svl.addElement(ly)
        svp.addElement(ll)
        svn.addElement(ll)
        svl.addElement(ll)
    for num in range(len(llist)):
        datalist=[]
        for (d,l,n,p) in mlist:
            try:
                place=l.index(llist[num])
                datalist.append((d,l[place],n[place],p[place]))
            except:
                datalist.append((d,'',0,0))
        if which!=0:
            r=rect(width=10,height=10,x=925,y=(90+25*num),fill=colors[num],stroke='black')
            svp.addElement(r)
            svn.addElement(r)
            svl.addElement(r)
            t=text(945,25*(num+4),llist[num])
            svp.addElement(t)
            svn.addElement(t)
            svl.addElement(t)
        if jurisdiction=='':
            all=1
        else:
            all=0
        if which==0 and total!=0:
            makeTotal(svn,colors[0],engine,total,len(datalist),jurisdiction)
        else:
            makeLine(datalist,svp,svn,svl,colors[num],total,logtotal,all)
    if which==0:
        name='total_all_history_'
        title='Total Linkbacks'
        if jurisdiction!='':
            title='Total Linkbacks; Jurisdiction '+jurisdiction
            name='total_'+jurisdiction+'_history_'
    elif which==1:
        name='codes_all_history_'
        title='Codes'
        if jurisdiction!='':
            title='Codes; Jurisdiction '+jurisdiction
            name='codes_'+jurisdiction+'_history_'
    elif which==2:
        name='versions_all_history_'
        title='Versions'
        if jurisdiction!='':
            title='Versions; Jurisdiction '+jurisdiction
            name='versions_'+jurisdiction+'_history_'
    else:
        name='jurisdictions_all_history_'
        title='Jurisdictions'
    tpelement=text(100,25,engine+" Percentage Line Graph Of "+title,24)
    tnelement=text(100,25,engine+" Numerical Line Graph Of "+title,24)
    tlelement=text(100,25,engine+" Logarithmic Line Graph Of "+title,24)
    svp.addElement(tpelement)
    svn.addElement(tnelement)
    svl.addElement(tlelement)
    drp.setSVG(svp)
    drn.setSVG(svn)
    drl.setSVG(svl)
    if total!=0:
        if which!=0:
            drp.toXml('/web/teamspace/www/stats/svgs/'+name+'Percentage_'+engine+'.svg')
            drl.toXml('/web/teamspace/www/stats/svgs/'+name+'Logarithmic_'+engine+'.svg')
        drn.toXml('/web/teamspace/www/stats/svgs/'+name+'Numerical_'+engine+'.svg')
    print 'out genGraphs()'

excise()
getJuris()
gatherTotals()
for engine in common.getEngines():
#for engine in []:
    for number in [0,1,2,3]:
        mlist=getMList(number,engine,'')
        llist=mlist[len(mlist)-1][1]
        plist=mlist[len(mlist)-1][3]
        lplist=[]
        newllist=[]
        for l,p in zip(llist,plist):
            lplist.append((p,l))
        lplist.sort()
        lplist.reverse()
        for p,l in lplist:
            newllist.append(l)
        genGraphs(engine,newllist,number,'',mlist)
    for jurisdiction in jlist:
        for number in [0,1,2]:
            mlist=getMList(number, engine, jurisdiction)
            llist=mlist[len(mlist)-1][1]
            plist=mlist[len(mlist)-1][3]
            lplist=[]
            newllist=[]
            for l,p in zip(llist,plist):
                lplist.append((p,l))
            lplist.sort()
            lplist.reverse()
            for p,l in lplist:
                newllist.append(l)
            genGraphs(engine,newllist,number,jurisdiction,mlist)
