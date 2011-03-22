# -*- coding: utf-8 -*-
from test_make_project import TestBase

class TestShabtiAuthCouchDB(TestBase):
    template='shabti_auth_couchdb'
    sqlatesting=False
    copydict = {'development.ini':'development.ini',
                'test.ini':'test.ini'}

