#!/usr/bin/env python
#-*- coding: utf8 -*-
from __future__ import unicode_literals
from datetime import datetime

from twisted.trial import unittest
from pytz import utc
import pytz

from tele.show import Show
from tele.show import ShowList

class TestShow(unittest.TestCase):
    
    def test_new(self):
        s = Show(utc.localize(datetime(2011, 1, 5, 22, 15)), "Mentalist", "Vision", "Krimi")
        self.assertEqual(s.time, datetime(2011, 1, 5, 22, 15, tzinfo=utc))
        self.assertEqual(s.title, "Mentalist")
        self.assertEqual(s.subtitle, "Vision")
        self.assertEqual(s.genre, "Krimi")
    
    def test_new_no_utc(self):
        cet = pytz.timezone("CET")
        s = Show(cet.localize(datetime(2011, 1, 1, 11, 20)), "", "", "")
        self.assertEqual(s.time, datetime(2011, 1, 1, 10, 20, tzinfo=utc))
        
        s = Show(cet.localize(datetime(2011, 7, 1, 11, 20)), "", "", "")
        self.assertEqual(s.time, datetime(2011, 7, 1, 9, 20, tzinfo=utc))
    
class TestShowList(unittest.TestCase):
    
    def setUp(self):
        self.list = ShowList()
        self.list.append(Show(utc.localize(datetime(2011, 1, 4, 23, 0)),
                         "Stargate", "Das Tor zum Universum", "Actionserie"))
        self.list.append(Show(utc.localize(datetime(2011, 1, 5, 3, 30)),
                         "Departed - Unter Feinden", "", "Mafiafilm"))
        self.list.append(Show(utc.localize(datetime(2011, 1, 5, 1, 0)),
                         "Reich und Schön", "Betrug", "Telenovela"))

    def test_get_at(self):
        dt = utc.localize(datetime(2011, 1, 5, 0, 0))
        self.assertEquals(self.list.get_at(dt).title, "Stargate")
        
        dt = utc.localize(datetime(2011, 1, 5, 2, 0))
        self.assertEquals(self.list.get_at(dt).title, "Reich und Schön")
        
        dt = utc.localize(datetime(2011, 1, 5, 5, 0))
        self.assertEquals(self.list.get_at(dt).title, "Departed - Unter Feinden")

    def test_get_at_before(self):
        dt = utc.localize(datetime(2010, 1, 1, 0, 0))
        self.assertRaises(KeyError, self.list.get_at, dt)
     

