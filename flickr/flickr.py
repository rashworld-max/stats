#!/usr/bin/python

import csv
import BeautifulSoup

def main(infd, outfd):
    soup = BeautifulSoup.BeautifulSoup(infd.read())
    license2count = {}
    for morecc in soup('p', {'class': 'MoreCC'}):
        number = morecc('b')[0].string.replace(',', '')
        license = morecc('a')[0]['href'] # in Flickr form, not CC form!
        assert 'by' in license # really a CC license, right?

        license2count[license] = number

    csv_writer = csv.writer(outfd)
    csv_writer.writerows([(lic, license2count[lic]) for lic in license2count])

if __name__ == '__main__':
    import sys
    main(sys.stdin, sys.stdout)
