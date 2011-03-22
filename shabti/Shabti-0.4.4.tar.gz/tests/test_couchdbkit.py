# -*- coding: utf-8 -*-
from test_make_project import TestBase

class TestShabtiCouchdbkit(TestBase):
    template='shabti_couchdbkit'
    sqlatesting=False
    copydict = {
        'development.ini':'development.ini',
    }

