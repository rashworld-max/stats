#!/usr/bin/python
import datetime

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

def csv_row2dict(row, utc_time_stamp):
    '''
    >>> parsed = csv_row2dict(['/creativecommons/by-2.0/', '3'], datetime.datetime(2005,3,2))
    >>> parsed['count']
    3
    >>> parsed['license_uri']
    'http://creativecommons.org/licenses/by/2.0/'
    >>> parsed['utc_time_stamp']
    datetime.datetime(2005, 3, 2, 0, 0)
    >>> parsed['site']
    'http://www.flickr.com/'
    '''

    ret = {}

    # Validate the input. Unpythonic, but life is short.
    assert type(utc_time_stamp) == type(datetime.datetime.now())

    # Copy data out of the row and into our dict
    internal_license_name, count = row
    ret['license_uri'] = flickr2license[internal_license_name]
    ret['count'] = int(count)
    ret['site'] = 'http://www.flickr.com/'
    ret['utc_time_stamp'] = utc_time_stamp
    return ret

def main():
    # Strategy: for each date from 2004-04-01 through tomorrow, see if we have a Flickr CSV
    # if so, import it
    # if that worked, rename the file on disk to .csv.bak
    # For the utc_time_stamp, we either (a) use the mtime of the file, if it is within
    # one day of the claimed date, or (b) assume that the snapshot took place at noon UTC,
    pass

if __name__ == '__main__':
    main()
