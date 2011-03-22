# -*- coding: utf-8 -*-
from test_make_project import TestBase

class TestShabtiMoinMoin(TestBase):
    template='shabti_moinmoin'
    copydict = {
        'development.ini':'development.ini',
    }

class TestShabtiQuickWiki(TestBase):
    template='shabti_quickwiki'


