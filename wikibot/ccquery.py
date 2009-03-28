#!/usr/bin/env python
"""
Caculate and query CC license data.
"""
import collections
import sqlite3

class CCQuery(object):
    """
    Database interface of CC license data.

    >>> q = CCQuery()
    >>> q.add_linkbacks((
    ...        ('2316360','http://creativecommons.org/licenses/by/1.0/','Google',
    ...         '4690','2009-03-24 00:05:23','','by','1.0','Unported'),))

    >>> [x for x in q.license_world()]
    [(u'by', 1)]

    >>> [x for x in q.license_by_juris(u'')]
    [(u'by', 1)]

    """
    def __init__(self, dbfile=':memory:'):
        self.conn = sqlite3.connect(dbfile)
        self.init_db()
        return

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
            create table continent(
                code text,
                country_code text
            );
        """)
        self.NUM_FIELDS = 9
        return

    def add_linkbacks(self, dataiter):
        """
        dataiter: An iterator of linkback datas as tuple, to be added into the database.
        """
        c = self.conn.cursor()
        c.executemany('insert into linkback values(%s)' % ( ','.join('?' * self.NUM_FIELDS) ), dataiter)
        return

    def _license_query(self, where_clause, args=()):
        """
        Cunstruct and execute a select query with the where_clause, to get numbers of items in every license.
        """
        c = self.conn.cursor()
        q = 'select license, count(*) from linkback %s group by license' % where_clause
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

class Stats(object):
    """
    Caculate stats data based on an iterator which is grouped license data fetched by CCQuery.
    The stats data includes:
    1. absolute numbers per license and the total sum
    2. % numbers of the above
    3. freedom score

    >>> q = CCQuery()
    >>> q.add_linkbacks((
    ...        ('2316360','http://creativecommons.org/licenses/by/1.0/','Google',
    ...         '4690','2009-03-24 00:05:23','','by','1.0','Unported'),
    ...        ('2316245','http://creativecommons.org/licenses/by-nd/3.0/hk/','Google',
    ...         '84','2009-03-24 00:05:23','hk','by-nd','3.0','Hong Kong')
    ...        ))

    >>> s = Stats(q.license_world())
    >>> s.count('by')
    1
    >>> s.percent('by-nd')
    0.5
    >>> s.freedom_score
    4.5

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

    def __init__(self, license_data):
        """
        license_data: an iterator of (license, count) tuples
        """
        licenses = collections.defaultdict(int)
        total = 0
        for license, count in license_data:
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
        return float(self.count(license)) / self.total

