#!/usr/bin/env python
import sys
import os.path
sys.path.append( os.path.dirname( os.path.dirname(__file__) ) ) #parent dir of this file

import wikipedia

def test():
    site = wikipedia.getSite()
    page = wikipedia.Page(site, u'Sandbox')
    page.put(u'Hello, world! This is from ccbot.py')
    return

if __name__=='__main__':
    test()

