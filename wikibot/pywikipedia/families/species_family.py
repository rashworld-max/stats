# -*- coding: utf-8  -*-

__version__ = '$Id: species_family.py 5089 2008-02-27 20:26:53Z rotem $'

import family

# The wikispecies family

class Family(family.Family):
    def __init__(self):
        family.Family.__init__(self)
        self.name = 'species'
        self.langs = {
            'species': 'species.wikimedia.org',
        }

        self.namespaces[4] = {
            '_default': [u'Wikispecies', self.namespaces[4]['_default']],
        }
        self.namespaces[5] = {
            '_default': [u'Wikispecies talk', self.namespaces[5]['_default']],
        }

        self.interwiki_forward = 'wikipedia'

    def version(self,code):
        return '1.13alpha'

    def shared_image_repository(self, code):
        return ('commons', 'commons')
