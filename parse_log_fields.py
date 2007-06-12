#!/usr/bin/python

'''
Usage: python parse_log_fields.py <logfile> [dryrun] [debug]

A script to parse the license versions, license types and jurisdictions
of a HTTP request for png images from the apache logs

This throws  2 warnings when it is not a dryrun (that is, when it interacts
with the MySQL database), but they are of no consequence.
'''

# TODO maintain counts of certain types of things, like in simple

import re
import datetime
import sys
import sqlalchemy
import dbconfig

month_map = {'Jan' : 1,
             'Feb' : 2,
             'Mar' : 3,
             'Apr' : 4,
             'May' : 5, 
             'Jun' : 6, 
             'Jul' : 7,
             'Aug' : 8,
             'Sep' : 9,
             'Oct' : 10,
             'Nov' : 11,
             'Dec' : 12}

def parse_date(apache_log_date):
    ''' Takes in a date  as a string in apache-log format     example: '[10/Jun/2007:06:38:39 +0000]'
    and returns a datetime object corresponding to it '''
    try:
        first_colon_index = apache_log_date.index(':')

        # deal with the date
        date_part = apache_log_date[1:first_colon_index]
        date_part = date_part.split('/')
        day, month, year = date_part
        
        # deal with the time
        time_part = apache_log_date[first_colon_index+1:first_colon_index+9]
        time_part = time_part.split(':')
        hour, minute, second = time_part

        # convert them all to ints and create a datetime object
        x =  [int(z) for z in year, month_map[month], day, 
                                    hour, minute, second]
        return datetime.datetime(*x)
    except:
        raise RuntimeError, \
        'ERROR IN PARSE_LOG_FIELDS.parse_date '\
            'date/time: %s ' % \
                [year, month_map[month], day, hour, minute, second]

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

    # compile the regexs
    pattern = r'/l/.*png'
    p = re.compile(pattern)
    date_pattern = '\[.*\]'
    d_p = re.compile(date_pattern)

    # loop through all the lines and insert the data
    # into the DB if the regex matches... otherwise, record the miss
    while True:
        try:
            line = log.next()
        except StopIteration:
            return
        m = p.search(line)
        d_m = d_p.search(line)
        if m == None:
            print "Error!  Regex %s did not match the following line:\n%s"\
                % (pattern, line)
            del line
            continue
        elif d_m == None:
            print "Error!  Regex %s did not match the following line:\n%s"\
                % (date_pattern, line)
            del line
            continue
        else:
            del line
            try: 
                field_list = parse_fields_from_re_group(m.group()) 
                log_date = parse_date(d_m.group()) # returns datetime object
            except RuntimeError, e:
                print e
                continue
            field_list.append(log_date.__str__())
            field_list = tuple(field_list)
            if field_list[0] == 'NULL': # all three fields are null
                insert_text = "INSERT INTO apache_log (apache_log_id, license_type, license_version, jurisdiction, timestamp) VALUES ('', %s, %s, %s, '%s')"  % field_list
            elif field_list[1] == 'NULL': # l_v and juris are null
                insert_text = "INSERT INTO apache_log (apache_log_id, license_type, license_version, jurisdiction, timestamp) VALUES ('', '%s', %s, %s, '%s')"  % field_list
            elif field_list[2] == 'NULL': # jurisdiction is null
                insert_text = "INSERT INTO apache_log (apache_log_id, license_type, license_version, jurisdiction, timestamp) VALUES ('', '%s', '%s', %s, '%s')"  % field_list
            else: # no null arguments
                insert_text = "INSERT INTO apache_log (apache_log_id, license_type, license_version, jurisdiction, timestamp) VALUES ('', '%s', '%s', '%s', '%s')"  % field_list

            if debug:
                print insert_text
            # execute the query
            if not dryrun:
                try:
                    update = db.text(insert_text)
                    update.execute()
                except Exception, e: 
                    print 'SQL STATEMENT EXECUTION FAILED', e

    log.close()

if __name__ == '__main__':
    global dryrun, debug
    if 'dryrun' in sys.argv[1:]: 
        dryrun = 1
    else: 
        dryrun = 0
    if 'debug' in sys.argv[1:]:
        debug = 1
    else:
        debug = 0
    main()


