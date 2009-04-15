#!/usr/bin/env python
"""
Caculate and query CC license data.
"""
import collections
import sqlite3
import csv

import bootstrap_db

SCHEME_SQL = """
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
            name text,
            code text
        );

        create table juris(
            name text,
            code text,
            fips text,
            region_code text,
            is_ported integer
        );
"""

class CCQuery(object):
    """
    Database interface of CC license data.

    >>> q = CCQuery(':memory:')
    >>> import bootstrap_db
    >>> q = bootstrap_db.bootstrap(q)
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

    >>> q.all_regions()
    [u'AF', u'AS', u'EU', u'ME', u'NA', u'OC', u'SA']

    >>> q.del_all_linkbacks()
    >>> [x for x in q.license_world()] 
    []

    """
    def __init__(self, dbfile=':memory:'):
        self.conn = sqlite3.connect(dbfile)
        if not self._inited():
            self.init_scheme()
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

    def init_scheme(self):
        self.conn.executescript(SCHEME_SQL)
        self.conn.commit()        
        return

    def bootstrap(self):
        return bootstrap_db.bootstrap(self)

    def export_table(self, table, file):
        c = self.conn.cursor()
        c.execute('select * from %s'%table)
        csvfile = csv.writer(file)
        csvfile.writerows(c)
        return

    def import_table(self, table, file):
        self.clear_table(table)
        csvfile = csv.reader(file)
        rowlen = self.len_table(table)
        self.conn.executemany('insert into %s values(%s)'%(table, ','.join('?'*rowlen)), csvfile)
        return

    def len_table(self, table):
        c = self.conn.cursor()
        c.execute('pragma table_info(%s)'%(table))
        rowlen = len(c.fetchall())
        return rowlen

    def clear_table(self, table):
        self.conn.execute('delete from %s'%table)
        return

    def add_region(self, name, code):
        code = code.upper()
        self.conn.execute('insert into region values(?,?)', (name, code))
        return

    def add_juris(self, name, code, fips, region_code, is_ported):
        code = code.upper()
        self.conn.execute('insert into juris values(?,?,?,?,?)', 
                (name, code, fips, region_code, is_ported))
        return

    def _check_juris(self):
        """
        Check for nonexistent juris and new juris.
        """
        # Remove linkback data which has no entry in juris table
        c = self.conn.cursor()
        c.execute("""
            select distinct juris_code, juris from linkback 
                where juris_code <> '' and juris_code not in 
                    (select code from juris)""")
        r = list(c)
        if r:
            import sys
            print >>sys.stderr, "Warning: We have no information about the following " \
                    "jurisdictions in our database, thus its' linkback data will be ignored:"
            for j in r:
                print >>sys.stderr, j
            c.execute("""
                delete from linkback
                    where juris_code <> '' and juris_code not in 
                        (select code from juris)""")

        # Set is_ported for new coming juris
        self.conn.execute("""
            update juris set is_ported=1
                where is_ported=0 and code in (select juris_code from linkback)""")
        return

    def add_linkbacks(self, dataiter):
        """
        dataiter: An iterator of linkback datas as tuple, to be added into the database.
        """
        dataiter = ( x for x in dataiter if int(x[3])>0 ) # filter out entries with count=0
        c = self.conn.cursor()
        c.executemany('insert into linkback values(?, ?, ?, ?, ?, upper(?), ?, ?, ?)', dataiter)
        self._check_juris()
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
        code = code.upper()
        self._del_linkbacks('where juris_code=?', (code,))
        return


    def _juris_code2x(self, x, code):
        """
        Get something from code.
        """
        code = code.upper()
        c = self.conn.cursor()
        c.execute('select %s from juris where code=?'%x, (code,))
        result = c.fetchone()[0]
        return result
    
    def juris_code2name(self, code):
        """
        Get juris name from code.
        """
        return self._juris_code2x('name', code)
   
    def juris_code2fips(self, code):
        """
        Get juris name from code.
        """
        return self._juris_code2x('fips', code)

    def region_code2name(self, code):
        """
        Get region name from code.
        """
        code = code.upper()
        c = self.conn.cursor()
        c.execute('select name from region where code=?',(code,))
        result = c.fetchone()[0]
        return result

    def all_regions(self):
        """
        All regions.
        """
        c = self.conn.cursor()
        c.execute('select distinct region_code from juris where code<>"" and is_ported<>0')
        result = [t[0] for t in c]
        return result

    def all_juris(self):
        """
        All juris avaiable with ported license.
        """
        c = self.conn.cursor()
        c.execute('select distinct code from juris where is_ported<>0')
        result = [t[0] for t in c]
        return result

    def juris_in_region(self, code):
        """
        All juris avaiable in a region specified by code.
        """
        code = code.upper()
        c = self.conn.cursor()
        c.execute("""select distinct code from juris where is_ported<>0 and
                             region_code=?""", (code,))
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
        juris_code = juris_code.upper()
        return self._license_query('where juris_code=?', (juris_code,))

    def license_by_region(self, region_code):
        """
        Count of each license in a specific region.
        """
        region_code = region_code.upper()
        return self._license_query('where juris_code in (select code from juris where region_code=?)', (region_code,))

class Stats(object):
    """
    Caculate stats data based on an iterator which is grouped license data fetched by CCQuery.
    The stats data includes:
    1. absolute numbers per license and the total sum
    2. % numbers of the above
    3. freedom score

    >>> q = CCQuery(':memory:')
    >>> import bootstrap_db
    >>> q = bootstrap_db.bootstrap(q)
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
        
        if total==0:
            raise ValueError("Linkback data is empty.")
        
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

