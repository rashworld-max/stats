"""
The view to generate pages than can be put onto wiki.
"""
import itertools
import jinja2
import locale

import linkback_reader
import ccquery

TEMPLATE_DIR = 'template/'
STATS_TEMPLATE = 'simpletable.wiki'
STATS_WORLD_TEMPLATE = 'world.wiki'
LINKLIST_TEMPLATE = 'simplelinklist.wiki'
WORLDMAP_FREEDOM_TEMPLATE = 'worldmap.xml'

COUNTRY_CODE_DATA = 'country_codes_Jan09.txt'

class Page(object):
    def __init__(self, title, text):
        self.title = title
        self.text = text
        return

    def __repr__(self):
        return "%s\n\n%s"%(self.title, self.text)

class PageRender(object):
    def __init__(self):
        self.env = jinja2.Environment(
                loader=jinja2.FileSystemLoader(TEMPLATE_DIR),
                trim_blocks=True
                )

        # Install a thousand spearator filter.
        def _thousandsep(number):
            number = str(number)
            return number if len(number)<=3 else \
                    _thousandsep(number[:-3]) + ',' + number[-3:]
        self.env.filters['thousandsep'] = _thousandsep

        return

    def __call__(self, title, template_fn, **kwargs):
        template = self.env.get_template(template_fn)
        text = template.render(**kwargs)
        page = Page(title, text)
        return page

class ToFips(object):
    """
    Helper to convert ISO 3166 country code to FIPS country code.
    
    >>> to_fips = ToFips()
    >>> to_fips('cn')
    'CH'
    """
    def __init__(self):
        codedict = {}
        for line in open(COUNTRY_CODE_DATA):
            items = line.split('\t')
            fips = items[1][1:-1].strip()
            iso = items[2][1:-1].strip()
            if not fips or not iso:
                continue

            codedict[iso] = fips
        self.codedict = codedict
        return

    def __call__(self, iso):
        return self.codedict[iso.upper()]

class View(object):
    """
    The methods in the View class are generators yielding pages.

    >>> view = View()
    >>> page = view.stats_world().next()
    >>> page.title
    'World'
    """
    def __init__(self, data=None):
        if data is None:
            data = linkback_reader.most_recent()
        self.query = ccquery.CCQuery()
        self.query.add_linkbacks(data)
        self.render = PageRender()
        self.to_fips = ToFips()
        self._uploaded_url = {}
        return

    def _stats(self, title, data, template = STATS_TEMPLATE, **extra_params):
        stat = ccquery.Stats(data)
        page = self.render(title, template, 
                licenses = stat.VALID_LICENSES,
                count = stat.count,
                percent = stat.percent,
                total = stat.total,
                freedom_score = stat.freedom_score,
                **extra_params
                )
        return page

    def set_uploaded_url(self, filename, url):
        self._uploaded_url[filename] = url
        return

    def all_pages(self):
        all = itertools.chain(
                self.stats_world(),
                self.stats_juris(),
                self.stats_continent(),
                self.list_juris(),
                self.list_continents(),
                )
        return all

    def all_files(self):
        all = itertools.chain(
                self.map_world(),
                )
        return all

    def stats_world(self):
        yield self._stats("World", self.query.license_world(), STATS_WORLD_TEMPLATE,
                            freedom_url = self._uploaded_url['worldmap_freedom.xml']
                    )
        return

    def stats_juris(self):
        query = self.query
        for code in query.all_juris():
            juris_name = query.juris_code2name(code)
            data = query.license_by_juris(code)
            yield self._stats(juris_name, data)
        return

    def stats_continent(self):
        query = self.query
        for code in query.all_continents():
            name = query.continent_code2name(code)
            data = query.license_by_continent(code)
            yield self._stats(name, data)
        return
    
    def list_juris(self):
        query = self.query
        links = [query.juris_code2name(code) for code in query.all_juris()]
        page = self.render("List of Jurisdictions", LINKLIST_TEMPLATE, links=links)
        yield page
        return

    def list_continents(self):
        query = self.query
        links = [query.continent_code2name(code) for code in query.all_continents()]
        page = self.render("List of Continents", LINKLIST_TEMPLATE, links=links)
        yield page
        return

    def map_world(self):
        """
        World map view.
        """
        query = self.query
        stats = {}
        names = {}
        for code in query.all_juris():
            try:
                fips_code = self.to_fips(code)
            except KeyError:
                continue
            data = query.license_by_juris(code)
            stats[fips_code] = ccquery.Stats(data)
            names[fips_code] = query.juris_code2name(code)
        page = self.render("worldmap_freedom.xml", WORLDMAP_FREEDOM_TEMPLATE,
                            jurisdictions = stats.keys(),
                            stats = stats,
                            names = names,
                            )
        yield page
        return

def test_map():
    MAPDIR = 'worldmap/'
    data = linkback_reader.read_csv('linkbacks-daily-Yahoo.csv')
    view = View(data)
    maps = view.all_files()
    for map in maps:
        fn = MAPDIR + map.title
        open(fn, 'w').write(map.text)
    return   

def test():
    view = View()
    pagegen = view.all_pages()
    for page in pagegen:
        print '='*50
        print
        print page
        print

    return

if __name__=='__main__':
    test_map()
    #test()
