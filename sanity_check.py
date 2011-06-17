#!/usr/bin/python

import os
import sys


def sanity_check():
    # First, verify Tor is working okay.
    import socks_monkey
    socks_monkey.enable_tor()
    
    import urllib2
    tor_ip = urllib2.urlopen('http://checkip.dyndns.org/').read()

    socks_monkey.disable_tor()
    my_ip = urllib2.urlopen('http://checkip.dyndns.org/').read()

    assert tor_ip != my_ip

    # Second, verify MySQL connectivity.
    import link_counts
    import dbconfig
    lc = link_counts.LinkCounter(dbconfig.dburl, 'old/api/licenses.xml')
    # just accessing the table "simple" using sqlsoup is a test:
    lc.db.simple

if __name__ == '__main__':
    sanity_check()
    sys.exit(0) # true
