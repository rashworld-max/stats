#!/usr/bin/python

import sys
import gzip
import datetime
import sqlalchemy
from sqlalchemy.ext.sqlsoup import SqlSoup
import re
import dbconfig
import subprocess
import csv
import os
import xml.sax

# import license_xsl's convert
sys.path.append('./licensexsl_tools/licensexsl_tools/')
import convert

class MysqldumpCsvCooker(xml.sax.ContentHandler):
    def __init__(self, output_directory_base):
        xml.sax.ContentHandler.__init__(self)
        self.output_directory_base = output_directory_base
        if not os.path.isdir(output_directory_base):
            os.makedirs(output_directory_base, mode=0755)
        self.csv = None
        self.text_collecting = u''
        self.state = None
        self.current_table = None
        self.csv_fd = None
        self.field2csv_index = None
        self.row_collecting = None
        self.current_table = None
        self.current_field = None

    def startElement(self, name, attrs):
        if name == 'table_data':
            # Init a new table dump
            self.current_table = attrs['name']
            assert '/' not in self.current_table
            self.csv_fd = open(os.path.join(self.output_directory_base, self.current_table + '.csv'), 'w')
            self.csv = csv.writer(self.csv_fd)
            self.field2csv_index = {}
        
        if name == 'row':
            self.state = name
            self.row_collecting = []
        
        if name == 'field':
            if self.state == 'row':
                # If the CSV has no place for this row, put it somewhere
                if attrs['name'] not in self.field2csv_index:
                    index = len(self.field2csv_index)
                    self.field2csv_index[attrs['name']] = index
                self.current_field = self.field2csv_index[attrs['name']]
                self.text_collecting = ''

    def endElement(self, name):
        if name == 'row':
            if self.state == 'row':
                self.csv.writerow(self.row_collecting)
            self.state = None
        if name == 'field':
            if self.state == 'row':
                assert len(self.row_collecting) == self.current_field
                self.row_collecting.append(self.text_collecting)
                

        if name == 'table_data':
            self.csv_fd.close()

    def characters(self, ch):
        if ch.strip():
            assert self.state == 'row'
        self.text_collecting += ch

def main():
    # Strategy: Call mysqldump, and pass that to the above SAXon
    # This is because mysql is incapable of ensuring it generates proper CSV
    # output, but for some reason I trust its XML generation.

    # Lame hack: Manually parse dburl
    _, username, password, hostname, dbname = re.split('[:/@]+', dbconfig.dburl)
    # Lame hack (but safe, I suppose): Connect to a msyqldump
    command = ['mysqldump', '-u' + username, '-p' + password, '-h', hostname, '--xml', dbname]
    p = subprocess.Popen(command, stdin=subprocess.PIPE,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT,
                         close_fds=True)

    # Set up our parser
    parser = xml.sax.make_parser()
    parser.setContentHandler(MysqldumpCsvCooker('csv-dumps'))
    # And we're off to the races.
    parser.parse(p.stdout)

def date2path(date):
    return date.strftime('../csv-dumps/%Y-%m-%d/%H:%M:%S')

def already_done(date, table):
    return os.path.exists(os.path.join(date2path(date), table + '.csv'))

def which_to_process(dates, table, do_this_many = 10):
    do_these = set()
    for date in dates:
        if len(do_these) < do_this_many / 2:
            if not already_done(date, table):
                do_these.add(date)

    for date in reversed(dates):
        if len(do_these) < do_this_many:
            if not already_done(date, table):
                do_these.add(date)

    return do_these

def old_main():
    db = SqlSoup(dbconfig.dburl)
    table = sys.argv[1]
    assert table in ('simple', 'complex')
    dump_table(db, table)

def dump_table(db, table):
    table_cursor = getattr(db, table)
    all_dates = sqlalchemy.select([table_cursor._table.c.timestamp], distinct=True).execute()
    all_dates = sorted([thing[0] for thing in all_dates])
    yesterday = datetime.datetime.now() - datetime.timedelta(days=1)
    old_enough = [date for date in all_dates if date < yesterday]
    to_be_processed = which_to_process(old_enough, table)
    for date in to_be_processed:
        dump_one_date(db, table, table_cursor, date)

def dump_one_date(db, table, table_cursor, date):
    path = date2path(date)

    # separate by search engines
    search_engines_query = sqlalchemy.select([table_cursor._table.c.search_engine], distinct = True)
    search_engines = [thing[0] for thing in search_engines_query.execute()]
    search_engines.append(None)

    for engine in search_engines:
        dump_one_date_engine(db, table, table_cursor, date, path, engine)
        dump_one_date_engine_historical(date, path, engine)

def dump_one_date_engine_historical(date, path, engine):
    pass

def table_and_engine2basename(table, engine, mode='daily'):
    ''' Input: table=simple, engine=Google
    Output: linkbacks-Google'''

    nicename = {'simple': 'linkbacks',
                'complex': 'api_queries'}
    first = nicename[table]

    if engine:
        assert engine != 'ALL'
        last = engine
    else:
        last = 'ALL'

    return '-'.join( (first, mode, last) )

def dump_one_date_engine(db, table, table_cursor, date, path, engine):
    basename = table_and_engine2basename(table, engine)
    filename = os.path.join(path, basename + '.csv')
    if os.path.isdir(path):
        if os.path.exists(filename):
            print "Hmm,", filename, "already exists."
            return
    else:
        os.makedirs(path, mode=0755)
    fd = gzip.open(filename + '.working', 'w')
    if table == 'simple':
            order_by=[table_cursor._table.c.search_engine,
                      table_cursor._table.c.jurisdiction,
          table_cursor._table.c.license_type,
                      table_cursor._table.c.license_version]
    else:
        order_by = []
    query = (table_cursor._table.c.timestamp == date)
    if engine:
        # restrict on engine, too
        query &= (table_cursor._table.c.search_engine == engine)

    if table == 'simple':
        query &= (table_cursor._table.c.license_uri != 'http://creativecommons.org/licenses/publicdomain')
        query &= (table_cursor._table.c.license_uri != 'http://www.creativecommons.org')
        query &= (table_cursor._table.c.license_uri != 'http://creativecommons.org')
    just_my_data = table_cursor.select(query, order_by = order_by)
    out_csv = csv.writer(fd)
    keys = table_cursor._table._columns.keys() # Super ugly syntax.
    for thing in just_my_data:
        row = [clean(getattr(thing, k)) for k in keys] # omg, that syntax is horrible.
        if table == 'simple':
            # totally lame hack here - id2countryname
            row.append(convert.country_id2name(thing.jurisdiction, 'en_US'))
        out_csv.writerow(row) 
    fd.close()
    os.rename(filename + '.working', filename)

def clean(thing):
    if hasattr(thing, 'strftime'):
        return thing.strftime('%Y-%m-%d %H:%M:%S')
    return thing

if __name__ == '__main__':
    old_main()

