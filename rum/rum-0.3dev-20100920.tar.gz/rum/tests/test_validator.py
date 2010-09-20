# -*- coding: utf-8 -*-
from unittest import TestCase
from rum.validators import *
from rum import RumApp, Repository

class HamRepository(Repository):
    def get_id(self, o):
        return "37"
    def get(self, id_value):
        return Ham("Eggs")

class Ham(object):
    def __init__(self, value):
        self.value=value
    def __unicode__(self):
        return unicode(self.value)
class TestValidator(TestCase):
    def test_related_fetcher(self):
        app=RumApp(debug=True)
        app.repositoryfactory.register(HamRepository, Ham)
        v=RelatedFetcher(resource=Ham,app=app, foo=1)
        self.failUnlessEqual(unicode(v.to_python("37")),"Eggs")
        self.failUnlessEqual(v.from_python(Ham("Eggs")), "37")
    def test_unicode_string(self):
        v=UnicodeString()
        self.failUnlessEqual(v.from_python("Eggs"), "Eggs")
        self.failUnlessEqual(v.from_python(u"Eggs"), "Eggs")
        self.failUnlessEqual(v.from_python(Ham("Eggs")), "Eggs")
        self.failUnlessEqual(v.from_python(3), "3")