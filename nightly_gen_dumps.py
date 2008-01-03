#!/usr/bin/python

import re
import dbconfig
import subprocess
import csv
import os
import xml.sax

class MysqldumpCsvCooker(xml.sax.ContentHandler):
    def __init__(self, output_directory_base):
        self.output_directory_base = output_directory_base
        if not os.path.isdir(output_directory_base):
            os.makedirs(output_directory_base, mode=0755)
        self.csv = None
        self.text_collecting = u''
        self.state = None

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
            self.current_state = None
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
    dbtype, username, password, hostname, dbname = re.split('[:/@]+', dbconfig.dburl)
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

def which_to_process(dates):
    return dates[-1:]

def old_main():
    db = SqlSoup(dbconfig.dburl)
    for table in ('simple', 'complex'):
        table_cursor = getattr(db, table)
        all_dates = sorted(sqlalchemy.select([table_cursor._table.c.timestamp], distinct=True))
        only_before_today = [date[0] for date in all_dates if date[0] < datetime.today()]
        to_be_processed = which_to_process(only_before_today)
        for date in to_be_processed:
            path = date.strftime('%Y-%m-%d/%H:%M:%S')
            #os.makedirs(path, mode=0755)
            just_my_data = table_cursor.filter(table_cursor.timestamp == date).all()
            for thing in just_my_data:
                print 'rooftop, whoa'

if __name__ == '__main__':
    main()
