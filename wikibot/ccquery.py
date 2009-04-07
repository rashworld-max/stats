#!/usr/bin/env python
"""
Caculate and query CC license data.
"""
import collections
import sqlite3

REGION_FILE = 'continents.txt'

REGION_DICT = dict(
                AF = u'Africa',
                AS = u'Asia',
                ME = u'Middle East',
                EU = u'Europe',
                NA = u'North America',
                SA = u'Latin America',
                OC = u'Oceania',
                AN = u'Antarctica')

class CCQuery(object):
    """
    Database interface of CC license data.

    >>> q = CCQuery(':memory:')
    >>> q.add_linkbacks((
    ...        ('2316360','http://creativecommons.org/licenses/by/1.0/','Google',
    ...         '4690','2009-03-24 00:05:23','','by','1.0','Unported'),
    ...        ('2316245','http://creativecommons.org/licenses/by-nd/3.0/hk/','Google',
    ...         '84','2009-03-24 00:05:23','hk','by-nd','3.0','Hong Kong')
    ...     ))

    >>> [x for x in q.license_world()]
    [(u'by', 4690), (u'by-nd', 84)]

    >>> [x for x in q.license_by_juris(u'')]
    [(u'by', 4690)]
    
    >>> [x for x in q.license_by_region('as')]
    [(u'by-nd', 84)]
    
    >>> q.juris_code2name('hk')
    u'Hong Kong'

    >>> q.region_code2name('as')
    u'Asia'
    
    >>> q.all_juris()
    [u'', u'hk']

    >>> q.all_regions()
    [u'as']

    >>> q.del_all_linkbacks()
    >>> q.all_regions()
    []

    """
    def __init__(self, dbfile=':memory:'):
        self.conn = sqlite3.connect(dbfile)
        if not self._inited():
            self.init_db()
        return

    def __del__(self):
        self.conn.commit()
        return

    def commit(self):
        self.conn.commit()
        return

    def _inited(self):
        c = self.conn.execute('select name from sqlite_master where type = "table"')
        tables = [x[0] for x in c]
        if u'linkback' in tables:
            return True
        else:
            return False

    # Number of fields in linkback table, should update this once the table updated.
    NUM_FIELDS = 9

    def init_db(self):
        c = self.conn.cursor()
        c.executescript("""
            create table linkback(
                id text,
                url text,
                searchengine text,
                count integer,
                query_time text,
                juris_code text,
                license text,
                version text,
                juris text
            );
            create table region(
                code text,
                juris_code text
            );
        """)
        self._load_region()
        self.conn.commit()
        
        return

    def _load_region(self, fn = REGION_FILE):
        c = self.conn.cursor()
        for line in open(fn):
            line = line.split('#')[0] # strip comment
            try:
                region, country_code = line.split()
            except ValueError:
                continue
            region = region.lower()
            country_code = country_code.lower()
            c.execute("insert into region values(?,?)", (region, country_code))
        return

    def _fix_no_region(self):
        c = self.conn.cursor()
        c.execute("""
            select distinct juris_code, juris from linkback 
                where juris_code <> '' and juris_code not in 
                    (select juris_code from region)""")
        r = list(c)
        if r:
            import sys
            print >>sys.stderr, "Warning: the following jurisdictions have no corresponding region and will be deleted:"
            for j in r:
                print >>sys.stderr, j
            c.execute("""
                delete from linkback
                    where juris_code <> '' and juris_code not in 
                        (select juris_code from region)""")
        return

    def add_linkbacks(self, dataiter):
        """
        dataiter: An iterator of linkback datas as tuple, to be added into the database.
        """
        c = self.conn.cursor()
        c.executemany('insert into linkback values(%s)' % ( ','.join('?' * self.NUM_FIELDS) ), dataiter)
        self._fix_no_region()
        self.conn.commit()
        return

    def _del_linkbacks(self, where_clause, args=()):
        q = 'delete from linkback %s' % where_clause
        self.conn.execute(q, args)
        self.conn.commit()
        return

    def del_all_linkbacks(self):
        self._del_linkbacks('')
        return

    def del_juris(self, code):
        self._del_linkbacks('where juris_code=?', (code,))
        return

    
    def juris_code2name(self, code):
        """
        Get juris name from code.
        """
        c = self.conn.cursor()
        c.execute('select distinct juris from linkback where juris_code=?', (code,))
        result = c.fetchone()[0]
        return result
    
    def region_code2name(self, code):
        return REGION_DICT[code.upper()]

    def all_regions(self):
        """
        All regions.
        """
        c = self.conn.cursor()
        c.execute('select distinct code from (region natural join linkback)')
        result = [t[0] for t in c]
        return result

    def all_juris(self):
        """
        All juris avaiable in the linkback table.
        """
        c = self.conn.cursor()
        c.execute('select distinct juris_code from linkback')
        result = [t[0] for t in c]
        return result

    def juris_in_region(self, code):
        """
        All juris avaiable in a region specified by code.
        """
        c = self.conn.cursor()
        c.execute("""select distinct juris_code from (region natural join linkback)
                             where code=?""", (code,))
        result = [t[0] for t in c]
        return result

    def _license_query(self, where_clause, args=()):
        """
        Cunstruct and execute a select query with the where_clause, to get numbers of items in every license.
        """
        c = self.conn.cursor()
        q = 'select license, sum(count) from linkback %s group by license' % where_clause
        c.execute(q, args)
        return c

    def license_world(self):
        """
        Count of each license in the whole world.
        """
        return self._license_query('')

    def license_by_juris(self, juris_code):
        """
        Count of each license in a specific juris.
        """
        return self._license_query('where juris_code=?', (juris_code,))

    def license_by_region(self, region_code):
        """
        Count of each license in a specific region.
        """
        return self._license_query('where juris_code in (select juris_code from region where code=?)', (region_code,))

class Stats(object):
    """
    Caculate stats data based on an iterator which is grouped license data fetched by CCQuery.
    The stats data includes:
    1. absolute numbers per license and the total sum
    2. % numbers of the above
    3. freedom score

    >>> q = CCQuery(':memory:')
    >>> q.add_linkbacks((
    ...        ('2316360','http://creativecommons.org/licenses/by/1.0/','Google',
    ...         '30','2009-03-24 00:05:23','','by','1.0','Unported'),
    ...        ('2316245','http://creativecommons.org/licenses/by-nd/3.0/hk/','Google',
    ...         '10','2009-03-24 00:05:23','hk','by-nd','3.0','Hong Kong')
    ...        ))

    >>> s = Stats(q.license_world())
    >>> s.count('by')
    30
    >>> s.percent('by-nd')
    0.25
    >>> s.freedom_score
    5.25

    """
    # freedom score = 6*%by+4.5*%by-sa+3*%by-nd+4*%by-nc+2.5*%by-nc-sa+1*%by-nc-nd
    # Just tune this when needed.
    FREEDOM_SCORE_FACTORS = ( 
                ('by', 6),
                ('by-sa', 4.5),
                ('by-nd', 3),
                ('by-nc', 4),
                ('by-nc-sa', 2.5),
                ('by-nc-nd', 1)
            )
    # We only count these licenses (ie. exclude GPL, publicdomain, etc.)
    VALID_LICENSES = [x[0] for x in FREEDOM_SCORE_FACTORS]

    def __init__(self, license_data):
        """
        license_data: an iterator of (license, count) tuples
        """
        licenses = collections.defaultdict(int)
        total = 0
        for license, count in license_data:
            if license in self.VALID_LICENSES:
                licenses[license] += count
                total += count

        self.total = total
        self.licenses = licenses
    
        # Calculate freedom score
        score = 0
        for license, factor in self.FREEDOM_SCORE_FACTORS:
            score += self.percent(license) * factor
        self.freedom_score = score
        return
    
    def count(self, license):
        return self.licenses[license]

    def percent(self, license):
        if self.total:
            return float(self.count(license)) / self.total
        else:
            return float('nan')

