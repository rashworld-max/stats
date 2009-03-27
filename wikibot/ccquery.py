#!/usr/bin/env python
"""
Caculate and query CC license data.
"""
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
