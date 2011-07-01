#!/usr/bin/python

import os
import sys
import lc_util


def sanity_check():
    # First, verify Tor is working okay.
    import socks_monkey
    socks_monkey.enable_tor()
    
    import urllib2

    # Sometimes checking the IP through fails TOR with an httplib error of
    # BadStatusLine, which causes the whole stats runner to fail for that day.
    # Make a small effort to reboot and retry using Asheesh's existing
    # try_thrice() function.
    try:
        tor_result = lc_util.try_thrice(urllib2.urlopen, 'http://checkip.dyndns.org')
        tor_ip = tor_result.read()
    except Exception, e:
        print "Failed to get get TOR IP address: " + e

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
