#!/usr/bin/python

from sqlalchemy.ext.sqlsoup import SqlSoup
import dbconfig
import csv
import gzip

def main():
    db = SqlSoup(dbconfig.dburl)
    for table in ('simple', 'complex'):
        out_csv = csv.writer(gzip.GzipFile(table + '.csv.gz', 'w'))
        table_cursor = getattr(db, table)
        everything = table_cursor._table.select().execute()
        for thing in everything:
            out_csv.writerow(list(thing))

if __name__ == '__main__':
    main()
