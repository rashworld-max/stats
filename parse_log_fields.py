#!/usr/bin/python

'''
Usage: python parse_log_fields.py <logfile>

A script to parse the license versions, license types and jurisdictions
of a HTTP request for png images from the logs
'''

# TODO add timestamp to insert for each query
# TODO maintain counts of certain types of things, like in simple

import re
import sys
import sqlalchemy
import dbconfig

def parse_fields_from_re_group(group):
    license_type = license_version = jurisdiction = 'NULL'
    match = group[3:]
    fields = match.split('/')
    if 'png' in fields[0]: # no fields present
        pass
    elif 'png' in fields[1]: # license_type present
        license_type = fields[0]
    elif 'png' in fields[2]: # license_type and license_version present
        license_type = fields[0]
        license_version = fields[1]
    elif 'png' in fields[3]: # all fields present
        license_type = fields[0]
        license_version = fields[1]
        jurisdiction = fields[2]
    else:
        raise RuntimeError, \
        'ERROR IN PARSE_LOG_FIELDS.parse_fields_from_re_group '\
            'fields: %s' % fields
    return [license_type, license_version, jurisdiction]

def main():
    # open the log file specified in the cmdargs
    log = open(sys.argv[1])

    # connect to the database
    db = sqlalchemy.create_engine(dbconfig.dburl)

    # compile the regex
    pattern = r'/l/.*png'
    p = re.compile(pattern)


    # loop through all the lines and insert the data
    # into the DB if the regex matches... otherwise, record the miss
    while True:
        try:
            line = log.next()
        except StopIteration:
            return
        m = p.search(line)
        if m == None:
            print "Error!  Regex %s did not match the following line:\n%s"\
                % (pattern, line)
            del line
            continue
        else:
            del line
            try: 
                field_list = parse_fields_from_re_group(m.group())
            except RuntimeError, e:
                print e
                continue
            field_list = tuple(field_list)
            if field_list[0] == 'NULL': # all three fields are null
                insert_text = "INSERT INTO apache_log (license_type, "\
                    "license_version, jurisdiction) VALUES (%s, %s, %s)" \
                        % field_list
            elif field_list[1] == 'NULL': # l_v and juris are null
                insert_text = "INSERT INTO apache_log (license_type, "\
                    "license_version, jurisdiction) VALUES ('%s', %s, %s)" \
                        % field_list
            elif field_list[2] == 'NULL': # jurisdiction is null
                insert_text = "INSERT INTO apache_log (license_type, "\
                    "license_version, jurisdiction) "\
                        "VALUES ('%s', '%s', %s)" % field_list
            else: # no null arguments
                insert_text = "INSERT INTO apache_log (license_type, "\
                    "license_version, jurisdiction) "\
                    "VALUES ('%s', '%s', '%s')" % field_list

            # execute the query
            update = db.text(insert_text)
            update.execute()

    log.close()

if __name__ == '__main__':
    main()
