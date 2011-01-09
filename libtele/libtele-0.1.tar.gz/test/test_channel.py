#!/usr/bin/env python
#-*- coding: utf8 -*-
from __future__ import unicode_literals

from twisted.trial import unittest

from tele.channel import Channel
from tele.channel import ChannelList

class TestChannel(unittest.TestCase):
    
    def test_new(self):
        c = Channel("PTV", "Puls 4")
        self.assertEqual(c.key, "PTV")
        self.assertEqual(c.name, "Puls 4")
    
    def test_eq(self):
        a = Channel("PTV", "Puls 4")
        b = Channel("P4", "Puls 4")
        c = Channel("PTV", "Puls 4")
        
        self.assertFalse(a == b)
        self.assertFalse(b == a)
        self.assertTrue(a != b)
        self.assertTrue(b != a)
        
        self.assertFalse(b == c)
        self.assertFalse(c == b)
        self.assertTrue(b != c)
        self.assertTrue(c != b)
        
        self.assertTrue(c == a)
        self.assertTrue(a == c)
        self.assertFalse(c != a)
        self.assertFalse(a != c)
        
      
class TestChannelList(unittest.TestCase):
    
    def setUp(self):
        self.a = Channel("PTV", "Puls 4")
        self.b = Channel("ATV", "ATV")
        self.c = Channel("OE1", "Ö1")
        self.d = Channel("OE1", "Ö1")
        
        self.list = ChannelList()
        self.list.append(self.a)
        self.list.append(self.b)
        self.list.append(self.c)
        self.list.append(self.d)
    
    def test_get_by_name(self):
        self.assertIs(self.list.get_by_name("Puls 4"), self.a)
        self.assertIs(self.list.get_by_name("Ö1"), self.c)
        self.assertRaises(KeyError, self.list.get_by_name, "Kabel 1")
    
    def test_get_by_key(self):
        self.assertIs(self.list.get_by_key("OE1"), self.c)
        self.assertIs(self.list.get_by_key("ATV"), self.b)
        self.assertRaises(KeyError, self.list.get_by_key, "ORF1")
        

