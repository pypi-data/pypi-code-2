# coding=utf-8

import unittest
from xmltopy.xmlserializer import *
from test_classes import *
from lxml import etree
from datetime import datetime

try: import pytz
except ImportError: print 'WARNING! pytz not installed. datetime related tests will fail.'

class TestUnicodeToXml(unittest.TestCase):
    def test_ascii(self):
        widget = Widget()
        widget.Name = u'Woozle'
        widget.Description = u'The Woozle is Widget'
        
        tree = toxml(widget)
        expected = u'<Widget xmlns="http://www.example.com/schemas/widget"><Name>Woozle</Name><Description>The Woozle is Widget</Description></Widget>'
        self.assertEqual(expected, etree.tostring(tree, encoding=unicode))
        
        widget_after = fromxml(tree, Widget())
        self.assertEqual(u'Woozle', widget_after.Name)

    def test_boris(self):
        widget = Widget()
        widget.Name = u'Карлаф'
        widget.Description = u'The Woozle is Widget'
        
        tree = toxml(widget)
        expected = u'<Widget xmlns="http://www.example.com/schemas/widget"><Name>Карлаф</Name><Description>The Woozle is Widget</Description></Widget>'
        self.assertEqual(expected, etree.tostring(tree, encoding=unicode))
        
        widget_after = fromxml(tree, Widget())
        self.assertEqual(u'Карлаф', widget_after.Name)
        
    def test_arabic(self):
        widget = Widget()
        widget.Name = u'مثال.إختبار'
        widget.Description = u'The Woozle is Widget'
        
        tree = toxml(widget)
        expected = u'<Widget xmlns="http://www.example.com/schemas/widget"><Name>مثال.إختبار</Name><Description>The Woozle is Widget</Description></Widget>'
        self.assertEqual(expected, etree.tostring(tree, encoding=unicode))
        
        widget_after = fromxml(tree, Widget())
        self.assertEqual(u'مثال.إختبار', widget_after.Name)
        
    def test_simplified_chinese(self):
        widget = Widget()
        widget.Name = u'例子.测试'
        widget.Description = u'The Woozle is Widget'
        
        tree = toxml(widget)
        expected = u'<Widget xmlns="http://www.example.com/schemas/widget"><Name>例子.测试</Name><Description>The Woozle is Widget</Description></Widget>'
        self.assertEqual(expected, etree.tostring(tree, encoding=unicode))
        
        widget_after = fromxml(tree, Widget())
        self.assertEqual(u'例子.测试', widget_after.Name)
        
    def test_traditional_chinese(self):
        widget = Widget()
        widget.Name = u'例子.測試'
        widget.Description = u'The Woozle is Widget'
        
        tree = toxml(widget)
        expected = u'<Widget xmlns="http://www.example.com/schemas/widget"><Name>例子.測試</Name><Description>The Woozle is Widget</Description></Widget>'
        self.assertEqual(expected, etree.tostring(tree, encoding=unicode))
        
        widget_after = fromxml(tree, Widget())
        self.assertEqual(u'例子.測試', widget_after.Name)
        
    def test_greek(self):
        widget = Widget()
        widget.Name = u'παράδειγμα.δοκιμή'
        widget.Description = u'The Woozle is Widget'
        
        tree = toxml(widget)
        expected = u'<Widget xmlns="http://www.example.com/schemas/widget"><Name>παράδειγμα.δοκιμή</Name><Description>The Woozle is Widget</Description></Widget>'
        self.assertEqual(expected, etree.tostring(tree, encoding=unicode))
        
        widget_after = fromxml(tree, Widget())
        self.assertEqual(u'παράδειγμα.δοκιμή', widget_after.Name)
        
    def test_hindi(self):
        widget = Widget()
        widget.Name = u'उदाहरण.परीक्षा'
        widget.Description = u'The Woozle is Widget'
        
        tree = toxml(widget)
        expected = u'<Widget xmlns="http://www.example.com/schemas/widget"><Name>उदाहरण.परीक्षा</Name><Description>The Woozle is Widget</Description></Widget>'
        self.assertEqual(expected, etree.tostring(tree, encoding=unicode))
        
        widget_after = fromxml(tree, Widget())
        self.assertEqual(u'उदाहरण.परीक्षा', widget_after.Name)
        
    def test_japanese(self):
        widget = Widget()
        widget.Name = u'例え.テスト'
        widget.Description = u'The Woozle is Widget'
        
        tree = toxml(widget)
        expected = u'<Widget xmlns="http://www.example.com/schemas/widget"><Name>例え.テスト</Name><Description>The Woozle is Widget</Description></Widget>'
        self.assertEqual(expected, etree.tostring(tree, encoding=unicode))
        
        widget_after = fromxml(tree, Widget())
        self.assertEqual(u'例え.テスト', widget_after.Name)
        
    def test_korean(self):
        widget = Widget()
        widget.Name = u'실례.테스트'
        widget.Description = u'The Woozle is Widget'
        
        tree = toxml(widget)
        expected = u'<Widget xmlns="http://www.example.com/schemas/widget"><Name>실례.테스트</Name><Description>The Woozle is Widget</Description></Widget>'
        self.assertEqual(expected, etree.tostring(tree, encoding=unicode))
        
        widget_after = fromxml(tree, Widget())
        self.assertEqual(u'실례.테스트', widget_after.Name)
        
    def test_persian(self):
        widget = Widget()
        widget.Name = u'مثال.آزمایشی'
        widget.Description = u'The Woozle is Widget'
        tree = toxml(widget)
        
        f = open('testunicodetoxml.xml', 'w')
        f.write(etree.tostring(tree, encoding='UTF-8'))
        f.close()
        
        expected = u'<Widget xmlns="http://www.example.com/schemas/widget"><Name>مثال.آزمایشی</Name><Description>The Woozle is Widget</Description></Widget>'
        self.assertEqual(expected, etree.tostring(tree, encoding=unicode))
        
        widget_after = fromxml(tree, Widget())
        self.assertEqual(u'مثال.آزمایشی', widget_after.Name)
        
    def test_tamil(self):
        widget = Widget()
        widget.Name = u'உதாரணம்.பரிட்சை'
        widget.Description = u'The Woozle is Widget'
        
        tree = toxml(widget)
        expected = u'<Widget xmlns="http://www.example.com/schemas/widget"><Name>உதாரணம்.பரிட்சை</Name><Description>The Woozle is Widget</Description></Widget>'
        self.assertEqual(expected, etree.tostring(tree, encoding=unicode))
        
        widget_after = fromxml(tree, Widget())
        self.assertEqual(u'உதாரணம்.பரிட்சை', widget_after.Name)
        
    def test_yiddish(self):
        widget = Widget()
        widget.Name = u'உதாரணம்.பரிட்சை'
        widget.Description = u'The Woozle is Widget'
        
        tree = toxml(widget)
        expected = u'<Widget xmlns="http://www.example.com/schemas/widget"><Name>உதாரணம்.பரிட்சை</Name><Description>The Woozle is Widget</Description></Widget>'
        self.assertEqual(expected, etree.tostring(tree, encoding=unicode))
        
        widget_after = fromxml(tree, Widget())
        self.assertEqual(u'உதாரணம்.பரிட்சை', widget_after.Name)
        