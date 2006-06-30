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
 
db = SqlSoup('mysql://root:@localhost/cc')

everything = db.simple.select(db.simple.c.timestamp != None)
search_engines = ['Google', 'All The Web', 'Yahoo']
all_html_colors = [k.lower() for k in ['AliceBlue', 'AntiqueWhite', 'Aqua', 'Aquamarine', 'Azure', 'Beige', 'Bisque', 'Black', 'BlanchedAlmond', 'Blue', 'BlueViolet', 'Brown', 'BurlyWood', 'CadetBlue', 'Chartreuse', 'Chocolate', 'Coral', 'CornflowerBlue', 'Cornsilk', 'Crimson', 'Cyan', 'DarkBlue', 'DarkCyan', 'DarkGoldenRod', 'DarkGray', 'DarkGreen', 'DarkKhaki', 'DarkMagenta', 'DarkOliveGreen', 'Darkorange', 'DarkOrchid', 'DarkRed', 'DarkSalmon', 'DarkSeaGreen', 'DarkSlateBlue', 'DarkSlateGray', 'DarkTurquoise', 'DarkViolet', 'DeepPink', 'DeepSkyBlue', 'DimGray', 'DodgerBlue', 'Feldspar', 'FireBrick', 'FloralWhite', 'ForestGreen', 'Fuchsia', 'Gainsboro', 'GhostWhite', 'Gold', 'GoldenRod', 'Gray', 'Green', 'GreenYellow', 'HoneyDew', 'HotPink', 'IndianRed', 'Indigo', 'Ivory', 'Khaki', 'Lavender', 'LavenderBlush', 'LawnGreen', 'LemonChiffon', 'LightBlue', 'LightCoral', 'LightCyan', 'LightGoldenRodYellow', 'LightGrey', 'LightGreen', 'LightPink', 'LightSalmon', 'LightSeaGreen', 'LightSkyBlue', 'LightSlateBlue', 'LightSlateGray', 'LightSteelBlue', 'LightYellow', 'Lime', 'LimeGreen', 'Linen', 'Magenta', 'Maroon', 'MediumAquaMarine', 'MediumBlue', 'MediumOrchid', 'MediumPurple', 'MediumSeaGreen', 'MediumSlateBlue', 'MediumSpringGreen', 'MediumTurquoise', 'MediumVioletRed', 'MidnightBlue', 'MintCream', 'MistyRose', 'Moccasin', 'NavajoWhite', 'Navy', 'OldLace', 'Olive', 'OliveDrab', 'Orange', 'OrangeRed', 'Orchid', 'PaleGoldenRod', 'PaleGreen', 'PaleTurquoise', 'PaleVioletRed', 'PapayaWhip', 'PeachPuff', 'Peru', 'Pink', 'Plum', 'PowderBlue', 'Purple', 'Red', 'RosyBrown', 'RoyalBlue', 'SaddleBrown', 'Salmon', 'SandyBrown', 'SeaGreen', 'SeaShell', 'Sienna', 'Silver', 'SkyBlue', 'SlateBlue', 'SlateGray', 'Snow', 'SpringGreen', 'SteelBlue', 'Tan', 'Teal', 'Thistle', 'Tomato', 'Turquoise', 'Violet', 'VioletRed', 'Wheat', 'White', 'WhiteSmoke', 'Yellow', 'YellowGreen']]

# Thanks, Will.
# Needs tests.
def urlParse(url):
    #print 'in urlParse()'
    jurisdiction=''
    elements=url.split('/')
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
    #print 'out urlParse()'
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
    ret = {'which': which, 'version': version, 'jurisdiction': jurisdiction, 'attribs': tuple(attribs)}
    return ret

def get_all_urlParse_results(key):
    ''' Neat for testing! '''
    ret = set()
    for r in [urlParse(k.license_uri)[key] for k in everything]:
        ret.add(r)
    return ret

def pie_chart(data, title):
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

def property_pie_chart():
    for engine in search_engines:
        just_us = [k for k in everything if k.search_engine == engine]
        if not just_us:
            print 'Hmm, nothing for', engine
        else:
            recent_stamp = max([k.timestamp for k in just_us])
            recent = [k for k in just_us if k.timestamp == recent_stamp ]

            data = {}
            for event in recent:
                properties = urlParse(event.license_uri)['attribs'].split('-')
                if 'by' in properties or 'nc' in properties or 'nd' in properties or 'sa' in properties:
                    for prop in properties:
                        data[prop] = data.get(prop, 0) + event.count
            # Kay, now graph it.
            pie_chart(data, title="Pie chart of properties from " + engine)

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
                jurisdiction = urlParse(event.license_uri)['jurisdiction']
                data[jurisdiction] = data.get(jurisdiction, 0) + event.count
                print 'added', event.count, 'to', jurisdiction
            pie_chart(data, title=engine)

if __name__ == '__main__':
    jurisdiction_data()

