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

def pie_chart(data, title):
    # make a square figure and axes
    pylab.figure(1, figsize=(8,8))
    
    labels = data.keys()
    fracs = [data[k] for k in labels]
    
    explode=[0.05 for k in labels]
    pylab.pie(fracs, explode=explode, colors=all_html_colors, labels=labels, autopct='%1.1f%%', shadow=True)
    pylab.legend()
    leg = pylab.gca().get_legend()
    ltext  = leg.get_texts()
    pylab.setp(ltext, fontsize='small') 
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

