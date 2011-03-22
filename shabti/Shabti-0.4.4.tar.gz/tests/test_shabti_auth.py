# -*- coding: utf-8 -*-
from test_make_project import TestBase

class TestShabtiAuth(TestBase):
    template = 'shabti_auth'
    copydict = {
        'development.ini':'development.ini',
    }

class TestShabtiAuthXp(TestBase):
    template='shabti_auth_xp'

class TestShabtiAuthPlus(TestBase):
    template='shabti_authplus'
    copydict = {
        'development.ini':'development.ini',
    }

