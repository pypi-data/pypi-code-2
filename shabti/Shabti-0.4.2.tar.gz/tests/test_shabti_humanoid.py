# -*- coding: utf-8 -*-
from test_make_project import TestBase

class TestShabtiHumanoid(TestBase):
    template='shabti_humanoid'
    copydict = {
        'development.ini':'development.ini',
        'test.ini':'test.ini',
    }

