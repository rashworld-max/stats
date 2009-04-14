"""
This is used to bootstrap the DB. After bootstrapped, it will not be used in
the workflow of the robot.
"""

import config
import linkback_reader
import ccquery

REGION_FILE = 'continents.txt'
COUNTRY_CODE_DATA = 'country_codes_Jan09.txt'

REGION_DICT = dict(
                AF = u'Sub-Saharan Africa',
                AS = u'Asia',
                ME = u'Middle East and North Africa',
                EU = u'Europe',
                NA = u'North America',
                SA = u'Latin America',
                OC = u'Oceania',
                AN = u'Antarctica')


class Juris(object):
    def __init__(self):
        self.name = None
        self.fips = None
        self.region = None
        self.is_ported = 0
        return


def bootstrap(q=None):
    if q is None:
        q = ccquery.CCQuery(config.DB_FILE)

    # Fill the region table
    for code, name in REGION_DICT.items():
        q.add_region(code, name)
    
    juris = {}
    # Load juris - region map
    for line in open(REGION_FILE):
        line = line.split('#')[0] # strip comment
        try:
            region, code = line.split()
        except ValueError:
            continue
        region = region.upper()
        code = code.upper()

        j = Juris()
        j.region = region
        juris[code] = j

    # Get country FIPS code data
    data = open(COUNTRY_CODE_DATA)
    data.readline() # pass first line 
    for line in data:
        items = line.split('\t')
        name = items[0][1:-1].strip()
        fips = items[1][1:-1].strip()
        code = items[2][1:-1].strip()
        if not fips or not code:
            continue
        juris[code].fips = fips
        juris[code].name = name

    # Use linkback CSV data for jurisdiction names
    csv = linkback_reader.most_recent()
    for data in csv:
        count = int(data[3])
        if count==0:
            continue
        code = data[5]
        if not code or code=='deed-music':
            continue
        name = data[8]
        code = code.upper()
        juris[code].name = name
        juris[code].is_ported = 1

    # Fill the juris table
    for code, j in juris.items():
        q.add_juris(j.name, code, j.fips, j.region, j.is_ported)

    q.commit()

    return q

if __name__=='__main__':
    bootstrap()
