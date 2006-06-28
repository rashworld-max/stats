def str2int(s):
    s = s.replace(',', '')
    return int(s)

def atw_count(query):
    PREFIX="http://www.alltheweb.com/search?cat=web&o=0&_sb_lang=any&q=link:"
    result = urllib2.urlopen(PREFIX + query).read()
    bs = BeautifulSoup.BeautifulSoup()
    bs.feed(result)
    for p in bs('p'):
        if ' '.join(p.renderContents().split()) == "No Web pages found that match your query.":
            return 0
        # I guess it's worth looking inside then
    count = re.search(r'<span class="ofSoMany">(.+?)</span>', result).group(1)
    return str2int(count)
