#!/usr/bin/python

'''
Sets the license_type, license_version and jurisdiction fields
in the database to NULL
'''

import sqlalchemy

def nullify_fields():
    text = db.text("UPDATE simple SET license_type = NULL, "\
        "license_version = NULL, jurisdiction = NULL")
    result = text.execute()

if __name__ == '__main__':
    # connect to the database
    dburl="mysql://dannyc:asdf@localhost/stats"
    db = sqlalchemy.create_engine(dburl)

    # nullify the fields
    nullify_fields()
