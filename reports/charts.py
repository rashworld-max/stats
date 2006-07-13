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

# FIXME: This code assumes you're always looking at the "simple"
# table.  That's dumb.

# FIXME: Remove fname parameter; calculate it each time.

# Note that it should only do this for a particular 
# run, not every single run.  Might as well get the 
# maximum value in that timestamp column to do the 
# latest.  Be sure to get that max separately per 
# search engine.

from sqlalchemy.ext.sqlsoup import SqlSoup
from sqlalchemy import * # Dangerously
import pylab, matplotlib
 
db = SqlSoup('mysql://root:@localhost/cc')

search_engines = ['Google', 'All The Web', 'Yahoo', 'MSN']
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

def bar_chart(data, title, fname):
    labels = data.keys()
    values = [data[k] for k in labels]
    # Bar supports multiple, well, bars
    # So we could do all search engines at once if we wanted
    # But that's harder to integrate with for_search_engines
    # So forget it.
    ind = pylab.arange(len(values))  # the x locations for the groups
    width = 0.35       # the width of the bars
    pylab.p1 = pylab.bar(ind, values, width, color='r')
    
    pylab.ylabel('ylabel!?')
    pylab.title(title)
    pylab.xticks(ind+(width/2.0), labels)
    pylab.xlim(-width,len(ind))
    pylab.yticks(pylab.arange(0,41,10))
    
    pylab.show()
    pylab.savefig(fname)
    pylab.close()
    
    # http://matplotlib.sourceforge.net/screenshots/barchart_demo.py shows how to smarten the legend
    pass

def pie_chart(data, title, fname):
    # make a square figure and axes
    pylab.figure(figsize=(8,8))

    print 'data was',data
    labels = data.keys()
    fracs = [data[k] for k in labels]
    
    explode=[0.05 for k in labels]
    pylab.pie(fracs, explode=explode, labels=labels, autopct='%1.1f%%', shadow=False, colors=('b', 'g', 'r', 'c', 'm', 'y', 'w'))

    ## I would have a legend, but they often overlap with the pie itself.
    #pylab.legend(prop=matplotlib.font_manager.FontProperties('x-small'))
    #leg = pylab.gca().get_legend()
    #ltext  = leg.get_texts()
    #pylab.setp(ltext, fontsize='small')
    #pylab.legend()

    pylab.title(title, bbox={'facecolor':0.8, 'pad':5})
    pylab.savefig(fname)
    pylab.close() # This is key!

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

def for_search_engine(chart_fn, data_fn, table):
    for engine in search_engines:
        just_us = [k for k in everything if k.search_engine == engine]
        if not just_us:
            print 'Hmm, nothing for', engine
        else:
            recent_stamp = select([func.max(table.c.timestamp)]).execute().fetchone()[0]
            recent = table.select(and_(table.c.timestamp == recent_stamp, table.c.search_engine == engine)) # I should be able to avoid execute() above, I hear.
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
        # Now flatten out everything < 0.5%
        total = sum([data[k] for k in data])
        for k in data.keys():
            if data[k] <  (0.005 * total):
                data['Other'] = data.get('Other', 0) + data[k]
                del data[k]
        return data
    def chart_fn(data, engine):
        return pie_chart(data, "%s Jurisdiction data" % engine, "/home/paulproteus/public_html/tmp/%s.png" % engine)

    for_search_engine(chart_fn, data_fn, db.simple)

def property_bar_chart():
    def data_fn(things):
        too_much = property_counts(things)
        if 'total' in too_much:
            del too_much['total']
        return too_much
    
    def chart_fn(data, engine):
        return bar_chart(data, "%s property bar chart" % engine, "/home/paulproteus/public_html/tmp/%s-properties.png" % engine)
    for_search_engine(chart_fn, data_fn, db.simple)

if __name__ == '__main__':
    jurisdiction_data()

