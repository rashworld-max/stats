#!/usr/bin/python

import sqlalchemy

# connect to the database
dburl="mysql://dannyc:asdf@localhost/stats"
db = sqlalchemy.create_engine(dburl)

# store all rows of simple in result
text = db.text("SELECT * FROM simple")
result = text.execute()

fetched = result.fetchone()
while fetched: # while there is another row
    id = jurisdiction = license_version = license_type = None
    id = fetched[0]

    # parse the license_uri
    segments = fetched[1].split("/")
    if len(segments) > 5:
        license_type = segments[4]
        if len(segments) > 6:
            license_version = segments[5]
            if len(segments) > 7:
                jurisdiction = segments[6]
                update_text = "UPDATE simple SET license_type = '%s', license_version = '%s', jurisdiction = '%s' WHERE id = %s" % (license_type, license_version, jurisdiction, id)
            else:
                update_text = "UPDATE simple SET license_type = '%s', license_version = '%s' WHERE id = %s" % (license_type, license_version, id)
        else:
            update_text = "UPDATE simple SET license_type = '%s' WHERE id = %s" % (license_type, id)
    else: # nothing to update, continue to the next row
        fetched = result.fetchone() 
        continue

    # commit the new data
    update = db.text(update_text)
    update.execute() 

    # fetch the next row
    fetched = result.fetchone() 
