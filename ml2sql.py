#!/usr/bin/python
## This code converts the Mike Linksvayer tab-separated values format
## into link_counts events.

import link_counts
import datetime
import dbconfig

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
            set.add(len(things))
        print set
