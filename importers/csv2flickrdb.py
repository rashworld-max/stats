#!/usr/bin/python
import datetime
import os
import glob
import csv
from sqlalchemy.ext.sqlsoup import SqlSoup
import sys
sys.path.append('..')
import dbconfig

# for now, copy-pasta from the reports
# later this will be reorganized, but this is pretty one-off import code

FLICKR_DATA_BASE_PATH = '/home/paulproteus/stats/flickr/data/'

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

def filename2utc_datetime(filename, _skip_stat = False, _mock_ctime = None):
    '''Take a filename that stat()s to a real file.
    Output a datetime object that represents a UTC timestamp according to the following rules:
    * parse the filename to pull out an ISO date
    * create a datetime object set to that date at noon
    * if the file has st_ctime within 12 hours (either direction) of that stamp,
      return the st_ctime as a datetime
    * else return the first created datetime
    >>> filename2utc_datetime('/nowhere/2009-03-12.csv', _mock_ctime = 0)
    datetime.datetime(2009, 3, 12, 12, 0)
    >>> filename2utc_datetime('/nowhere/2009-03-12.csv', _mock_ctime = 1236884413)
    datetime.datetime(2009, 3, 12, 19, 0, 13)
    '''
    abspath = os.path.abspath(filename)
    filebase = os.path.basename(abspath)
    before_dot = filebase.rsplit('.', 1)[0]
    # parse file name into ISO date
    y,m,d = map(int, before_dot.split('-'))
    ret = datetime.datetime(y, m, d, 12, 0) # unless otherwise specified

    # handle the _mock_ctime for testing
    if _mock_ctime is None:
        ctime = os.stat(abspath).st_ctime
    else:
        ctime = _mock_ctime
    # either way, calculate abs val of difference
    from_file = datetime.datetime.utcfromtimestamp(ctime)
    abs_val_of_diff = abs(ret - from_file)
    if abs_val_of_diff < datetime.timedelta(hours=12):
        ret = from_file
    return ret

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
    db = SqlSoup(dbconfig.dburl)
    for filename in sorted(glob.glob(FLICKR_DATA_BASE_PATH + '/*.csv')):
        if 'cumulative' in filename:
            continue
        utc_date_time = filename2utc_datetime(filename)
        csv_fd = csv.reader(open(filename))
        print 'Importing', filename,
        for row in csv_fd:
            importable = csv_row2dict(row, utc_date_time)
            db.site_specific.insert(**importable)
            db.flush()
        # since that worked, rename the filename
        os.rename(filename, filename + '.imported')
        print '...done.'

if __name__ == '__main__':
    main()
