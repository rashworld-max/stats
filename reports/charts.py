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

from sqlalchemy.ext.sqlsoup import SqlSoup
from sqlalchemy import * # Dangerously
import pylab, matplotlib
 
db = SqlSoup('mysql://paulproteus:zomg@einstein.cs.jhu.edu/paulproteus')

everything = db.simple.select(db.simple.c.timestamp != None)
search_engines = ['Google', 'All The Web', 'Yahoo']
all_html_colors = [k.lower() for k in ['AliceBlue', 'AntiqueWhite', 'Aqua', 'Aquamarine', 'Azure', 'Beige', 'Bisque', 'Black', 'BlanchedAlmond', 'Blue', 'BlueViolet', 'Brown', 'BurlyWood', 'CadetBlue', 'Chartreuse', 'Chocolate', 'Coral', 'CornflowerBlue', 'Cornsilk', 'Crimson', 'Cyan', 'DarkBlue', 'DarkCyan', 'DarkGoldenRod', 'DarkGray', 'DarkGreen', 'DarkKhaki', 'DarkMagenta', 'DarkOliveGreen', 'Darkorange', 'DarkOrchid', 'DarkRed', 'DarkSalmon', 'DarkSeaGreen', 'DarkSlateBlue', 'DarkSlateGray', 'DarkTurquoise', 'DarkViolet', 'DeepPink', 'DeepSkyBlue', 'DimGray', 'DodgerBlue', 'Feldspar', 'FireBrick', 'FloralWhite', 'ForestGreen', 'Fuchsia', 'Gainsboro', 'GhostWhite', 'Gold', 'GoldenRod', 'Gray', 'Green', 'GreenYellow', 'HoneyDew', 'HotPink', 'IndianRed', 'Indigo', 'Ivory', 'Khaki', 'Lavender', 'LavenderBlush', 'LawnGreen', 'LemonChiffon', 'LightBlue', 'LightCoral', 'LightCyan', 'LightGoldenRodYellow', 'LightGrey', 'LightGreen', 'LightPink', 'LightSalmon', 'LightSeaGreen', 'LightSkyBlue', 'LightSlateBlue', 'LightSlateGray', 'LightSteelBlue', 'LightYellow', 'Lime', 'LimeGreen', 'Linen', 'Magenta', 'Maroon', 'MediumAquaMarine', 'MediumBlue', 'MediumOrchid', 'MediumPurple', 'MediumSeaGreen', 'MediumSlateBlue', 'MediumSpringGreen', 'MediumTurquoise', 'MediumVioletRed', 'MidnightBlue', 'MintCream', 'MistyRose', 'Moccasin', 'NavajoWhite', 'Navy', 'OldLace', 'Olive', 'OliveDrab', 'Orange', 'OrangeRed', 'Orchid', 'PaleGoldenRod', 'PaleGreen', 'PaleTurquoise', 'PaleVioletRed', 'PapayaWhip', 'PeachPuff', 'Peru', 'Pink', 'Plum', 'PowderBlue', 'Purple', 'Red', 'RosyBrown', 'RoyalBlue', 'SaddleBrown', 'Salmon', 'SandyBrown', 'SeaGreen', 'SeaShell', 'Sienna', 'Silver', 'SkyBlue', 'SlateBlue', 'SlateGray', 'Snow', 'SpringGreen', 'SteelBlue', 'Tan', 'Teal', 'Thistle', 'Tomato', 'Turquoise', 'Violet', 'VioletRed', 'Wheat', 'White', 'WhiteSmoke', 'Yellow', 'YellowGreen']]

# Thanks, Will.
# Needs tests.
def urlParse(url):
    jurisdiction=''
    elements=url.split('/')
    if len(elements) >= 6:
        which=elements[4]
        if which=='publicdomain':
            which='pd'
        version=elements[5]
        if version=='':
            version='1.0'
        if len(elements)>6:
            jurisdiction=elements[6]
        if jurisdiction=='' or jurisdiction=='us' or jurisdiction=='deed-music':
            jurisdiction='generic'
        # attribs: if it's a CC license, then the list of CC attributes
        if which in ('GPL', 'LGPL', 'devnations', 'sampling', 'pd'): # How to handle PD later in later graphs?
            attribs = []
        else:
            if which in ('sampling+', 'nc-sampling+'):
               attribs = ['by','nc','nd']
            else:
               attribs = which.split('-')
            print url
            assert(('by' in attribs) or
                   ('nc' in attribs) or
                   ('nd' in attribs) or
                   ('sa' in attribs))
    else:
        which, version, jurisdiction, attribs = None, None, None, []
    ret = {'which': which, 'version': version, 'jurisdiction': jurisdiction, 'attribs': tuple(attribs)}
    return ret

def get_all_urlParse_results(key):
    ''' Neat for testing! '''
    ret = set()
    for r in [urlParse(k.license_uri)[key] for k in everything]:
        ret.add(r)
    return ret

def pie_chart(data, title):
    # http://home.gna.org/pychart/examples/pietest.py if this gets too bad
    # http://matplotlib.sourceforge.net/screenshots/barchart_demo.py shows how to smarten the legend
    # make a square figure and axes
    pylab.figure(1, figsize=(8,8))
    
    labels = data.keys()
    fracs = [data[k] for k in labels]
    
    explode=[0.05 for k in labels]
    pylab.pie(fracs, explode=explode, colors=all_html_colors, labels=labels, autopct='%1.1f%%', shadow=True)
    pylab.legend(prop=matplotlib.font_manager.FontProperties('x-small'))
    #leg = pylab.gca().get_legend()
    #ltext  = leg.get_texts()
    #pylab.setp(ltext, fontsize='small')
    #pylab.legend()

    pylab.title(title, bbox={'facecolor':0.8, 'pad':5})
    pylab.show()

def bar_chart(data, title):
    pass

def date_chart(data, title):
    from matplotlib.dates import YearLocator, MonthLocator, DateFormatter
    import datetime

    ''' Untested.  Tee-hee.
    Based on http://matplotlib.sourceforge.net/screenshots/date_demo.py '''
    months   = MonthLocator()  # every month
    days     = pylab.DayLocator()    # daily?
    monthsFmt = DateFormatter('%m')

    keys = data.keys()
    keys.sort()
    dates = [pylab.date2num(k) for k in keys]
    values = [data[k] for k in keys]
    print values

    ax = pylab.subplot(111)
    pylab.plot_date(dates, values, '-')

    # format the ticks
    #ax.xaxis.set_major_locator(months)
    #ax.xaxis.set_major_formatter(monthsFmt)
    #ax.xaxis.set_minor_locator(days)
    #ax.autoscale_view()

    # format the coords message box
    #ax.fmt_xdata = DateFormatter('%Y-%m-%d')
    
    pylab.grid(True)
    pylab.show()

def simple_aggregate_date_chart():
    for engine in search_engines:
        just_us = [k for k in everything if k.search_engine == engine]
        if not just_us:
            print 'Hmm, nothing for', engine
        else:
            stamps = [k.timestamp for k in just_us]
            data = {}
            for stamp in stamps:
                data[stamp] = sum([k.count for k in just_us if k.timestamp == stamp])
            date_chart(data, 'zomg')

def property_counts(things):
    ''' Input: A subset of everything.
    Output: A hash of prop -> count, plus an extra "total"->total'''
    ret = {}
    for thing in things:
        props = urlParse(thing.license_uri)['attribs']
        for prop in props:
            ret[prop] = ret.get(prop, 0) + thing.count
        ret['total'] = ret.get('total',0) + thing.count
    return ret

def property_bar_chart():
    """ A whole lot of repeated code.  It's getting embarrassing. """
    for engine in search_engine:
        just_us = [k for k in everything if k.search_engine == engine]
        if not just_us:
            print 'Hmm, nothing for', engine
        else:
            recent_stamp = max([k.timestamp for k in just_us])
            recent = [k for k in just_us if k.timestamp == recent_stamp ]
            data = property_counts(things)
            bar_chart(data, '%s Linkbacks, Property Percentages' % engine) # Does not exist! :-)

def property_pie_chart():
    """ This chart is worse than useless.  It's flat-out wrong. """
    for engine in search_engines:
        just_us = [k for k in everything if k.search_engine == engine]
        if not just_us:
            print 'Hmm, nothing for', engine
        else:
            recent_stamp = max([k.timestamp for k in just_us])
            recent = [k for k in just_us if k.timestamp == recent_stamp ]

            data = {}
            for event in recent:
                properties = urlParse(event.license_uri)['attribs']
                if 'by' in properties or 'nc' in properties or 'nd' in properties or 'sa' in properties:
                    for prop in properties:
                        data[prop] = data.get(prop, 0) + event.count
            # Kay, now graph it.
            pie_chart(data, title="Pie chart of properties from " + engine)

def for_search_engine(chart_fn, data_fn):
    for engine in search_engines:
        just_us = [k for k in everything if k.search_engine == engine]
        if not just_us:
            print 'Hmm, nothing for', engine
        else:
            recent_stamp = max([k.timestamp for k in just_us])
            recent = [k for k in just_us if k.timestamp == recent_stamp ]
            data = data_fn(recent)
            chart_fn(data, engine)

def jurisdiction_data():
    def data_fn(recent):
        # Okay, now gather the data.
        data = {}
        for event in recent:
            jurisdiction = urlParse(event.license_uri)['jurisdiction']
            if jurisdiction:
                data[jurisdiction] = data.get(jurisdiction, 0) + event.count
                print 'added', event.count, 'to', jurisdiction
        return data
    def chart_fn(data, engine):
        return pie_chart(data, "%s Jurisdiction data" % engine)

    for_search_engine(chart_fn, data_fn)

if __name__ == '__main__':
    jurisdiction_data()

