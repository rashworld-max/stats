## CONFIGURATION
_BASEDIR='/home/paulproteus/public_html/tmp/charts/'
DB = 'mysql://stats:ioP1gae8@localhost/stats'

## CODE 
from sets import Set as set
import pdb
try:
    import psyco
except ImportError:
    pass
import pylab
import math
from matplotlib.dates import YearLocator, MonthLocator, DateFormatter
from matplotlib.dates import MONDAY, SATURDAY
import datetime
from sqlalchemy.ext.sqlsoup import SqlSoup
import sqlalchemy
assert sqlalchemy.__version__.startswith('0.3')
import os
import matplotlib
import HTMLgen
import sys
from collections import defaultdict
# Jurisdictions
# for search_engine in 'Yahoo', 'Google', 'All The Web':
# select from simple where search_engine=search_engine
# and language=NULL and country=NULL

def split(dates, data):
    ret = [] # return a list of listss
    currentdates = []
    assert(len(dates) == len(data))
    last = None
    for k in range(len(dates)):
            thisdate = dates[k]
            if currentdates:
                last = currentdates[-1]
            else:
                last = thisdate
            if abs(thisdate - last) > 3:
                    if currentdates:
                            ret.append( (currentdates, [data.pop(0) for k in currentdates] ) )
                            currentdates = [thisdate]
            else:
                    currentdates.append(thisdate)
    if currentdates:
            ret.append( (currentdates, [data.pop(0) for k in currentdates]))
    return ret


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

# FIXME: Write a date_chart that shows total Google's or() of all the CC attributes

_PROCESSING_MAX_DATE = datetime.datetime(3000, 1, 1) # In the grim future of humanity
                                         # there are only license
                                         # usage statistics
db = SqlSoup(DB)
JURI = None

class ListCycle:
    ''' Takes a list l and, on calling next(), keeps cycling
    through its contents, starting with the first element.
    Goes on forever and never overflows.'''
    def __init__(self, l):
        self.l = l
        self.index = 0
    def next(self):
        if self.index >= len(self.l):
            self.index = -1
        ret = self.l[self.index]
        self.index += 1
        return ret

REPORT_DATE=''
def fname(s):
    assert(REPORT_DATE)
    #print REPORT_DATE, 'is report date'
    assert('/' not in REPORT_DATE)
    if JURI is None:
        juri_dirpart = 'all'
    else:
        juri_dirpart = JURI
    dirpart = os.path.join(_BASEDIR, REPORT_DATE, juri_dirpart)
    if not os.path.isdir(dirpart):
        os.makedirs(dirpart, mode=0755)
        # If that failed, let the exception blow up the whole program.
    print dirpart
    return os.path.join(dirpart, s)

search_engines = ['Google', 'All The Web', 'Yahoo', 'MSN']
all_html_colors = [k.lower() for k in ['AliceBlue', 'AntiqueWhite', 'Aqua', 'Aquamarine', 'Azure', 'Beige', 'Bisque', 'Black', 'BlanchedAlmond', 'Blue', 'BlueViolet', 'Brown', 'BurlyWood', 'CadetBlue', 'Chartreuse', 'Chocolate', 'Coral', 'CornflowerBlue', 'Cornsilk', 'Crimson', 'Cyan', 'DarkBlue', 'DarkCyan', 'DarkGoldenRod', 'DarkGray', 'DarkGreen', 'DarkKhaki', 'DarkMagenta', 'DarkOliveGreen', 'Darkorange', 'DarkOrchid', 'DarkRed', 'DarkSalmon', 'DarkSeaGreen', 'DarkSlateBlue', 'DarkSlateGray', 'DarkTurquoise', 'DarkViolet', 'DeepPink', 'DeepSkyBlue', 'DimGray', 'DodgerBlue', 'Feldspar', 'FireBrick', 'FloralWhite', 'ForestGreen', 'Fuchsia', 'Gainsboro', 'GhostWhite', 'Gold', 'GoldenRod', 'Gray', 'Green', 'GreenYellow', 'HoneyDew', 'HotPink', 'IndianRed', 'Indigo', 'Ivory', 'Khaki', 'Lavender', 'LavenderBlush', 'LawnGreen', 'LemonChiffon', 'LightBlue', 'LightCoral', 'LightCyan', 'LightGoldenRodYellow', 'LightGrey', 'LightGreen', 'LightPink', 'LightSalmon', 'LightSeaGreen', 'LightSkyBlue', 'LightSlateBlue', 'LightSlateGray', 'LightSteelBlue', 'LightYellow', 'Lime', 'LimeGreen', 'Linen', 'Magenta', 'Maroon', 'MediumAquaMarine', 'MediumBlue', 'MediumOrchid', 'MediumPurple', 'MediumSeaGreen', 'MediumSlateBlue', 'MediumSpringGreen', 'MediumTurquoise', 'MediumVioletRed', 'MidnightBlue', 'MintCream', 'MistyRose', 'Moccasin', 'NavajoWhite', 'Navy', 'OldLace', 'Olive', 'OliveDrab', 'Orange', 'OrangeRed', 'Orchid', 'PaleGoldenRod', 'PaleGreen', 'PaleTurquoise', 'PaleVioletRed', 'PapayaWhip', 'PeachPuff', 'Peru', 'Pink', 'Plum', 'PowderBlue', 'Purple', 'Red', 'RosyBrown', 'RoyalBlue', 'SaddleBrown', 'Salmon', 'SandyBrown', 'SeaGreen', 'SeaShell', 'Sienna', 'Silver', 'SkyBlue', 'SlateBlue', 'SlateGray', 'Snow', 'SpringGreen', 'SteelBlue', 'Tan', 'Teal', 'Thistle', 'Tomato', 'Turquoise', 'Violet', 'VioletRed', 'Wheat', 'White', 'WhiteSmoke', 'Yellow', 'YellowGreen']]

# Thanks, Will.
# Needs tests.
urlParse_cache = {}
def urlParse(url):
    ''' Input: http://creativecommons.org/some/license/URI/
    Output: A dict with keys (which, version, jurisdiction, attribs)
    of types (str, str, str, tuple)'''
    # Note: ret['attribs'] is empty for a public domain dedication.
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
        # attribs: if it's a "normal" CC license, then the list of CC attributes
        if which in ('GPL', 'LGPL', 'devnations', 'sampling', 'pd', 'zero'):
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
    ''' Pass me an iterable of everything and I return to you
    a set of all urlParse(k)[key] for k in everything'''
    ret = set()
    for r in [urlParse(k.license_uri)[key] for k in everything]:
        ret.add(r)
    return ret

def bar_chart(data, title,ylabel='',labelfmt='%1.1f'):
    ''' Input: a dict that maps bar labels to values and a title for the chart.
    Output: relative path to a PNG bar chart.  ylabel controls the y axis
    lablel. It labels the bars with the values, by default a percent.'''
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
    short_fname = title + '.png'
    
    pylab.savefig(fname(short_fname),dpi=100)
    pylab.close()
    
    # http://matplotlib.sourceforge.net/screenshots/barchart_demo.py shows how to smarten the legend
    return short_fname

def pie_chart(data, title):
    ''' Input: A dict that maps labels to values; a title for the pie.
    Output: A relative path to a PNG that is the rendered pie chart. '''
    # make a square figure and axes
    pylab.figure(figsize=(8,8))

    labels = sorted_dict_keys_by_value(data)
    fracs = [ data[label] for label in labels ]
    
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
    short_fname = title + '.png'
    pylab.savefig(fname(short_fname),dpi=100)
    pylab.close() # This is key!
    return short_fname

def date_chart_data(engine, table):
    ''' Input: a search engine and a SQLAlchemy table.
    Output: {date1: sum of allowed (based on _PROCESSING_MAX_DATE and JURI) data from table on date1, date2: same for date2, ...}'''
    restrictions = sqlalchemy.and_(table.c.search_engine == engine, table.c.timestamp < _PROCESSING_MAX_DATE)
    s = sqlalchemy.select([sqlalchemy.func.sum(table.c.count), table.c.timestamp, table.c.license_uri], restrictions)
    s.group_by(table.c.timestamp)
    data = s.execute() # sum() returns a string, BEWARE!

    send_this = {}
    for datum in data:
        if JURI:
            juri = urlParse(datum.license_uri)['jurisdiction']
            if juri != JURI:
                continue
        value, timestamp, jurisdiction = datum
        value = int(value) # sqlalchemy bug: SUM() returns a string
        send_this[timestamp] = value
    return send_this

def find_month_count_that_fits(start_date, end_date, max_ticks):
    ''' Returns the smallest nice-looking number of months that lets you have
    at most max_ticks ticks on a graph axis betweeen start_date and end_date.'''
    factors = (1, 2, 3, 4, 6, 12, 23, 36, 48) # That should cover us

    for factor in factors:
        delta = datetime.timedelta(days=(factor*30)) # HACK!  Not correct. :-)
        dates = matplotlib.dates.drange(start_date, end_date, delta)
        if len(dates) <= max_ticks:
            return factor
    raise AssertionError, "Really?  Gawrsh!"

def clean_dict(d):
    ''' WARNING: Only call this before graphing data.  It is evil to corrupt data
    in a context other than displaying it.
    It removes keys from d where the value is false (0, None, etc.).'''
    ret = {}
    for key in d:
        if d[key]:
            ret[key] = d[key]
    return ret

class FileAndHtml:
    file = ''
    html = ''
    def __init__(self, f, h):
        self.file = f
        self.html = h
    def __cmp__(self, other):
        return cmp(self.file, other.file)

def show_png_chart(path):
    html = '' # Sorry for spewing out a string
    img = HTMLgen.Image(filename=fname(path), src=path, alt=path)
    # Why does HTMLgen not pick up on the metadata (width, height)?
    html += str(img)
    html += str(HTMLgen.BR())
    return FileAndHtml(f=path, h=html)

def date_chart(lots_of_data, title, scaledown = 1):
    ''' Input: Some data, a title, and a percentage by which we scale down the data.
    Output: The relative path to a PNG I created. '''
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
        data_keys = sorted_dict_keys(data)
        dates = [pylab.date2num(date) for date in data_keys]
        values = [data[date] / (scaledown * 1.0) for date in data_keys]

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
        splitted = split(dates, values)
        mycolor = colors.next()
        for splitteddates, splittedvalues in splitted:
            pylab.plot_date(splitteddates, splittedvalues, mycolor + '-')
        labels.append(label)
    pylab.legend(labels, loc='upper left')

    # There is room for 15 month labels
    # Anything more and it's too squished
    # Meanwhile, want the month labels to happen on some factor of 12
    # So let's calculate the smallest factor of 12 we can do this for

    if lots_of_data:
        monthcount = find_month_count_that_fits(start_date, end_date, max_ticks=15)
    # FIXME: See top of function.

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
    short_fname = title + '.png'
    pylab.savefig(fname(short_fname),dpi=100)
    pylab.close()
    return short_fname

def make_total(d):
    ret = {}
    so_far = 0
    for k in d:
        ret[k] = d[k]
        so_far += d[k]
    ret['total'] = so_far
    return ret

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

def most_common_entry(iterable):
    '''Input: Iterable of things
    Output: Most frequent one, breaking ties randomly (!)

    >>> most_common_entry([1,2,2,3])
    2
    >>> most_common_entry([])
    >>>
    '''
    entry2count = defaultdict(int)
    for entry in iterable:
        entry2count[entry] += 1
    if not entry2count:
        return None
    count, winner = max([ (entry2count[item], item) for item in entry2count])
    return winner

def license_counts(things):
    ''' Input: A subset of everything.
    Output: A hash of e.g. "by-sa" -> count, plus an extra "total" -> total'''
    ret = {}
    for thing in things:
        which = urlParse(thing.license_uri)['which']
        attribs = urlParse(thing.license_uri)['attribs']
        if attribs or (which == 'pd'):
            ret[which] = ret.get(which, 0) + thing.count
            ret['total'] = ret.get('total',0) + thing.count
    return ret

def get_all_most_recent(table, engine, debug = False, recent_stamp = None):
    '''Input: a table object, a search engine, and a debug boolean that decides if
    to print tracing information about this process. If recent_stamp is provided
    and not None, then we search for a crawl that took place *on that date*,
    returning the empty list if we don't find one.
    Output: A list (?) of SQL objects.'''
    if recent_stamp is None:
        # if recent_stamp is None, just grab the most recent one:
        recent_stamp = sqlalchemy.select([sqlalchemy.func.max(table.c.timestamp)], table.c.timestamp < _PROCESSING_MAX_DATE).execute().fetchone()[0]
    else:
        # look for a timestamp that share day, month, year with recent_stamp
        # if there is more than one, break the tie by FIXME
        start_of_day = datetime.datetime(year=recent_stamp.year,
                                         month=recent_stamp.month,
                                         day=recent_stamp.day,
                                         hour=0, minute=0, second=0)
        end_of_day = datetime.datetime(year=recent_stamp.year,
                                       month=recent_stamp.month,
                                       day=recent_stamp.day,
                                       hour=23, minute=59, second=59)
        possible_recent_stamps_q = sqlalchemy.select([table.c.timestamp], sqlalchemy.and_(
                table.c.timestamp < end_of_day, table.c.timestamp > start_of_day))
        possible_recent_stamps = [k[0] for k in possible_recent_stamps_q.execute()]
        # If there are none, just bail out.
        if not possible_recent_stamps:
            raise StopIteration
        else:
            # pick the winner: the one with the most entries...
            recent_stamp = most_common_entry(possible_recent_stamps)
    if debug:
        print recent_stamp
    recent = sqlalchemy.select(table.c.keys(), sqlalchemy.and_(table.c.timestamp == recent_stamp, table.c.search_engine == engine)).execute()
    for datum in recent:
        if JURI:
            juri = urlParse(datum.license_uri)['jurisdiction']
            if juri != JURI:
                continue
        yield datum

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
        return data
    def chart_fn(data, engine):
        crushed = flatten_small_percents(data, percent_floor=0.5)
        pic = pie_chart(crushed, "%s Jurisdiction data" % engine)
        html = pic_and_data(pic, data, fmtstr = "%1.1f")
        ret = FileAndHtml(f=pic, h=str(html))
        return ret

    return for_search_engine(chart_fn, data_fn, db.simple)

def sorted_dict_keys(d):
    keys = d.keys()
    keys.sort()
    return keys

def sorted_dict_keys_by_value(d):
    all = [ (d[key], key) for key in d ]
    all.sort()
    return [ key for val,key in all ]

def pic_and_data(pic, data, fmtstr = "%s"):
    intab = HTMLgen.Table()
    intab.body = []
    for key in sorted_dict_keys_by_value(data):
        intab.body.append( map(HTMLgen.Text, [key, fmtstr % data[key]]) )
    intab.body.reverse() # since sorted comes out little to big
    img = HTMLgen.Image(filename=fname(pic), src=pic, alt=pic)

    # a table of one row, two columns
    # second column is (egad) a table
    outtab = HTMLgen.Table()
    outtab.body = [ [img, intab] ]
    return outtab

def exact_license_pie_chart():
    def data_fn(table, engine):
        recent = get_all_most_recent(table, engine)
        percents = percentage_ify(license_counts, recent)
        return percents
    def chart_fn(data, engine):
        crushed = flatten_small_percents(data, percent_floor=0.2)
        pic = pie_chart(crushed, "%s exact license distribution" % engine)
        html = pic_and_data(pic, data, fmtstr = "%1.1f")
        ret = FileAndHtml(f=pic, h=html)
        return ret
    return for_search_engine(chart_fn, data_fn, db.simple)

def simple_aggregate_date_chart():
    def data_fn(table, engine):
        return {'Total linkbacks': date_chart_data(engine, table)}
    def chart_fn(data, engine):
        return date_chart(data, "%s total linkbacks line graph in millions" % engine,
                          scaledown=1000*1000)
    return for_search_engine(chart_fn, data_fn, db.simple)

def data2htmltable(data, formatstring = '%1.1f%%'):
    ''' Input: data is a mapping from license identifiers to
    (percent, jurisdiction) pairs.
    Output: HTML. '''
    ret = '' # HTML as strings because HTMLgen.Table doesn't support style=
    for l in sorted_dict_keys(data):
        ret += '<table border=1 style="float: left;">'
        ret += '<caption>%s</caption>' % l
        for percent, jurisdiction in data[l]:
            ret += ('<tr><td>%s</td><td>' + formatstring + '</td></tr>') % (jurisdiction, percent)
        ret += '</table>'
    return ret

def data_for_tables_at_bottom(table, engine):
    recent = get_all_most_recent(table, engine) # Memory-stealing hack
    # Going to implement this the slow way
    # because our database is too dumb

    # Get all known jurisdictions
    all_jurisdictions = get_all_urlParse_results('jurisdiction', recent)

    data = {}
    recent = get_all_most_recent(table, engine) # Have to re-create generator
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

def generate_charts(y, m, d, jurismode = False, juri = None):
    ''' Current goal: Emulate existing stats pages.
    Takes the arguments y, m, d and representing the year/month/day of the last day
    whose data to consider.'''
    # For _PROCESSING_MAX_DATE handling, for now: set a global variable to its value
    # and mention it in all our queries
    global _PROCESSING_MAX_DATE
    _PROCESSING_MAX_DATE = datetime.datetime(y,m,d) + datetime.timedelta(days=1)
    charts = [] # a list of tuples: (chart name, HTML for it)
    # First, generate all the graphs
    charts.extend(map(show_png_chart, simple_aggregate_date_chart()))
    charts.extend(map(show_png_chart, specific_license_date_chart()))
    charts.extend(exact_license_pie_chart())
    charts.extend(map(show_png_chart, property_bar_chart()))
    if jurismode:
        charts.extend(jurisdiction_pie_chart())
        charts.extend(map(show_png_chart, jurisdiction_log_date_chart()))
    charts.extend(map(show_png_chart, license_versions_percentage_date_chart()))
    # Now make a trivial HTML page
    charts.sort()
    doc = HTMLgen.SimpleDocument()
    for chart in charts:
        doc.append(chart.html)
    doc.append(data2htmltable(data_for_tables_at_bottom(db.simple, 'Yahoo')))
    fd = open(fname('index.html'), 'w')
    print >> fd, doc
    fd.close()

def aggregate_for_date_chart(table, engine, fn, logbase=None):
    ''' Input: table and engine, plus a fn for determing keys
    Output: {fn-return-val1: {date: val, date:val, ...} '''
    # It is impossible to implement this fully cleanly because
    # the license tag data we want is not available in the database. :-(
    query = sqlalchemy.select([sqlalchemy.func.sum(table.c.count), table.c.timestamp, table.c.license_uri], sqlalchemy.and_(table.c.search_engine == engine, table.c.timestamp < _PROCESSING_MAX_DATE))
    query.group_by(table.c.license_uri)
    query.group_by(table.c.timestamp)
    data = {} # a mapping of 'by' -> {date: num, date: num, ...}
    for datum in query.execute():
        if JURI:
            juri = urlParse(datum.license_uri)['jurisdiction']
            if juri != JURI:
                continue
        name = fn(datum)
        if name:
            if name not in data:
                data[name] = {}
            data[name][datum.timestamp] = data[name].get(datum.timestamp, 0) + int(datum[0])
    # Optionally handle log:
    if logbase is not None:
        for name in data:
            for timestamp in data[name]:
                val = data[name][timestamp]
                if val == 0:
                    vallog = 0 # Tee-hee, this is a lie.
                else:
                    vallog = math.log(val, logbase)
                data[name][timestamp] = vallog
    return data

def jurisdiction_log_date_chart():
    def data_fn(table, engine):
        def fn(datum):
            jur = urlParse(datum.license_uri)['jurisdiction']
            if jur:
                return jur
            return None # fall-through for explicitness
        return aggregate_for_date_chart(table, engine, fn, logbase=10)
    def chart_fn(data, engine):
        return date_chart(data, "%s jurisdiction count (log10)" % engine)
    return for_search_engine(chart_fn, data_fn, db.simple)


def license_versions_percentage_date_chart():
    def data_fn(table, engine):
        # FYI, this looks totally crazy.  The workings of this will be forgotten by Thursday.
        def fn(datum):
            v = urlParse(datum.license_uri)['version']
            if v:
                return v
            return None # fall-through for explicitness' sake
        raw_data = aggregate_for_date_chart(table, engine, fn)
        license_types = raw_data.keys()
        # let's union the dates up
        bag_of_dates = [raw_data[lic].keys() for lic in license_types]
        dates = set()
        for bag in bag_of_dates:
            dates.update(set(bag))
            
        # Now percentage_ify, but carefully
        percentaged = {}
        for lic in license_types:
            percentaged[lic] = {}
        yesterday_licenses = None
        sorted_dates = list(dates)
        sorted_dates.sort()
        for date in sorted_dates:
            percentages = [ (lic, raw_data[lic].get(date, 0)) for lic in license_types ]
            dictified = dict(percentages)
            percentaged_dict = percentage_ify(make_total, dictified)
            # A heuristic to smooth sloppy data: Throw away a day if there is a license in yesterday but not today
            today_licenses = set([lic for lic in license_types if date in raw_data[lic]]) # YEEK
            if yesterday_licenses is None: # base case
                yesterday_licenses = today_licenses
            if yesterday_licenses.issubset(today_licenses): # then today_licenses is considered useful
                for lic in today_licenses:
                    percentaged[lic][date] = percentaged_dict[lic]
                yesterday_licenses = today_licenses # Store this as a model for future days to live up to
            else:
                print 'threw away', date, 'because', today_licenses, 'not a subset of', yesterday_licenses
        return percentaged
    def chart_fn(data, engine):
        return date_chart(data, "%s license version percentages" % engine)
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
        return date_chart(data, "%s linkbacks per license in millions" % engine,
                          scaledown=1000*1000)
    return for_search_engine(chart_fn, data_fn, db.simple)

def main(max_date,nojuris=False):
    # Step 0: Assert sanity of _BASEDIR
    if not os.path.isdir(_BASEDIR):
        print "%s needs to be a directory that exists.  Good-bye." % _BASEDIR
        sys.exit(-1)
    
    # Step 1: Parse input.
    y,m,d = map(int, max_date.split('-'))
    juris = get_all_urlParse_results('jurisdiction', get_all_most_recent(db.simple, 'Yahoo'))

    # Step 2: Set global config vars to appropriate values
    global REPORT_DATE
    global JURI # but it's here to stay.
    REPORT_DATE=max_date

    # Step 3: Create the directory for this date's report
    empty = fname('')
    if not os.path.isdir(empty):
        os.makedirs(empty, mode=0755)
        
    # Step 4: Figure out which jursdictions to report for
    if nojuris:
        juris = []

    # Step 5: For each jurisdiction, run the report
    for juri in juris:
        if juri:
            JURI = juri
            print 'jurying for', juri
            generate_charts(y,m,d,jurismode=True)

    # Step 6: Always run the empty jurisdiction
    JURI = None
    generate_charts(y,m,d)

if __name__ == '__main__':
    import sys
    nojuris = False
    if len(sys.argv) < 2:
        print >> sys.stderr, "You must pass an ISO date to this program."
        print >> sys.stderr, "Only events from on or before this date will be considered in the data analysis."
        print >> sys.stderr, "This allows you to re-run the chart generation and be sure of what data will be included."
        sys.exit(-1)
    if len(sys.argv) >= 3 and sys.argv[2] == 'nojuris':
        nojuris = True
    max_date = sys.argv[1]
    main(max_date, nojuris)

