try:
    import dbconfig
except ImportError:
    import sys
    sys.path.append('..')
    import dbconfig

import datetime
from sqlalchemy.ext.sqlsoup import SqlSoup
import sqlalchemy

def last_flickr_estimate(date):
    '''Input: a datetime.date object.
    Output: a dict mapping CC license URIs to counts during that date'''
    db = SqlSoup(dbconfig.dburl)
    start_time = datetime.datetime(date.year, date.month, date.day, 0, 0)
    end_time = datetime.datetime(date.year, date.month, date.day, 23, 59, 59)
    all_q = sqlalchemy.select(
        [db.site_specific.c.utc_time_stamp],
        sqlalchemy.and_(
        db.site_specific.c.utc_time_stamp >= start_time,
        db.site_specific.c.utc_time_stamp < end_time,
        db.site_specific.c.site == 'http://www.flickr.com/'),
        distinct=True).execute()
    all = list(all_q)
    assert len(all) == 1 # there better be only one row per day; otherwise
    # which would be canonical?
    winning_row = all[0]
    winning_date_time = winning_row[0]

    # Now grab the data that was requested from us
    interesting_q = sqlalchemy.select(
        [db.site_specific.c.license_uri, db.site_specific.c.count],
        sqlalchemy.and_(
        db.site_specific.c.utc_time_stamp == winning_date_time,
        db.site_specific.c.site == 'http://www.flickr.com/'),
        distinct=True).execute()
    return dict(list(interesting_q))

if __name__ == '__main__':
    print last_flickr_estimate(datetime.date.today())
