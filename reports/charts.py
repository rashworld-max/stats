from __future__ import generators # YOW!
import pdb
try:
    import psyco
except ImportError:
    pass
import pylab
from matplotlib.dates import YearLocator, MonthLocator, DateFormatter
from matplotlib.dates import MONDAY, SATURDAY
import datetime
from sqlalchemy.ext.sqlsoup import SqlSoup
import sqlalchemy
import os
import pylab, matplotlib
# Jurisdictions
# for search_engine in 'Yahoo', 'Google', 'All The Web':
# select from simple where search_engine=search_engine
# and language=NULL and country=NULL

# FIXME: My HTML templating is pure evil.

# But how to count jurisidictions?
# I could manually regex against the database results.
# That's hilariously inefficient.

# But it works for now, I suppose.
# Something smarter would be to store this in the database.

# FIXME: This code assumes you're always looking at the "simple"
# table.  That's dumb.

# Note that it should only do this for a particular 
# run, not every single run.  Might as well get the 
# maximum value in that timestamp column to do the 
# latest.  Be sure to get that max separately per 
# search engine.

MAX_DATE = datetime.datetime(3000, 1, 1) # In the grim future of humanity
                                         # there are only license
                                         # usage statistics

# FIXME: Move this somewhere I can use it later.
class ListCycle:
    def __init__(self, l):
        self.l = l
        self.index = 0
    def next(self):
        if self.index >= len(self.l):
            self.index = -1
        ret = self.l[self.index]
        self.index += 1
        return ret

BASEDIR='/home/paulproteus/public_html/tmp/'
def fname(s):
    return os.path.join(BASEDIR, s)

db = SqlSoup('mysql://root:@localhost/cc')
 
search_engines = ['Google', 'All The Web', 'Yahoo', 'MSN']
all_html_colors = [k.lower() for k in ['AliceBlue', 'AntiqueWhite', 'Aqua', 'Aquamarine', 'Azure', 'Beige', 'Bisque', 'Black', 'BlanchedAlmond', 'Blue', 'BlueViolet', 'Brown', 'BurlyWood', 'CadetBlue', 'Chartreuse', 'Chocolate', 'Coral', 'CornflowerBlue', 'Cornsilk', 'Crimson', 'Cyan', 'DarkBlue', 'DarkCyan', 'DarkGoldenRod', 'DarkGray', 'DarkGreen', 'DarkKhaki', 'DarkMagenta', 'DarkOliveGreen', 'Darkorange', 'DarkOrchid', 'DarkRed', 'DarkSalmon', 'DarkSeaGreen', 'DarkSlateBlue', 'DarkSlateGray', 'DarkTurquoise', 'DarkViolet', 'DeepPink', 'DeepSkyBlue', 'DimGray', 'DodgerBlue', 'Feldspar', 'FireBrick', 'FloralWhite', 'ForestGreen', 'Fuchsia', 'Gainsboro', 'GhostWhite', 'Gold', 'GoldenRod', 'Gray', 'Green', 'GreenYellow', 'HoneyDew', 'HotPink', 'IndianRed', 'Indigo', 'Ivory', 'Khaki', 'Lavender', 'LavenderBlush', 'LawnGreen', 'LemonChiffon', 'LightBlue', 'LightCoral', 'LightCyan', 'LightGoldenRodYellow', 'LightGrey', 'LightGreen', 'LightPink', 'LightSalmon', 'LightSeaGreen', 'LightSkyBlue', 'LightSlateBlue', 'LightSlateGray', 'LightSteelBlue', 'LightYellow', 'Lime', 'LimeGreen', 'Linen', 'Magenta', 'Maroon', 'MediumAquaMarine', 'MediumBlue', 'MediumOrchid', 'MediumPurple', 'MediumSeaGreen', 'MediumSlateBlue', 'MediumSpringGreen', 'MediumTurquoise', 'MediumVioletRed', 'MidnightBlue', 'MintCream', 'MistyRose', 'Moccasin', 'NavajoWhite', 'Navy', 'OldLace', 'Olive', 'OliveDrab', 'Orange', 'OrangeRed', 'Orchid', 'PaleGoldenRod', 'PaleGreen', 'PaleTurquoise', 'PaleVioletRed', 'PapayaWhip', 'PeachPuff', 'Peru', 'Pink', 'Plum', 'PowderBlue', 'Purple', 'Red', 'RosyBrown', 'RoyalBlue', 'SaddleBrown', 'Salmon', 'SandyBrown', 'SeaGreen', 'SeaShell', 'Sienna', 'Silver', 'SkyBlue', 'SlateBlue', 'SlateGray', 'Snow', 'SpringGreen', 'SteelBlue', 'Tan', 'Teal', 'Thistle', 'Tomato', 'Turquoise', 'Violet', 'VioletRed', 'Wheat', 'White', 'WhiteSmoke', 'Yellow', 'YellowGreen']]

# Thanks, Will.
# Needs tests.
urlParse_cache = {}
def urlParse(url):
    global urlParse_cache
    if url in urlParse_cache:
        return urlParse_cache[url]
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
        if which in ('GPL', 'LGPL', 'devnations', 'sampling', 'pd'): # FIXME: How to handle PD later in later graphs?
            attribs = []
        else:
            if which in ('sampling+', 'nc-sampling+'):
               attribs = ['by','nc','nd']
            else:
               attribs = which.split('-')
            assert(('by' in attribs) or
                   ('nc' in attribs) or
                   ('nd' in attribs) or
                   ('sa' in attribs))
        # now canonicalize which
        whichparts = which.split('-')
        whichparts.sort()
        which = '-'.join(whichparts)
    else:
        which, version, jurisdiction, attribs = None, None, None, []
    ret = {'which': which, 'version': version, 'jurisdiction': jurisdiction, 'attribs': tuple(attribs)}
    urlParse_cache[url] = ret
    return ret

def get_all_urlParse_results(key, everything):
    ''' Neat for testing! '''
    ret = set()
    for r in [urlParse(k.license_uri)[key] for k in everything]:
        ret.add(r)
    return ret

def bar_chart(data, title,ylabel='',labelfmt='%1.1f'):
    pylab.figure(figsize=(8,8))
    data = clean_dict(data)
    labels = data.keys()
    values = [data[k] for k in labels]
    # Bar supports multiple, well, bars
    # So we could do all search engines at once if we wanted
    # But that's harder to integrate with for_search_engines
    # So forget it.
    ind = pylab.arange(len(values))  # the x locations for the groups
    width = 0.35       # the width of the bars
    p1 = pylab.bar(ind, values, width, color='r',
                   yerr=[0] * len(values),xerr=[0] * len(values))
    # xerr,yerr is matplotlib workaround; not needed in 0.87.4
    
    pylab.ylabel(ylabel)
    pylab.title(title)
    pylab.xticks(ind+(width/2.0), labels)
    pylab.xlim(-width,len(ind))
    #pylab.yticks(pylab.arange(0,41,10))

    # Labels!
    for x,y in zip(xrange(len(values)), values):
        pylab.text(x+width/2., y, labelfmt % y, va='bottom', ha='center')
    
    pylab.savefig(fname(title))
    pylab.close()
    
    # http://matplotlib.sourceforge.net/screenshots/barchart_demo.py shows how to smarten the legend
    return title

def pie_chart(data, title):
    # make a square figure and axes
    pylab.figure(figsize=(8,8))

    # here's some fun: sort the labels by the values (-:
    data_unpacked = [ (data[key], key) for key in data ]
    data_unpacked.sort()

    fracs = [ datum[0] for datum in data_unpacked ]
    labels= [ datum[1] for datum in data_unpacked ]
    
    explode=[0.05 for k in labels]
    patches, texts, autotexts = pylab.pie(fracs, explode=explode, labels=labels, autopct='%1.1f%%', shadow=False, colors=('b', 'g', 'r', 'c', 'm', 'y', 'w')) # pctradius=0.85

    # Shrink the both text chunks' font size
    proptease = matplotlib.font_manager.FontProperties()
    proptease.set_size('xx-small') # I don't think it goes smaller than xx
    pylab.setp(autotexts, fontproperties=proptease)
    pylab.setp(texts, fontproperties=proptease)

    ## I would have a legend, but they often overlap with the pie itself.
    #pylab.figlegend()
    #pylab.legend(prop=matplotlib.font_manager.FontProperties('x-small'))
    #leg = pylab.gca().get_legend()
    #ltext  = leg.get_texts()
    #pylab.setp(ltext, fontsize='small')
    #pylab.legend()

    pylab.title(title, bbox={'facecolor':'0.8', 'pad':5})
    pylab.savefig(fname(title))
    pylab.close() # This is key!
    return title

def date_chart_data(engine, table):
    s = sqlalchemy.select([sqlalchemy.func.sum(table.c.count), table.c.timestamp], sqlalchemy.and_(table.c.search_engine == engine, table.c.timestamp < MAX_DATE))
    s.group_by(table.c.timestamp)
    data = s.execute() # sum() returns a string, BEWARE!

    send_this = {}
    for datum in data:
        value, timestamp = datum
        value = int(value) # sqlalchemy bug: SUM() returns a string
        send_this[timestamp] = value
    return send_this

def find_month_count_that_fits(start_date, end_date, max_ticks):
    factors = (1, 2, 3, 4, 6, 12, 23, 36, 48) # That should cover us

    for factor in factors:
        delta = datetime.timedelta(days=(factor*30)) # HACK!  Not correct. :-)
        dates = matplotlib.dates.drange(start_date, end_date, delta)
        if len(dates) <= max_ticks:
            return factor
    raise AssertionError, "Really?  Gawrsh!"

def clean_dict(d):
    ''' Input: A dict.
    Output: A dict with all the keys in d that had values, mapped to the right values. '''
    ret = {}
    for key in d:
        if d[key]:
            ret[key] = d[key]
    return ret

def date_chart(lots_of_data, title):
    # FIXME: Use horizontal space more efficiently
    """ data is now input as a dict that maps label -> a dict that maps dates to data
    So we can't guarantee the order of keys. """

    # First things first: Make a clean copy of the lots_of_data dict
    lots_of_data = clean_dict(lots_of_data)
    pylab.figure(figsize=(8,8))
    ax = pylab.subplot(111) # We're going to have a plot, okay?

    colors = ListCycle( ('b', 'g', 'r', 'c', 'm', 'y', 'k') )

    # We'll order the labels descending based on the last values
    # so we'll avoid plotting until we've got all the values
    graph_this_data = []

    # We assume the date ranges are the same...
    for label in lots_of_data:
        data = lots_of_data[label]
        data_keys = data.keys()
        data_keys.sort()
        dates = [pylab.date2num(date) for date in data_keys]
        values = [data[date] for date in data_keys]

        # Calculate date delta to decide if later on we'll be in
        # months mode or years mode
        start_date = data_keys[0]
        end_date   = data_keys[-1]
        graph_this_data.append( (dates, values, label) )

    # re-order the lines
    def plot_cmp(a, b):
        a_values = a[1]
        last_a_value = a_values[-1]
        b_values = b[1]
        last_b_value = b_values[-1]
        return cmp(last_b_value, last_a_value)
    graph_this_data.sort(plot_cmp)

    labels = []
    for elt in graph_this_data:
        dates, values, label = elt
        pylab.plot_date(dates, values, colors.next() + '-')
        labels.append(label)
    pylab.legend(labels)

    # There is room for 15 month labels
    # Anything more and it's too squished
    # Meanwhile, want the month labels to happen on some factor of 12
    # So let's calculate the smallest factor of 12 we can do this for

    if lots_of_data:
        monthcount = find_month_count_that_fits(start_date, end_date, max_ticks=15)
    # ASKMIKE?

    rule = matplotlib.dates.rrulewrapper(matplotlib.dates.MONTHLY, interval=3)
    loc = matplotlib.dates.RRuleLocator(rule)
    formatter = matplotlib.dates.DateFormatter('%m/%y')

    # format the ticks
    ax.xaxis.set_major_locator(loc)
    ax.xaxis.set_major_formatter(formatter)
    if lots_of_data:
        ax.autoscale_view()

    # And shrink the text!
    locs, labels = pylab.xticks()
    pylab.setp(labels, fontsize=8)

    ax.format_xdata = DateFormatter('%Y-%m-%d')
    ax.format_ydata = lambda f: f
    pylab.title(title)
    pylab.grid(True)
    pylab.savefig(fname(title))
    pylab.close()
    return title

def property_counts(things):
    ''' Input: A subset of everything.
    Output: A hash of prop -> count, plus an extra "total"->total'''
    ret = {}
    for thing in things:
        props = urlParse(thing.license_uri)['attribs']
        for prop in props:
            ret[prop] = ret.get(prop, 0) + thing.count
        if props:
            ret['total'] = ret.get('total',0) + thing.count
            # Only bump total if there were really properties
    return ret

def license_counts(things):
    ''' FIXME: Poorly-named.
    Input: A subset of everything.
    Output: A hash of e.g. "by-sa" -> count, plus an extra "total" -> total'''
    ret = {}
    for thing in things:
        which = urlParse(thing.license_uri)['which']
        attribs = urlParse(thing.license_uri)['attribs']
        if attribs or (which == 'pd'):
            ret[which] = ret.get(which, 0) + thing.count
            ret['total'] = ret.get('total',0) + thing.count
    return ret

def get_all_most_recent(table, engine):
    recent_stamp = sqlalchemy.select([sqlalchemy.func.max(table.c.timestamp)], table.c.timestamp < MAX_DATE).execute().fetchone()[0]
    recent = sqlalchemy.select(table.columns, sqlalchemy.and_(table.c.timestamp == recent_stamp, table.c.search_engine == engine)).execute()
    return recent

def for_search_engine(chart_fn, data_fn, table):
    ret = []
    for engine in search_engines:
        data = data_fn(table, engine)
        ret.append(chart_fn(data, engine))
    return ret

def flatten_small_percents(data, percent_floor):
    ''' Input: a dict that maps keys to number values.
    Output: A dict that has most of the same keys, but combines keys whose percent < percent_floor '''
    # Now flatten out everything < 0.5%
    ret = {}
    ret.update(data) # work on a copy!
    total = sum([ret[k] for k in ret])
    for k in ret.keys():
        if ret[k] <  (0.01 * percent_floor * total):
            ret['Other'] = ret.get('Other', 0) + data[k]
            del ret[k]
    return ret

def percentage_ify(fn, things):
    counts = fn(things)
    if not counts:
        return counts
    # Now flatten into percents
    for thing in counts.keys():
        if thing != 'total':
            # into percent:
            if counts['total'] == 0:
                ratio = 0
            else:
                ratio = counts[thing] / (1.0 * counts['total'])
            counts[thing] = 100.0 * ratio
                
    del counts['total']
    return counts    

def jurisdiction_pie_chart():
    def data_fn(table, engine):
        recent = get_all_most_recent(table, engine)
        # Okay, now gather the data.
        data = {}
        for event in recent:
            jurisdiction = urlParse(event.license_uri)['jurisdiction']
            if jurisdiction:
                data[jurisdiction] = data.get(jurisdiction, 0) + event.count
        data = flatten_small_percents(data, percent_floor=0.5)
        return data
    def chart_fn(data, engine):
        return pie_chart(data, "%s Jurisdiction data" % engine)

    return for_search_engine(chart_fn, data_fn, db.simple)

def exact_license_pie_chart():
    def data_fn(table, engine):
        recent = get_all_most_recent(table, engine)
        percents = percentage_ify(license_counts, recent)
        better = flatten_small_percents(percents, percent_floor=0.2)
        return better
    def chart_fn(data, engine):
        return pie_chart(data, "%s exact license distribution" % engine)
    return for_search_engine(chart_fn, data_fn, db.simple)

def simple_aggregate_date_chart():
    def data_fn(table, engine):
        return {'Total linkbacks': date_chart_data(engine, table)}
    def chart_fn(data, engine):
        return date_chart(data, "%s total linkbacks line graph" % engine)
    return for_search_engine(chart_fn, data_fn, db.simple)

def data2htmltable(data, formatstring = '%1.1f%%'):
    ''' Input: data is a mapping from license identifiers to
    (percent, jurisdiction) pairs.
    Output: HTML. '''
    licenses = data.keys()
    licenses.sort() # 'by' first, etc.
    ret = '' # FIXME: Evil HTML creation
    for l in licenses:
        ret += '<table border=1 style="float: left;">'
        ret += '<caption>%s</caption>' % l
        for percent, jurisdiction in data[l]:
            ret += ('<tr><td>%s</td><td>' + formatstring + '</td></tr>') % (jurisdiction, percent)
        ret += '</table>'
    return ret

def data_for_tables_at_bottom(table, engine):
    recent = get_all_most_recent(table, engine).fetchall() # Memory-stealing hack
    # Going to implement this the slow way
    # because our database is too dumb

    # Get all known jurisdictions
    all_jurisdictions = get_all_urlParse_results('jurisdiction', recent)

    data = {}
    for jur in all_jurisdictions:
        just_jur = [k for k in recent if urlParse(k.license_uri)['jurisdiction'] == jur]
        jur_percents = percentage_ify(license_counts, just_jur)
        data[jur] = jur_percents

    # Now we turn the data inside-out
    ret = {} # A map from "by-nd" to [(86.7, 'Generic'), (94.2, 'kr'), ...]
    for jur in data:
        for license_tag in data[jur]:
            percent = data[jur][license_tag]
            pair = (percent, jur)
            if license_tag in ret:
                ret[license_tag].append(pair)
            else:
                ret[license_tag] = [pair]

    # Now sort this mess
    for license_tag in ret:
        ret[license_tag].sort()
        ret[license_tag].reverse()
    return ret
    
def property_bar_chart():
    def data_fn(table, engine):
        recent = get_all_most_recent(table, engine)
        return percentage_ify(property_counts, recent)
    
    def chart_fn(data, engine):
        return bar_chart(data, "%s property bar chart" % engine, 'Percent of total','%1.1f%%')
    return for_search_engine(chart_fn, data_fn, db.simple)

def main(y, m, d):
    ''' Current goal: Emulate existing stats pages.
    Takes the arguments y, m, d and representing the year/month/day of the last day
    whose data to consider.'''
    # For max_date handling, for now: set a global variable to its value
    # and mention it in all our queries
    global MAX_DATE
    MAX_DATE = datetime.datetime(y,m,d) + datetime.timedelta(days=1)
    filenames = []
    # First, generate all the graphs
    filenames.extend(simple_aggregate_date_chart())
    filenames.extend(specific_license_date_chart())
    filenames.extend(exact_license_pie_chart())
    filenames.extend(property_bar_chart())
    filenames.extend(jurisdiction_pie_chart())
    filenames.extend(license_versions_date_chart())
    # Now make a trivial HTML page
    filenames.sort()
    html = '<html><body>'
    for f in filenames:
        html += '<img src="%s.png" /><br />' % f
    html += data2htmltable(data_for_tables_at_bottom(db.simple, 'Yahoo'))
    
    html += '</body></html>'
    fd = open(os.path.join(BASEDIR, 'index.html'), 'w')
    fd.write(html)
    fd.close()

def aggregate_for_date_chart(table, engine, fn):
    ''' Input: table and engine, plus a fn for determing keys
    Output: {fn-return-val1: {date: val, date:val, ...} '''
    # It is impossible to implement this fully cleanly because
    # the license tag data we want is not available in the database. :-(
    query = sqlalchemy.select([sqlalchemy.func.sum(table.c.count), table.c.timestamp, table.c.license_uri], sqlalchemy.and_(table.c.search_engine == engine, table.c.timestamp < MAX_DATE))
    query.group_by(table.c.license_uri)
    query.group_by(table.c.timestamp)
    data = {} # a mapping of 'by' -> {date: num, date: num, ...}
    for datum in query.execute():
        name = fn(datum)
        if name:
            if name not in data:
                data[name] = {}
            data[name][datum.timestamp] = data[name].get(datum.timestamp, 0) + int(datum[0])
    return data

# FIXME: Jurisdictions by log over time

def license_versions_date_chart():
    # FIXME: Make that percentage
    def data_fn(table, engine):
        def fn(datum):
            v = urlParse(datum.license_uri)['version']
            if v:
                return v
            return None # fall-through for explicitness' sake
        return aggregate_for_date_chart(table, engine, fn)
    def chart_fn(data, engine):
        return date_chart(data, "%s linkbacks per license version" % engine)
    return for_search_engine(chart_fn, data_fn, db.simple)

def specific_license_date_chart():
    def data_fn(table, engine):
        def fn(datum):
            attribs = urlParse(datum.license_uri)['attribs']
            which = urlParse(datum.license_uri)['which']
            if attribs or (which == 'pd'):
                return which
            return None # fall-through for explicitness
        return aggregate_for_date_chart(table, engine, fn)
    def chart_fn(data, engine):
        return date_chart(data, "%s linkbacks per license" % engine)
    return for_search_engine(chart_fn, data_fn, db.simple)

if __name__ == '__main__':
    import sys
    if len(sys.argv) < 2:
        print >> sys.stderr, "You must pass an ISO date to this program."
        print >> sys.stderr, "Only events from on or before this date will be considered in the data analysis."
        print >> sys.stderr, "This allows you to re-run the chart generation and be sure of what data will be included."
        sys.exist(-1) # "No typo." ;-)
    max_date = sys.argv[1]
    y,m,d = map(int, max_date.split('-'))
    main(y,m,d)
    
# FIXME: x1e+7 is what?
# Scale actual data down; print at top, "in millions"

# FIXME: These h <-- !??!
