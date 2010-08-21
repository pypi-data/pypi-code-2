# -*- coding: utf-8 -*-
from test_make_project import TestBase

class TestShabtiAuthRDFAlchemy(TestBase):
    template='shabti_auth_rdfalchemy'
    copydict = {'development.ini':'development.ini'}

class TestShabtiRDFAlchemy(TestBase):
    template='shabti_rdfalchemy'
    copydict = {
        'development.ini':'development.ini',
    }

