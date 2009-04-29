#!/usr/bin/python

# for now, copy-pasta from the reports
# later this will be reorganized, but this is pretty one-off import code

flickr2license = {
    '/creativecommons/by-nd-2.0/':
    'http://creativecommons.org/licenses/by-nd/2.0/',
    '/creativecommons/by-nc-2.0/':
    'http://creativecommons.org/licenses/by-nc/2.0/',
    '/creativecommons/by-2.0/':
    'http://creativecommons.org/licenses/by/2.0/',
    '/creativecommons/by-nc-nd-2.0/':
    'http://creativecommons.org/licenses/by-nc-nd/2.0/',
    '/creativecommons/by-sa-2.0/':
    'http://creativecommons.org/licenses/by-sa/2.0/',
    '/creativecommons/by-nc-sa-2.0/':
    'http://creativecommons.org/licenses/by-nc-sa/2.0/'}

def main():
    # Strategy: for each date from 2004-04-01 through tomorrow, see if we have a Flickr CSV
    # if so, import it
    # if that worked, rename the file on disk to .csv.bak
    pass

if __name__ == '__main__':
    main()
