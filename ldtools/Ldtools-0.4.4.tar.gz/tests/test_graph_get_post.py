# -*- coding: utf-8 -*-
import ldtools
import rdflib
import unittest2
from rdflib import compare


class TestOriginGET(unittest2.TestCase):
    def setUp(self):
        ldtools.Origin.objects.reset_store()
        ldtools.Resource.objects.reset_store()

        uri = "http://www.w3.org/People/Berners-Lee/card"
        self.origin, created = ldtools.Origin.objects.get_or_create(uri)
        self.origin.GET()


class TestResource2(unittest2.TestCase):
    def setUp(self):
        ldtools.Origin.objects.reset_store()
        ldtools.Resource.objects.reset_store()

    def test_manager_get_origin_guessing(self):
        uri = "http://example.org/resource"
        resourceuri = uri + "#me"
        resource, created = ldtools.Resource.objects.get_or_create(resourceuri,
                                                          auto_origin=True)
        assert str(resource._uri) == resourceuri
        resource_get = ldtools.Resource.objects.get(resourceuri)

    def test_manager_get_origin_guessing_miss(self):
        uri = "http://example.org/resource"
        resourceuri = uri + "#me"
        self.assertRaises(ldtools.Resource.DoesNotExist,
            ldtools.Resource.objects.get, resourceuri)


if __name__ == '__main__':
    unittest2.main()