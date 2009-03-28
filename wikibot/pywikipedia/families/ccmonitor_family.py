# -*- coding: utf-8  -*-

__version__ = '$Id: commons_family.py 6308 2009-01-28 18:28:30Z russblau $'

import family

class Family(family.Family):
    def __init__(self):
        family.Family.__init__(self)
        self.name = 'ccmonitor'
        self.langs = {
            'en': 'monitor.creativecommons.org',
        }

    def version(self, code):
        return '1.10'

    def scriptpath(self, code):
        return ''
