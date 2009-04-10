"""
The view to generate pages than can be put onto wiki.
"""
import itertools
import datetime
import codecs
import jinja2

import linkback_reader
import ccquery

TEMPLATE_DIR = 'template/'
STATS_TEMPLATE = 'stats.wiki'
LINKLIST_TEMPLATE = 'simplelinklist.wiki'
XML_WORLDMAP_FREEDOM = 'worldmap_freedom.xml'
XML_WORLDMAP_TOTAL = 'worldmap_total.xml'

TEMPLATE_USER_WORLD = 'user_world.wiki'
TEMPLATE_USER_REGION = 'user_region.wiki'
TEMPLATE_USER_LIST = 'user_list.wiki'
TEMPLATE_USER_JURIS = 'user_juris.wiki'

TITLE_LIST_JURIS = 'List of Jurisdictions'
TITLE_LIST_REGIONS = 'List of Regions'

BOTPAGE_PREFIX = 'Robot/'
BOTPAGE_STATS = 'Statistics'
BOTPAGE_MAP_FREEDOM = 'Freedom Score Map'
BOTPAGE_MAP_TOTAL = 'Total Number Map'
BOTPAGE_LIST_JURIS = 'List of Jurisdictions'
BOTPAGE_LIST_REGIONS = 'List of Regions'


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

        def _botpage(title):
            return '{{%s%s}}'%(BOTPAGE_PREFIX, title)

        self.env.filters['thousandsep'] = _thousandsep
        self.env.filters['botpage'] = _botpage
        return

    def __call__(self, title, template_fn, **kwargs):
        template = self.env.get_template(template_fn)
        text = template.render(**kwargs)
        text = text.encode('utf-8')
        # Jinja did nothing with DOM, so we remove it manually
        if text.startswith(codecs.BOM_UTF8):
            text = text[len(codecs.BOM_UTF8):]
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

    >>> data = linkback_reader.read_csv('linkbacks-daily-Yahoo.csv')
    >>> view = View.from_data(data)
    >>> page = view.list_juris().next()
    >>> page.title
    'List of Jurisdictions'
    """
    def __init__(self, query):
        self.query = query
        self.render = PageRender()
        self.to_fips = ToFips()
        self._uploaded_url = {}
        return
    
    @classmethod
    def from_data(cls, data):
        query = ccquery.CCQuery()
        query.add_linkbacks(data)
        view = cls(query)
        return view

    @classmethod
    def from_most_recent(cls):
        data = linkback_reader.most_recent()
        view = cls.from_data(data)
        return view

    def _stats(self, name, data, template = STATS_TEMPLATE, **extra_params):
        stat = ccquery.Stats(data)
        title = self._botns(name, BOTPAGE_STATS)
        date = datetime.date.today().strftime("%Y-%m-%d")
        page = self.render(title, template,
                licenses = stat.VALID_LICENSES,
                count = stat.count,
                percent = stat.percent,
                total = stat.total,
                freedom_score = stat.freedom_score,
                date = date,
                **extra_params
                )
        return page

    def _user(self, name, template, **botpages):
        """
        Render user pages and automatically put page arguments into proper namespace.
        """
        for key in botpages:
            botpages[key] = name + '/' + botpages[key]
        page = self.render(name, template, **botpages)
        return page

    def _botns(self, *names):
        name = '/'.join(names)
        return 'Template:%s%s'%(BOTPAGE_PREFIX, name)

    def set_uploaded_url(self, filename, url):
        self._uploaded_url[filename] = url
        return

    def all_pages(self):
        all = itertools.chain(
                self.stats_world(),
                self.stats_juris(),
                self.stats_region(),
                self.list_juris(),
                self.list_regions(),
                )
        return all

    def all_files(self):
        all = itertools.chain(                
                self.map_world(),
                )
        return all

    def all_userpages(self):
        """
        These pages produces an initial value of user content pages.
        """
        all = itertools.chain(
                self.user_world(),
                self.user_region(),
                self.user_juris(),
                self.user_lists(),
                )
        return all

    def user_world(self):
        page = self._user('World', TEMPLATE_USER_WORLD,
                        stats = BOTPAGE_STATS,
                        map_freedom = BOTPAGE_MAP_FREEDOM,
                        map_total = BOTPAGE_MAP_TOTAL
                        )
        yield page
        return

    def user_region(self):
        query = self.query
        for code in query.all_regions():
            name = query.region_code2name(code)
            page = self._user(name, TEMPLATE_USER_REGION,
                                stats = BOTPAGE_STATS,
                                list = BOTPAGE_LIST_JURIS
                                )
            yield page
        return

    def user_juris(self):
        query = self.query
        for code in query.all_juris():
            name = query.juris_code2name(code)
            page = self._user(name, TEMPLATE_USER_JURIS,
                                stats = BOTPAGE_STATS)
            yield page
        return

    def user_lists(self):
        yield self.render(TITLE_LIST_JURIS, TEMPLATE_USER_LIST, list=BOTPAGE_LIST_JURIS)
        yield self.render(TITLE_LIST_REGIONS, TEMPLATE_USER_LIST, list=BOTPAGE_LIST_REGIONS)
        return

    def stats_world(self):
        yield self._stats("World", self.query.license_world())
        yield self.render(self._botns('World', BOTPAGE_MAP_FREEDOM),
                'map.wiki', map_url = self._uploaded_url[XML_WORLDMAP_FREEDOM])
        yield self.render(self._botns('World', BOTPAGE_MAP_TOTAL),
                'map.wiki', map_url = self._uploaded_url[XML_WORLDMAP_TOTAL])
        return

    def stats_juris(self):
        query = self.query
        for code in query.all_juris():
            juris_name = query.juris_code2name(code)
            data = query.license_by_juris(code)
            yield self._stats(juris_name, data)
        return

    def stats_region(self):
        query = self.query
        for code in query.all_regions():
            name = query.region_code2name(code)
            data = query.license_by_region(code)
            juris_list = [query.juris_code2name(c) for c 
                            in query.juris_in_region(code)]
            yield self._stats(name, data)
            yield self.render(self._botns(name, BOTPAGE_LIST_JURIS), 
                                LINKLIST_TEMPLATE, links = juris_list)
        return
    
    def list_juris(self):
        query = self.query
        links = [query.juris_code2name(code) for code in query.all_juris()]
        page = self.render(self._botns(BOTPAGE_LIST_JURIS),
                                LINKLIST_TEMPLATE, links=links)
        yield page
        return

    def list_regions(self):
        query = self.query
        links = [query.region_code2name(code) for code in query.all_regions()]
        page = self.render(self._botns(BOTPAGE_LIST_REGIONS),
                                LINKLIST_TEMPLATE, links=links)
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

        #fix for United Kingdom
        ukdata = itertools.chain(query.license_by_juris('scotland'),
                                 query.license_by_juris('uk'))
        stats['UK'] = ccquery.Stats(ukdata)
        names['UK'] = 'United Kingdom'

        world = ccquery.Stats(query.license_world())

        page = self.render(XML_WORLDMAP_FREEDOM, XML_WORLDMAP_FREEDOM,
                            jurisdictions = stats.keys(),
                            stats = stats,
                            names = names,
                            world = world,
                            )
        yield page
        
        page = self.render(XML_WORLDMAP_TOTAL, XML_WORLDMAP_TOTAL,
                            jurisdictions = stats.keys(),
                            stats = stats,
                            names = names,
                            world = world,
                            )
        yield page

        return

def test_map():
    MAPDIR = 'worldmap/'
    data = linkback_reader.read_csv('linkbacks-daily-Yahoo.csv')
    view = View.from_data(data)
    maps = view.all_files()
    for map in maps:
        fn = MAPDIR + map.title
        open(fn, 'w').write(map.text)
    return   

def test():
    data = linkback_reader.read_csv('linkbacks-daily-Yahoo.csv')
    view = View.from_data(data)
    maps = view.all_files()
    for map in maps:
        view.set_uploaded_url(map.title, 'http://FOO.BAR.org/'+map.title)

    pagegen = itertools.chain(view.all_pages(), view.all_userpages())
    for page in pagegen:
        print '='*50
        print
        print page
        print

    return

if __name__=='__main__':
    #test_map()
    test()
