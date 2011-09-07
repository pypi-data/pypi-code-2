# -*- coding: utf-8 -*-
import ldtools
import rdflib
import unittest2
from rdflib import compare


class OriginIsDirtyTest(unittest2.TestCase):
    def setUp(self):
        ldtools.Origin.objects.reset_store()
        ldtools.Resource.objects.reset_store()

    def test_resource_created_for_origin_causes_unsaved(self):
        origin = ldtools.Origin.objects.create("http://example.org/",
            BACKEND=ldtools.MemoryBackend())

        self.assert_(not origin.has_unsaved_changes())

        origin.GET()

        self.assertEqual(len(list(ldtools.Resource.objects.all())), 0)
        self.assertEqual(len(list(ldtools.Origin.objects.all())), 1)
        self.assert_(origin.processed)

        resource = ldtools.Resource.objects.create("http://example.org/test1",
            origin=origin)

        self.assertEqual(len(list(ldtools.Resource.objects.all())), 1)
        self.assertEqual(len(list(ldtools.Origin.objects.all())), 1)

        self.assert_(origin.has_unsaved_changes())

    def test_resource_created_for_origin_saved_does_not_cause_unsaved(self):
        origin = ldtools.Origin.objects.create("http://example.org/",
            BACKEND=ldtools.MemoryBackend())

        self.assert_(not origin.has_unsaved_changes())

        origin.GET()

        self.assertEqual(len(list(ldtools.Resource.objects.all())), 0)
        self.assertEqual(len(list(ldtools.Origin.objects.all())), 1)
        self.assert_(origin.processed)

        resource = ldtools.Resource.objects.create("http://example.org/test1",
            origin=origin)
        resource.save()

        self.assertEqual(len(list(ldtools.Resource.objects.all())), 1)
        self.assertEqual(len(list(ldtools.Origin.objects.all())), 1)

        self.assert_(not origin.has_unsaved_changes())


class AcceptanceTests(unittest2.TestCase):
    def setUp(self):
        ldtools.Origin.objects.reset_store()
        ldtools.Resource.objects.reset_store()

    def test_create_origin(self):
        origin = ldtools.Origin.objects.create("http://example.org/",
            BACKEND=ldtools.MemoryBackend())

        origin.GET()

        self.assertEqual(len(list(ldtools.Resource.objects.all())), 0)
        self.assertEqual(len(list(ldtools.Origin.objects.all())), 1)
        self.assert_(origin.processed)

        resource = ldtools.Resource.objects.create("http://example.org/test1",
            origin=origin)

        self.assertEqual(len(list(ldtools.Resource.objects.all())), 1)
        self.assertEqual(len(list(ldtools.Origin.objects.all())), 1)

        resource._origin.GET()

        self.assertEqual(len(list(ldtools.Resource.objects.all())), 1)
        self.assertEqual(len(list(ldtools.Origin.objects.all())), 1)
