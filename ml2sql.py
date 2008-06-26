#!/usr/bin/python
## This code converts the Mike Linksvayer tab-separated values format
## into link_counts events.

import link_counts
import datetime
import dbconfig

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
    def __init__(self, fd, db = dbconfig.dburl):
        '''Takes an ML-format fd as input.
        Creates some internal state and does some SQL queries as a result.'''
        self.lc = link_counts.LinkCounter(db, 'old/api/licenses.xml')
        self.date = "RIGGED TO EXPLODE"
        self.parse(fd)

    def parse(self, fd):
        seen_lengths = set()
        for row in fd:
            things = row.split()
            if len(things) in [5,6]:
                engines = {}
                date = things.pop(0)
                time = things.pop(0)
                url = things.pop(-1)
                if url == 'SUM':
                    print 'discarding due to sum:', things
                    continue
                engines['yahoo'] = try_to_intify(things.pop(0))
                engines['google'] = try_to_intify(things.pop(0))
                if things:
                    engines['atw'] = try_to_intify(things.pop(0))
                print engines
            else:
                print 'discarding', things

            

if __name__ == '__main__':
    import sys
    Importer(sys.stdin)
