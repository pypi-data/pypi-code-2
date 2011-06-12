"""
Ax_Handoff Unit Tests.

To run these tests from the command line:

    $ python -m axonchisel.handoff.tests

------------------------------------------------------------------------------
Author: Dan Kamins <dos at axonchisel dot net>
Copyright (c) 2011 Dan Kamins, AxonChisel.net
"""


# ----------------------------------------------------------------------------


import os
import hashlib
import cgi
import copy
import unittest

import axonchisel.handoff.util as util
import axonchisel.handoff.protocol as protocol
import axonchisel.handoff.error as error
from axonchisel.handoff.object import Ax_Handoff


# ----------------------------------------------------------------------------


#
# Unit Tests
#


class Test_ub64(unittest.TestCase):
    """Test 'base64url' Base64 encoding and decoding utilities."""

    def setUp(self):
        pass

    def test_rpad(self):
        for slen in range(0, 500):
            s = os.urandom(slen)
            senc = util.ub64encode(s)
            senc_urlenc = cgi.escape(senc)  # test URL-safeness
            self.assertEqual(senc, senc_urlenc)
            sdec = util.ub64decode(senc)         # test enc/dec equivalent
            self.assertEqual(s, sdec)


class Test_rpad(unittest.TestCase):
    """Test padding and unpadding utilities."""

    def setUp(self):
        pass

    def test_rpad(self):
        for block_size in range(4, 64, 4):
            for slen in range(0, 128):
                s = "x" * slen
                spad = util.rpad_string(s, block_size=block_size, pad_char='p')
                self.assertEqual(len(spad) % block_size, 0)
                self.assertTrue(len(spad) >= len(s))

    def test_rpad_crypto(self):
        for block_size in range(4, 64, 4):
            for slen in range(0, 128):
                s = "x" * slen
                spad = util.rpad_string_crypto(s, block_size=block_size)
                self.assertEqual(len(spad) % block_size, 0)
                self.assertTrue(len(spad) > len(s))
                self.assertEqual(ord(spad[-1]), len(spad) - len(s))
                sunpad = util.unrpad_string_crypto(spad, block_size=block_size)
                self.assertEqual(sunpad, s)



class Test_Header(unittest.TestCase):
    """Test Header protocol element."""

    def setUp(self):
        self.body = "This is a test body content here."
        self.body_hmac = hashlib.sha1(self.body).digest()

    def test_serialize_unserialize(self):

        # Serialize and test length:
        h1 = protocol.Header()
        h1.body_hmac = self.body_hmac
        hs1 = h1.serialize()
        self.assertEqual(len(hs1), protocol.Header.LENGTH)

        # Unserialize and compare body:
        h2 = protocol.Header.from_serialized(hs1)
        self.assertEqual(h2.body_hmac, h1.body_hmac)

        # Reserialize and compare with original serialization:
        hs2 = h2.serialize()
        self.assertEqual(hs2, hs1)

        # Test adding and replacing chars to trigger errors:
        for rep_char in ['%', '^', ')']:
            for pos in range(protocol.Header.LENGTH + 1):
                hs2x = hs2[:pos] + rep_char + hs2[pos:]  # add char
                self.assertRaises(error.UnserializeError, protocol.Header.from_serialized, hs2x)
            for pos in range(protocol.Header.LENGTH):
                hs2x = hs2[:pos] + rep_char + hs2[pos+1:]  # replace char
                self.assertRaises(error.UnserializeError, protocol.Header.from_serialized, hs2x)


class Test_Footer(unittest.TestCase):
    """Test Footer protocol element."""

    def setUp(self):
        pass

    def test_serialize_unserialize(self):

        # Serialize and test length:
        f1 = protocol.Footer()
        fs1 = f1.serialize()
        self.assertEqual(len(fs1), protocol.Footer.LENGTH)

        # Unserialize:
        f2 = protocol.Footer.from_serialized(fs1)

        # Reserialize and compare with original serialization:
        fs2 = f2.serialize()
        self.assertEqual(fs2, fs1)

        # Test adding and replacing chars to trigger errors:
        for rep_char in ['%', '^', ')']:
            for pos in range(protocol.Footer.LENGTH + 1):
                fs2x = fs2[:pos] + rep_char + fs2[pos:]  # add char
                self.assertRaises(error.UnserializeError, protocol.Footer.from_serialized, fs2x)
            for pos in range(protocol.Footer.LENGTH):
                fs2x = fs2[:pos] + rep_char + fs2[pos+1:]  # replace char
                self.assertRaises(error.UnserializeError, protocol.Footer.from_serialized, fs2x)


class Test_Body(unittest.TestCase):
    """Test Body protocol element."""

    def setUp(self):
        self.secret = "This is my secret phrase here! It's long & strong."
        self.data = "ADVANCE CONCORD TO WESTERN RIDGE 0600. FIRE FLARE TO INITIATE ARTILLERY. CONCORD IS GO. CONCORD IS GO."

    def test_serialize_unserialize(self):

        # Serialize:
        b1 = protocol.Body()
        b1.data = self.data
        bs1 = b1.serialize(secret=self.secret)

        # Unsserialize:
        b2 = protocol.Body.from_serialized(bs1, secret=self.secret)
        self.assertEqual(b2.data, b1.data)

        # Test adding and replacing chars in secret to trigger errors:
        for rep_char in ['%', '^', ')', 'a', '1']:
            for pos in range(len(self.secret) + 1):
                secretx = self.secret[:pos] + rep_char + self.secret[pos:]  # add char
                self.assertRaises(error.UnserializeError, protocol.Body.from_serialized, bs1, secret=secretx)
        for pos in range(len(self.secret)):
            secretx = self.secret[:pos] + chr(ord(self.secret[pos]) ^ 0xff) + self.secret[pos+1:]  # bit flip char
            self.assertRaises(error.UnserializeError, protocol.Body.from_serialized, bs1, secret=secretx)

        # Test adding and replacing chars to encrypted string to trigger errors:
        for rep_char in ['%', '^', ')', 'a', '1']:
            for pos in range(len(bs1) + 1):
                bs1x = bs1[:pos] + rep_char + bs1[pos:]  # add char
                self.assertRaises(error.UnserializeError, protocol.Body.from_serialized, bs1x, secret=self.secret)
        for rep_char in ['%', '^', ')']:
            for pos in range(len(bs1)):
                bs1x = bs1[:pos] + rep_char + bs1[pos+1:]  # replace char
                self.assertRaises(error.UnserializeError, protocol.Body.from_serialized, bs1x, secret=self.secret)


class Test_Envelope(unittest.TestCase):
    """Test full header+body+footer protocol envelope."""

    def setUp(self):
        self.secret = "This is my secret phrase here! It's long & strong."
        self.data = "ADVANCE CONCORD TO WESTERN RIDGE 0600. FIRE FLARE TO INITIATE ARTILLERY. CONCORD IS GO. CONCORD IS GO."

    def test_serialize_unserialize(self):

        # Build envelope:
        e1 = protocol.Envelope()
        e1.body.data = self.data
        
        # Serialize:
        es1 = e1.serialize(secret=self.secret)

        # Test URL-safeness:
        self.assertEqual(es1, cgi.escape(es1))
        
        # Unserialize:
        e2 = protocol.Envelope.from_serialized(es1, secret=self.secret)
        self.assertEqual(e1.body.data, e2.body.data)
        
        # Reserialize:
        es2 = e2.serialize(secret=self.secret)
        self.assertEqual(es1, es2)
        
        # Alter header HMAC (overwrite a 0 prefix) and trigger HMAC verify error:
        es1x = es1[:3] + '000000000000' + es1[15:]
        self.assertRaises(error.UnserializeError, protocol.Envelope.from_serialized, es1x, secret=self.secret)


class Test_Object(unittest.TestCase):
    """Test high level object wrapper."""

    def setUp(self):
        self.secret = "This is my secret phrase here! It's long & strong."
        self.obj = {
            "msg": "ADVANCE CONCORD TO WESTERN RIDGE 0600. FIRE FLARE TO INITIATE ARTILLERY. CONCORD IS GO. CONCORD IS GO.",
            "coords": [1.4325, -88.095],
            "d": { "foo": "Mike", "bar": [10, 12] }
        }
            

    def test_serialize_unserialize(self):

        # Encode/decode and compare:
        es1 = Ax_Handoff.encode(self.obj, secret=self.secret)
        obj2 = Ax_Handoff.decode(es1, secret=self.secret)
        self.assertEqual(self.obj, obj2)

        # Test encoding non-JSON-congruent data:
        obj3x = copy.copy(self.obj)
        obj3x['obj'] = object()  # objects cannot be JSON-encoded
        self.assertRaises(error.SerializeError, Ax_Handoff.encode, obj3x, secret=self.secret)


class Test_Unicode(unittest.TestCase):
    """Test Unicode in secret phrase and data payload."""

    def setUp(self):
        self.secret = u"\xfe\xeb\xebp-\xfe\xf6p! \xf1\xebv\xebr f\xf6rg\xe9t!"
        self.obj = u"#2 p\xe9nc\xedl"

    def test_serialize_unserialize(self):

        # Encode/decode and compare:
        es1 = Ax_Handoff.encode(self.obj, secret=self.secret)
        obj2 = Ax_Handoff.decode(es1, secret=self.secret)
        self.assertEqual(self.obj, obj2)
        
        # Test unicode version of encoded string:
        es1u = unicode(es1)
        obj2u = Ax_Handoff.decode(es1u, secret=self.secret)


class Test_Types(unittest.TestCase):
    """Test error handling of bad types."""

    def setUp(self):
        self.secret = "This is my secret phrase here! It's long & strong."
        self.obj = [5]
        self.not_string = [1,2,3]

    def test_serialize_unserialize(self):

        # Test non-string secrets to verify error handling:
        self.assertRaises(error.SerializeError, Ax_Handoff.encode, self.obj, secret=12345)
        self.assertRaises(error.UnserializeError, Ax_Handoff.decode, "fakeencstr", secret=12345)

        # Test non-string encstr to verify error handling:
        self.assertRaises(TypeError, Ax_Handoff.decode, self.not_string, secret=self.secret)
        self.assertRaises(TypeError, protocol.Header.from_serialized, self.not_string, secret=self.secret)
        self.assertRaises(TypeError, protocol.Body.from_serialized, self.not_string, secret=self.secret)
        self.assertRaises(TypeError, protocol.Footer.from_serialized, self.not_string, secret=self.secret)
        self.assertRaises(TypeError, protocol.Envelope.from_serialized, self.not_string, secret=self.secret)


# ----------------------------------------------------------------------------


if __name__ == '__main__':
    unittest.main()

