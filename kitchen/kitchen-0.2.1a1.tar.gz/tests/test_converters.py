# -*- coding: utf-8 -*-
#

import unittest
from nose import tools
from nose.plugins.skip import SkipTest

import StringIO
import warnings

try:
    import chardet
except:
    chardet = None

from kitchen.text import converters
from kitchen.text.exceptions import XmlEncodeError

import base_classes

class UnicodeNoStr(object):
    def __unicode__(self):
        return u'El veloz murciélago saltó sobre el perro perezoso.'

class StrNoUnicode(object):
    def __str__(self):
        return u'El veloz murciélago saltó sobre el perro perezoso.'.encode('utf8')

class StrReturnsUnicode(object):
    def __str__(self):
        return u'El veloz murciélago saltó sobre el perro perezoso.'

class UnicodeReturnsStr(object):
    def __unicode__(self):
        return u'El veloz murciélago saltó sobre el perro perezoso.'.encode('utf8')

class UnicodeStrCrossed(object):
    def __unicode__(self):
        return u'El veloz murciélago saltó sobre el perro perezoso.'.encode('utf8')

    def __str__(self):
        return u'El veloz murciélago saltó sobre el perro perezoso.'

class ReprUnicode(object):
    def __repr__(self):
        return u'ReprUnicode(El veloz murciélago saltó sobre el perro perezoso.)'

class TestConverters(unittest.TestCase, base_classes.UnicodeTestData):
    def test_to_unicode(self):
        '''Test to_unicode when the user gives good values'''
        tools.ok_(converters.to_unicode(self.u_japanese, encoding='latin1') == self.u_japanese)

        tools.ok_(converters.to_unicode(self.utf8_spanish) == self.u_spanish)
        tools.ok_(converters.to_unicode(self.utf8_japanese) == self.u_japanese)

        tools.ok_(converters.to_unicode(self.latin1_spanish, encoding='latin1') == self.u_spanish)
        tools.ok_(converters.to_unicode(self.euc_jp_japanese, encoding='euc_jp') == self.u_japanese)

        tools.assert_raises(TypeError, converters.to_unicode, *[5], **{'non_string': 'foo'})

    def test_to_unicode_errors(self):
        tools.ok_(converters.to_unicode(self.latin1_spanish) == self.u_spanish_replace)
        tools.ok_(converters.to_unicode(self.latin1_spanish, errors='ignore') == self.u_spanish_ignore)
        tools.assert_raises(UnicodeDecodeError, converters.to_unicode,
                *[self.latin1_spanish], **{'errors': 'strict'})

    def test_to_unicode_non_string(self):
        tools.ok_(converters.to_unicode(5) == u'')
        tools.ok_(converters.to_unicode(5, non_string='passthru') == 5)
        tools.ok_(converters.to_unicode(5, non_string='simplerepr') == u'5')
        tools.ok_(converters.to_unicode(5, non_string='repr') == u'5')
        tools.assert_raises(TypeError, converters.to_unicode, *[5], **{'non_string': 'strict'})

        tools.ok_(converters.to_unicode(UnicodeNoStr(), non_string='simplerepr') == self.u_spanish)
        tools.ok_(converters.to_unicode(StrNoUnicode(), non_string='simplerepr') == self.u_spanish)
        tools.ok_(converters.to_unicode(StrReturnsUnicode(), non_string='simplerepr') == self.u_spanish)
        tools.ok_(converters.to_unicode(UnicodeReturnsStr(), non_string='simplerepr') == self.u_spanish)
        tools.ok_(converters.to_unicode(UnicodeStrCrossed(), non_string='simplerepr') == self.u_spanish)

        obj_repr = converters.to_unicode(object, non_string='simplerepr')
        tools.ok_(obj_repr == u"<type 'object'>" and isinstance(obj_repr, unicode))

    def test_to_bytes(self):
        '''Test to_bytes when the user gives good values'''
        tools.ok_(converters.to_bytes(self.utf8_japanese, encoding='latin1') == self.utf8_japanese)

        tools.ok_(converters.to_bytes(self.u_spanish) == self.utf8_spanish)
        tools.ok_(converters.to_bytes(self.u_japanese) == self.utf8_japanese)

        tools.ok_(converters.to_bytes(self.u_spanish, encoding='latin1') == self.latin1_spanish)
        tools.ok_(converters.to_bytes(self.u_japanese, encoding='euc_jp') == self.euc_jp_japanese)

    def test_to_bytes_errors(self):
        tools.ok_(converters.to_bytes(self.u_mixed, encoding='latin1') ==
                self.latin1_mixed_replace)
        tools.ok_(converters.to_bytes(self.u_mixed, encoding='latin',
            errors='ignore') == self.latin1_mixed_ignore)
        tools.assert_raises(UnicodeEncodeError, converters.to_bytes,
            *[self.u_mixed], **{'errors': 'strict', 'encoding': 'latin1'})

    def _check_repr_bytes(self, repr_string, obj_name):
        tools.ok_(isinstance(repr_string, str))
        match = self.repr_re.match(repr_string)
        tools.ok_(match != None)
        tools.ok_(match.groups()[0] == obj_name)

    def test_to_bytes_non_string(self):
        tools.ok_(converters.to_bytes(5) == '')
        tools.ok_(converters.to_bytes(5, non_string='passthru') == 5)
        tools.ok_(converters.to_bytes(5, non_string='simplerepr') == '5')
        tools.ok_(converters.to_bytes(5, non_string='repr') == '5')

        # Raise a TypeError if the msg is non_string and we're set to strict
        tools.assert_raises(TypeError, converters.to_bytes, *[5], **{'non_string': 'strict'})
        # Raise a TypeError if given an invalid non_string arg
        tools.assert_raises(TypeError, converters.to_bytes, *[5], **{'non_string': 'INVALID'})

        # No __str__ method so this returns repr
        string = converters.to_bytes(UnicodeNoStr(), non_string='simplerepr')
        self._check_repr_bytes(string, 'UnicodeNoStr')

        # This object's _str__ returns a utf8 encoded object
        tools.ok_(converters.to_bytes(StrNoUnicode(), non_string='simplerepr') == self.utf8_spanish)

        # This object's __str__ returns unicode which to_bytes converts to utf8
        tools.ok_(converters.to_bytes(StrReturnsUnicode(), non_string='simplerepr') == self.utf8_spanish)
        # Unless we explicitly ask for something different
        tools.ok_(converters.to_bytes(StrReturnsUnicode(),
            non_string='simplerepr', encoding='latin1') == self.latin1_spanish)

        # This object has no __str__ so it returns repr
        string = converters.to_bytes(UnicodeReturnsStr(), non_string='simplerepr')
        self._check_repr_bytes(string, 'UnicodeReturnsStr')

        # This object's __str__ returns unicode which to_bytes converts to utf8
        tools.ok_(converters.to_bytes(UnicodeStrCrossed(), non_string='simplerepr') == self.utf8_spanish)

        # This object's __repr__ returns unicode which to_bytes converts to utf8
        tools.ok_(converters.to_bytes(ReprUnicode(), non_string='simplerepr')
                == u'ReprUnicode(El veloz murciélago saltó sobre el perro perezoso.)'.encode('utf8'))
        tools.ok_(converters.to_bytes(ReprUnicode(), non_string='repr') ==
                u'ReprUnicode(El veloz murciélago saltó sobre el perro perezoso.)'.encode('utf8'))

        obj_repr = converters.to_bytes(object, non_string='simplerepr')
        tools.ok_(obj_repr == "<type 'object'>" and isinstance(obj_repr, str))

    def test_unicode_to_xml(self):
        tools.ok_(converters.unicode_to_xml(None) == '')
        tools.assert_raises(XmlEncodeError, converters.unicode_to_xml, *['byte string'])
        tools.assert_raises(ValueError, converters.unicode_to_xml, *[u'string'], **{'control_chars': 'foo'})
        tools.assert_raises(XmlEncodeError, converters.unicode_to_xml,
                *[u'string\u0002'], **{'control_chars': 'strict'})
        tools.ok_(converters.unicode_to_xml(self.u_entity) == self.utf8_entity_escape)
        tools.ok_(converters.unicode_to_xml(self.u_entity, attrib=True) == self.utf8_attrib_escape)

    def test_xml_to_unicode(self):
        tools.ok_(converters.xml_to_unicode(self.utf8_entity_escape, 'utf8', 'replace') == self.u_entity)
        tools.ok_(converters.xml_to_unicode(self.utf8_attrib_escape, 'utf8', 'replace') == self.u_entity)

    def test_xml_to_byte_string(self):
        tools.ok_(converters.xml_to_byte_string(self.utf8_entity_escape, 'utf8', 'replace') == self.u_entity.encode('utf8'))
        tools.ok_(converters.xml_to_byte_string(self.utf8_attrib_escape, 'utf8', 'replace') == self.u_entity.encode('utf8'))

        tools.ok_(converters.xml_to_byte_string(self.utf8_attrib_escape,
            output_encoding='euc_jp', errors='replace') ==
            self.u_entity.encode('euc_jp', 'replace'))
        tools.ok_(converters.xml_to_byte_string(self.utf8_attrib_escape,
            output_encoding='latin1', errors='replace') ==
            self.u_entity.encode('latin1', 'replace'))

    def test_byte_string_to_xml(self):
        tools.assert_raises(XmlEncodeError, converters.byte_string_to_xml, *[u'test'])
        tools.ok_(converters.byte_string_to_xml(self.utf8_entity) == self.utf8_entity_escape)
        tools.ok_(converters.byte_string_to_xml(self.utf8_entity, attrib=True) == self.utf8_attrib_escape)

    def test_bytes_to_xml(self):
        tools.ok_(converters.bytes_to_xml(self.b_byte_chars) == self.b_byte_encoded)

    def test_xml_to_bytes(self):
        tools.ok_(converters.xml_to_bytes(self.b_byte_encoded) == self.b_byte_chars)

    def test_guess_encoding_to_xml(self):
        tools.ok_(converters.guess_encoding_to_xml(self.u_entity) == self.utf8_entity_escape)
        tools.ok_(converters.guess_encoding_to_xml(self.utf8_spanish) == self.utf8_spanish)
        tools.ok_(converters.guess_encoding_to_xml(self.latin1_spanish) == self.utf8_spanish)
        tools.ok_(converters.guess_encoding_to_xml(self.utf8_japanese) == self.utf8_japanese)

    def test_guess_encoding_to_xml_euc_japanese(self):
        if chardet:
            tools.ok_(converters.guess_encoding_to_xml(self.euc_jp_japanese)
                    == self.utf8_japanese)
        else:
            raise SkipTest('chardet not installed, euc_japanese won\'t be detected')

    def test_guess_encoding_to_xml_euc_japanese_mangled(self):
        if chardet:
            raise SkipTest('chardet installed, euc_japanese won\'t be mangled')
        else:
            tools.ok_(converters.guess_encoding_to_xml(self.euc_jp_japanese)
                    == self.utf8_mangled_euc_jp_as_latin1)

class TestGetWriter(unittest.TestCase, base_classes.UnicodeTestData):
    def setUp(self):
        self.io = StringIO.StringIO()

    def test_utf8_writer(self):
        writer = converters.getwriter('utf-8')
        io = writer(self.io)
        io.write(u'%s\n' % self.u_japanese)
        io.seek(0)
        result = io.read().strip()
        tools.ok_(result == self.utf8_japanese)

        io.seek(0)
        io.truncate(0)
        io.write('%s\n' % self.euc_jp_japanese)
        io.seek(0)
        result = io.read().strip()
        tools.ok_(result == self.euc_jp_japanese)

        io.seek(0)
        io.truncate(0)
        io.write('%s\n' % self.utf8_japanese)
        io.seek(0)
        result = io.read().strip()
        tools.ok_(result == self.utf8_japanese)

    def test_error_handlers(self):
        '''Test setting alternate error handlers'''
        writer = converters.getwriter('latin1')
        io = writer(self.io, errors='strict')
        tools.assert_raises(UnicodeEncodeError, io.write, self.u_japanese)

class TestDeprecatedConverters(unittest.TestCase, base_classes.UnicodeTestData):
    def setUp(self):
        warnings.simplefilter('ignore', DeprecationWarning)

    def tearDown(self):
        warnings.simplefilter('default', DeprecationWarning)

    def test_to_xml(self):
        tools.ok_(converters.to_xml(self.u_entity) == self.utf8_entity_escape)
        tools.ok_(converters.to_xml(self.utf8_spanish) == self.utf8_spanish)
        tools.ok_(converters.to_xml(self.latin1_spanish) == self.utf8_spanish)
        tools.ok_(converters.to_xml(self.utf8_japanese) == self.utf8_japanese)

    def test_to_utf8(self):
        tools.ok_(converters.to_utf8(self.u_japanese) == self.utf8_japanese)
        tools.ok_(converters.to_utf8(self.utf8_spanish) == self.utf8_spanish)

    def test_to_str(self):
        tools.ok_(converters.to_str(self.u_japanese) == self.utf8_japanese)
        tools.ok_(converters.to_str(self.utf8_spanish) == self.utf8_spanish)
        tools.ok_(converters.to_str(object) == "<type 'object'>")
