#!/usr/bin/python
## This code converts the Mike Linksvayer tab-separated values format
## into link_counts events.

import link_counts
import datetime
import dbconfig

def license_clean(s):
    if '://' not in s:
        s = 'http://' + s
    # that should be it
    return s

def try_to_intify(n):
    if n in ('!', '<font', ')'):
        # just to point out the kind of trash in these columns
        # there's some ghastly binary trash in the file, too, which gets
        # caught below.
        return None
    try:
        return int(n)
    except ValueError:
        return None

class Importer:
    def __init__(self, fd, ending_date, db = dbconfig.dburl):
        '''Takes an ML-format fd as input.
        Creates some internal state and does some SQL queries as a result.'''
        self.lc = link_counts.LinkCounter(db, 'old/api/licenses.xml')
        self.date = "RIGGED TO EXPLODE"
        self.ending_datetime = datetime.datetime(*map(int, ending_date.split('-')))
        self.parse(fd)

    def parse(self, fd):
        seen_lengths = set()
        for row in fd:
            things = row.split()
            if len(things) in [5,6]:
                engines = {}
                date = things.pop(0)
                time = things.pop(0)
                url = license_clean(things.pop(-1))
                if url == 'SUM':
                    print 'discarding due to sum:', things
                    continue
                engines['Yahoo'] = try_to_intify(things.pop(0))
                engines['Google'] = try_to_intify(things.pop(0))
                if things:
                    engines['All The Web'] = try_to_intify(things.pop(0))

                # Calculate proper datetime value
                try:
                    year, month, day =map(int, date.split('-'))
                    hour, minute, second =map(int, time.split(':'))
                except ValueError:
                    continue # screw this "date"
                nice_datetime = datetime.datetime(year, month, day,
                                     hour, minute, second)
                
                if nice_datetime < self.ending_datetime:
                    if '/licenses/' in url:
                        for engine in engines:
                            count = engines[engine]
                            if count is not None:
                                pass
                                self.lc.record(cc_license_uri = url,
                                  search_engine=engine, count=count,
                                  timestamp = nice_datetime)
                        print date, url, engines
            else:
                print 'discarding', things

            

if __name__ == '__main__':
    import sys
    if len(sys.argv) != 2:
        print 'Usage: python ml2sql.py 2005-06-21 < /tmp/some_file.txt'
        print ''
        print 'That will import some_file.txt into the database for all'
        print 'dates inside it that are less than (not equal to) that date.'
    else:
        Importer(sys.stdin, sys.argv[1])
