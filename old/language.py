#!/usr/bin/python

import urllib
import re
import string
import time
from time import localtime, strftime
from lxml import etree
from lxml.etree import Element

langs=["lang_ar",
       "lang_bg",
       "lang_ca",
       "lang_zh-CN",
       "lang_zh-TW",
       "lang_hr",
       "lang_cs",
       "lang_da",
       "lang_nl",
       "lang_en",
       "lang_et",
       "lang_fi",
       "lang_fr",
       "lang_de",
       "lang_el",
       "lang_iw",
       "lang_hu",
       "lang_is",
       "lang_id",
       "lang_it",
       "lang_ja",
       "lang_ko",
       "lang_lv",
       "lang_lt",
       "lang_no",
       "lang_fa",
       "lang_pl",
       "lang_pt",
       "lang_ro",
       "lang_ru",
       "lang_sr",
       "lang_sk",
       "lang_sl",
       "lang_es",
       "lang_sv",
       "lang_th",
       "lang_tr"]

def parse():
    urls=[]
    urls.append("http://creativecommons.org/licenses/publicdomain/")
    parsetree=etree.parse('api/licenses.xml')
    parseroot=parsetree.getroot()
    for element in parseroot.getiterator('jurisdiction'):
        if element.get('id')=='-':
            for sub in element.getchildren():
                urls.append(sub.get('uri'))
    return urls

def run():
    date=strftime("%Y-%m-%d",localtime())
    root=Element("Dataset")
    tree=etree.ElementTree(element=root)
    root.set("Date",date)
    prefix = "http://search.yahoo.com/search?_adv_prop=web&x=op&ei=UTF-8&fr=fp-top&va=link:"
    midfix = "&va_vt=any&vp_vt=any&vo_vt=any&ve_vt=any&vd=all&vst=0&vf=all&vm=i&fl=1&vl="
    suffix = "&n=10"
    urls=parse()
    for l in langs:
        total=0
        node=etree.SubElement(root,"Trawl")
        node.set("Lang",l)
        for url in urls:
            try:
                results=urllib.urlopen(prefix+url+midfix+l+suffix).read()
                count=re.search('of about <.*?>(\S+?)<',results).group(1)
                count = string.replace(count,',','')
                total += int(count)
            except:
                count = '!'
            subnode=etree.SubElement(node,"Search")
            subnode.set("URI",url)
            subnode.text=str(count)
            time.sleep(1)
        totnode=etree.SubElement(node,"Total")
        totnode.text=str(total)
    fileopen=open('/web/teamspace/www/stats/lang.xml','w')
    tree.write(fileopen)
run()
