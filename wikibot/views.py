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
LINKLIST_TEMPLATE = 'simplelinklist.wiki'

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


class View(object):
    """
    The methods in the view are generators yielding pages.

    >>> view = View()
    >>> page = view.stats_world().next()
    >>> page.title
    'World'
    """
    def __init__(self):
        data = linkback_reader.most_recent()
        self.query = ccquery.CCQuery()
        self.query.add_linkbacks(data)
        self.render = PageRender()
        return

    def _stats(self, title, data, template = STATS_TEMPLATE):
        stat = ccquery.Stats(data)
        page = self.render(title, template, 
                licenses = stat.VALID_LICENSES,
                count = stat.count,
                percent = stat.percent,
                total = stat.total,
                freedom_score = stat.freedom_score,
                )
        return page

    def all_pages(self):
        all = itertools.chain(
                self.stats_world(),
                self.stats_juris(),
                self.stats_continent(),
                self.list_juris(),
                self.list_continents(),
                )
        return all

    def stats_world(self):
        yield self._stats("World", self.query.license_world())
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
    test()
