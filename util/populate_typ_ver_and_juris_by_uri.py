#!/usr/bin/python

"""
A script for running through the database and updating the
license_type, license_version and jurisdiction fields by
parsing data out of the license_uri.
"""

# TODO this could probably be made more efficient by using cursors instead 
# of sending out a seperate UPDATE x if ID = y; SQL query for each row,
# but it's the disk that we're bottlenecked at so the performance boost
# might be negligable

import sqlalchemy
import dbconfig

def parse_fields_from_uri(uri):
    '''parses the license_type, license_version and jurisdiction
    from the uri and returns it in a list in that order'''
    license_type = license_version = jurisdiction = 'NULL'
    segments = uri.split('/')
    if len(segments) > 4:
        license_type = segments[4]
        if len(segments) > 5:
            license_version = segments[5]
            # the second clause of this next if comes into play when the
            # uri has a trailing slash, for example:
            # http://creativecommons.org/licenses/by-nc/1.0/
            if len(segments) > 6 and segments[6] != '':
                    jurisdiction = segments[6]
    return [license_type, license_version, jurisdiction]

if __name__ == '__main__':
    # connect to the database
    db = sqlalchemy.create_engine(dbconfig.dburl)

    # store all rows of simple with null in one of the 3 fields in result
    text = db.text("SELECT * FROM simple WHERE jurisdiction IS NULL OR "\
        "license_type IS NULL OR license_version IS NULL") 
    result = text.execute()

    fetched = result.fetchone()
    while fetched: # while there is another row
        uri = fetched[1]
        field_list = parse_fields_from_uri(uri)
        if field_list[0] == 'NULL' and field_list[1] == 'NULL' \
            and field_list[2] == 'NULL':
            # nothing to update, continue to the next row
            fetched = result.fetchone()
            continue

        # commit the new data
        id = fetched[0]
        field_list.append(id)
        field_list = tuple(field_list)

        # this additional switch below is necessary because it is imperative
        # that fields that are NULL are NOT quoted as they go into the
        # DB... otherwise, the attribute will be the quoted string
        # 'NULL', not the NULL value... of course, they show up as the
        # same on the mysql command line... very confusing (footnote1)

        if field_list[0] == 'NULL': # all three fields are null
            update_text = "UPDATE simple SET license_type = %s, " \
                "license_version = %s, jurisdiction = %s WHERE id = %s" \
                    % field_list
        elif field_list[1] == 'NULL': # l_v and juris are null
            update_text = "UPDATE simple SET license_type = '%s', " \
                "license_version = %s, jurisdiction = %s WHERE id = %s" \
                    % field_list
        elif field_list[2] == 'NULL': # jurisdiction is null
            update_text = "UPDATE simple SET license_type = '%s', " \
                "license_version = '%s', jurisdiction = %s WHERE id = %s" \
                    % field_list
        else: # no null arguments
            update_text = "UPDATE simple SET license_type = '%s', " \
              "license_version = '%s', jurisdiction = '%s' WHERE id = %s" \
                    % field_list
        update = db.text(update_text)
        update.execute()

        # fetch the next row
        fetched = result.fetchone() 


# (footnote1)
# I tried to put this into some function like quote_if_not_null(field) 
# in order to eliminate this switch but ran into problems.
# Either the python interpreter switches quotes back and forth for
# convinience on the interactive prompt to reduce clutter or there is 
# some way I don't know about (or maybe it does not exist) to enforce
# single or double quotes to stay with a string across invocations...
# For example string s = 'asdf' would show up as '"asdf"' on the prompt
# regardless if I did a s = "'"+s+"'" or a s = '"'+s'"' ... I don't feel
# too compelled to solve this as it would require a deep understanding of
# python internals and the solution here works just fine, although it is
# a bit inelegant.
