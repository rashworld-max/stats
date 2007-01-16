#!/usr/bin/python
import datetime
FIRST_DATE=datetime.date(2004, 4, 1)
TODAY=datetime.date.today()
import charts

PROCESS_THIS = TODAY - datetime.timedelta(days=1)
while FIRST_DATE < PROCESS_THIS < TODAY:
    iso = PROCESS_THIS.isoformat()
    print "Going to process", iso,
    charts.main(iso)
    print "(done)."
    PROCESS_THIS -= datetime.timedelta(days=1)

