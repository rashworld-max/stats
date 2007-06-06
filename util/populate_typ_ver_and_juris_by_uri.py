#!/usr/bin/python

"""
A script for running through the database and updating the
license_type, license_version and jurisdiction fields by
parsing data out of the license_uri.
"""

import sqlalchemy

def parse_fields_from_uri(uri):
    '''parses the license_type, license_version and jurisdiction
    from the uri and returns it in a list in that order'''
    license_type = license_version = jurisdiction = None
    segments = uri.split('/')
    if len(segments) > 4:
        license_type = segments[4]
        if len(segments) > 5:
            license_version = segments[5]
            if len(segments) > 6:
                jurisdiction = segments[6]
    return [license_type, license_version, jurisdiction]
 
# connect to the database
dburl="mysql://dannyc:asdf@localhost/stats"
db = sqlalchemy.create_engine(dburl)

# store all rows of simple in result
text = db.text("SELECT * FROM simple")
result = text.execute()

fetched = result.fetchone()
while fetched: # while there is another row
    uri = fetched[1]
    field_list = parse_fields_from_uri(uri)
    if not any(field_list):
        # nothing to update, continue to the next row
        fetched = result.fetchone() 
        continue

    # commit the new data
    id = fetched[0]
    field_list.append(id)
    field_list = tuple(field_list)
    update_text = "UPDATE simple SET license_type = '%s', " \
        "license_version = '%s', jurisdiction = '%s' WHERE id = %s" \
            % field_list
    update = db.text(update_text)
    update.execute() 

    # fetch the next row
    fetched = result.fetchone() 
