# -*- coding: utf-8 -*-
from test_make_project import TestBase

class TestShabtiAuthRepozePylons(TestBase):
    template='shabti_auth_repozepylons'
    copydict = {
        'development.ini':'development.ini',
        'auth_repoze_pylons_test.ini':'test.ini',
    }

class TestShabtiAuthRepozeWhat(TestBase):
    template='shabti_auth_repozewhat'
    copydict = {
        'development.ini':'development.ini',
        'auth_repoze_pylons_test.ini':'test.ini',
    }

class TestShabtiAuthRepozeWho(TestBase):
    template='shabti_auth_repozewho'
    copydict = {
        'development.ini':'development.ini',
        'auth_repoze_pylons_test.ini':'test.ini',
    }

