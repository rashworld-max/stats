#!/usr/bin/python
import datetime
FIRST_DATE=datetime.date(2004, 4, 1)
TODAY=datetime.date.today()
import charts

PROCESS_THIS = FIRST_DATE
while PROCESS_THIS < TODAY:
    iso = PROCESS_THIS.isoformat()
    print "Going to process", iso,
    charts.main(iso)
    print "(done)."
    PROCESS_THIS += datetime.timedelta(days=1)

