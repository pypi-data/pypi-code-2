#!/usr/bin/env python
#-*- coding: utf8 -*-
from __future__ import unicode_literals
from datetime import datetime
import os

from twisted.trial import unittest
from pytz import utc
import pytz

from tele.client import Client
from tele.client import _init_cache
from tele.client import _get_page
from tele.channel import Channel

MOCKUPS = os.path.abspath(os.path.join(os.path.dirname(__file__), "mockups"))

class TestInitCache(unittest.TestCase):
    
    def test_success(self):
        path = os.path.join("cache_test_success")
        if os.path.isdir(path):
            os.path.unlink(path)
        
        cache = _init_cache(path)
        self.assertEqual(cache, os.path.abspath(path))
        self.assertTrue(os.path.isdir(path))
    
    def test_existing(self):
        path = "cache_test_existing"
        os.makedirs(path)
        
        cache = _init_cache(path)
        self.assertEqual(cache, os.path.abspath(path))
        self.assertTrue(os.path.isdir(path))
    
    def test_error(self):
        cache = _init_cache(os.devnull)
        self.assertIs(cache, None)

class TestGetPage(unittest.TestCase):
    
    def test_success(self):
        def on_success(html):
            self.assertEquals(html.tag, "html")
        
        url = "file://" + os.path.join(MOCKUPS, "programmvorschau")
        
        defer = _get_page(url, {}, None)
        defer.addCallback(on_success)
        return defer
    
    def test_error(self):
        url = "file://invalid/and/so/on"
        
        defer = _get_page(url, {}, None)
        defer.addCallback(self.fail)
        defer.addErrback(lambda failure: None)
        return defer
    
    def test_get(self):
        url = "file://" + os.path.join(MOCKUPS, "programmvorschau")
        get = {"channels": "ATV", "tsstart": "1294200000"}
        
        defer = _get_page(url, get, None)
        return defer
    
    def test_cache(self):
        url = "file://" + os.path.join(MOCKUPS, "programmvorschau")
        get = {}
        cache = _init_cache("get_page_test_cache_cache")
        
        self.assertTrue(cache)
        if os.path.isfile(os.path.join(cache, "489c8f034588f669f8b6d919d6bf9f3f79b5e2e7")):
            os.unlink(os.path.join(cache, "489c8f034588f669f8b6d919d6bf9f3f79b5e2e7"))
        
        def on_success(html):
            self.assertEqual(html.tag, "html")
            self.assertTrue(os.path.isfile(os.path.join(cache, "489c8f034588f669f8b6d919d6bf9f3f79b5e2e7")))
        
        defer = _get_page(url, get, cache)
        defer.addCallback(on_success)
        return defer

class TestClient(unittest.TestCase):
    
    def setUp(self):
        self.client = Client("file://" + os.path.join(MOCKUPS, "programmvorschau"),
                             "test_client_cache")
    
    def test_get_channels(self):
        def on_success(channels):
            self.assertEqual(len(channels), 114)
            self.assertEqual(channels.get_by_name("kabel").key, "KAB")
            self.assertEqual(channels.get_by_key("PTV").name, "Puls 4")

        defer = self.client.get_channels()
        defer.addCallback(on_success)
    
    def test_get_tele_day(self):
        def on_success(shows):
            self.assertEqual(len(shows), 32)
            self.assertEqual(shows[1].title, "Für alle Fälle Amy")
            self.assertEqual(shows[2].subtitle, "Ein langer harter Sommer (1/2)")
            self.assertEqual(shows[-1].genre, "Comedyserie")
            self.assertEqual(shows[-2].time, datetime(2011, 1, 6, 3, 30, tzinfo=utc))
            self.assertEqual(shows[0].time, datetime(2011, 1, 5, 4, 5, tzinfo=utc))
        
        cet = pytz.timezone("CET")
        dt = cet.localize(datetime(2011, 1, 5, 10, 0))
        defer = self.client.get_tele_day(Channel("ATV", "ATV"), dt)
        defer.addCallback(on_success)
        return defer
    
    def test_get_prev_tele_day(self):
        def on_success(shows):
            self.assertEqual(len(shows), 25)
            self.assertEqual(shows[0].time, datetime(2011, 1, 5, 4, 35, tzinfo=utc))
            self.assertEqual(shows[-1].time, datetime(2011, 1, 6, 3, 45, tzinfo=utc))
        
        cet = pytz.timezone("CET")
        dt = cet.localize(datetime(2011, 1, 6, 4, 59))
        defer = self.client.get_tele_day(Channel("PTV", "Puls 4"), dt)
        defer.addCallback(on_success)
        return defer
    
    def test_get_shows(self):
        def on_success(shows):
            self.assertEqual(shows[0].time, datetime(2011, 1, 10, 3, 40, tzinfo=utc))
            self.assertEqual(shows[1].time, datetime(2011, 1, 10, 4, 20, tzinfo=utc))
            self.assertEqual(shows[2].title, "Seitenblicke")
            self.assertEqual(shows[-1].time, datetime(2011, 1, 11, 10, 45, tzinfo=utc))
            self.assertEqual(shows[11].subtitle, "Alles auf Anfang")
        
        cet = pytz.timezone("CET")
        dtfrom = cet.localize(datetime(2011, 1, 10, 5, 10))
        dtto = cet.localize(datetime(2011, 1, 11, 12, 0))
        
        defer = self.client.get_shows(Channel("ORF1", "ORF eins"), dtfrom, dtto)
        defer.addCallback(on_success)
        return defer
    
    def test_get_shows_point(self):
        def on_success(shows):
            self.assertEqual(len(shows), 1)
            self.assertEqual(shows[0].title, "Desperate Housewives")
        
        cet = pytz.timezone("CET")
        dt = cet.localize(datetime(2011, 1, 10, 21, 6))
        defer = self.client.get_shows(Channel("ORF1", "ORF eins"), dt, dt)
        defer.addCallback(on_success)
        return defer

    def test_get_shows_exact_start(self):
        def on_success(shows):
            self.assertEqual(len(shows), 1)
            self.assertEqual(shows[0].title, "Desperate Housewives")
        
        cet = pytz.timezone("CET")
        dt = cet.localize(datetime(2011, 1, 10, 21, 5))
        defer = self.client.get_shows(Channel("ORF1", "ORF eins"), dt, dt)
        defer.addCallback(on_success)
        return defer
    
    def test_get_shows_error(self):
        cet = pytz.timezone("CET")
        dt = cet.localize(datetime(2000, 1, 1))  # this won't exist
        defer = self.client.get_shows(Channel("ORF1", "ORF eins"), dt, dt)
        defer.addCallback(self.fail)
        defer.addErrback(lambda failure: None)
        return defer
        
