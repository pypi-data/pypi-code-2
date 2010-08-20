# -*- coding: utf-8 -*-
from test_make_project import TestBase

class TestPylons(TestBase):
    # template = None
    template = 'pylons' 
    def test_project_paster_create(self):
        self.paster_create()

class TestShabtiMicrosite(TestBase):
    template='shabti_microsite'

class TestShabtiPyBlosxom(TestBase):
    sqlatesting = False
    template='shabti_pyblosxom'

