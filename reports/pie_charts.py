import datetime
# Jurisdictions
# for search_engine in 'Yahoo', 'Google', 'All The Web':
# select from simple where search_engine=search_engine
# and language=NULL and country=NULL

# But how to count jurisidictions?
# I could manually regex against the database results.
# That's hilariously inefficient.

# But it works for now, I suppose.
# Something smarter would be to store this in the database.

# Note that it should only do this for a particular 
# run, not every single run.  Might as well get the 
# maximum value in that timestamp column to do the 
# latest.  Be sure to get that max separately per 
# search engine.

import random

from sqlalchemy.ext.sqlsoup import SqlSoup
from sqlalchemy import * # Dangerously
import pylab
 
db = SqlSoup('mysql://root:@localhost/cc')

everything = db.simple.select(db.simple.c.timestamp != None)
search_engines = ['Google', 'All The Web', 'Yahoo']

def pie_chart(data, title):
    # make a square figure and axes
    pylab.figure(1, figsize=(8,8))
    
    labels = data.keys()
    fracs = [data[k] for k in labels]
    
    explode=[random.random() for k in labels]
    pylab.pie(fracs, explode=explode, labels=labels, autopct='%1.1f%%', shadow=True)
    pylab.title(title, bbox={'facecolor':0.8, 'pad':5})
    
    pylab.show()
    
def extract_jurisdiction(uri):
    splitted = uri.split('/')
    splitted = [k for k in splitted if k]
    numbers = [str(k) for k in range(9)]
    last = splitted[-1]
    for number in numbers:
        if number in last:
            print 'generic for', uri
            return 'Generic'
    if len(last) > 2:
        print 'generic for', uri
        return 'Generic'
    print splitted[-1], 'for',uri
    return splitted[-1]

def jurisdiction_data():
    # Some day, I'll do this all in SQL. :-)
    for engine in search_engines:
        just_us = [k for k in everything if k.search_engine == engine]
        if not just_us:
            print 'Hmm, nothing for', engine
        else:
            recent_stamp = max([k.timestamp for k in just_us])
            recent = [k for k in just_us if k.timestamp == recent_stamp]

            # Okay, now gather the data.
            data = {}
            for event in recent:
                jurisdiction = extract_jurisdiction(event.license_uri)
                data[jurisdiction] = data.get(jurisdiction, 0) + event.count
                print 'added', event.count, 'to', jurisdiction
            pie_chart(data, title=engine)

if __name__ == '__main__':
    jurisdiction_data()

