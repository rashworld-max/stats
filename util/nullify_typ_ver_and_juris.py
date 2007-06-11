#!/usr/bin/python

'''
Sets the license_type, license_version and jurisdiction fields
in the database to NULL
'''

import sqlalchemy
import dbconfig

def nullify_fields():
    text = db.text("UPDATE simple SET license_type = NULL, "\
        "license_version = NULL, jurisdiction = NULL")
    result = text.execute()

if __name__ == '__main__':
    # connect to the database
    db = sqlalchemy.create_engine(dbconfig.dburl)

    # nullify the fields
    nullify_fields()
