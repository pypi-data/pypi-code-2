"""
Ax_Handoff Protocol.

Contains class representations of protocol elements:
  - Header
  - Body
  - Footer
  - Envelope (wraps header, body, footer)

Each element is able to serialize/unserialize to/from encoded strings.

Clients wishing to descend below the higher-level "Ax_Handoff" wrapper in the
object module may wish to use the "Envelope" element here.

------------------------------------------------------------------------------
Author: Dan Kamins <dos at axonchisel dot net>
Copyright (c) 2011 Dan Kamins, AxonChisel.net
"""


# ----------------------------------------------------------------------------


import os
import math
import hashlib
import zlib
import hmac

try:
    from Crypto.Cipher import AES
except ImportError as e:
    print "\n*** Please ensure that PyCrypto is installed! ***\n"
    raise

import axonchisel.handoff.config as config
import axonchisel.handoff.util as util
import axonchisel.handoff.error as error


# ----------------------------------------------------------------------------


#
# Protocol Elements
#


class ProtocolElement(object):
    """Abstract superclass for protocol elements."""
    pass

    
class Header(ProtocolElement):
    """Header protocol element."""

    MAGIC         = "XH"
    VARIANT       = "A"
    HMAC_BITS     = 160                                             # (160 bits for SHA1)
    LENGTH_HMAC   = int(math.ceil(HMAC_BITS/8*4/3.0))               # 27
    LENGTH        = len(MAGIC) + len(VARIANT) + LENGTH_HMAC         # 30=2+1+27
    
    def __init__(self):
        self.body_hmac = ""    # byte string

    @classmethod
    def from_serialized(cls, encstr):
        """Construct and return new object by unserializing string. Raise UnserializeError on errors."""
        o = Header()
        o.unserialize(encstr)
        return o

    def serialize(self):
        """Serialize self into string and return. Raise SerializeError on errors."""
        if len(self.body_hmac) != Header.HMAC_BITS/8:
            raise error.SerializeError("Header body_hmac size {0}B is not {1}B".format(len(self.body_hmac), Header.HMAC_BITS/8))
        return "{magic}{variant}{hmac}".format(
            magic=Header.MAGIC, 
            variant=Header.VARIANT, 
            hmac=util.ub64encode(self.body_hmac))

    def unserialize(self, encstr):
        """Unserialize string into self. Raise UnserializeError on errors."""
        if not isinstance(encstr, basestring):
            raise TypeError("Header can only unserialize from strings, but {0} given".format(type(encstr)))
        if len(encstr) != Header.LENGTH:
            raise error.UnserializeError("Header length {0} is not {1}".format(len(encstr), Header.LENGTH))
        if encstr[0:2] != Header.MAGIC:
            raise error.UnserializeError("Header magic '{0}' is not '{1}'".format(encstr[0:2], Header.MAGIC))
        if encstr[2:3] != Header.VARIANT:
            raise error.UnserializeError("Header variant '{0}' is not '{1}'".format(encstr[2:3], Header.VARIANT))

        try:
            self.body_hmac = util.ub64decode(encstr[3:])
        except TypeError as e:
            raise error.UnserializeError("Error decoding body_hmac: {0!r}".format(e))

    def compute_body_hmac(self, serialized_body, secret=""):
        """Compute and return the body hmac based on serialized Body ProtocolElement passed."""
        return hmac.new(self._hmac_key(secret), serialized_body, config.HMAC_DIGEST).digest()

    def _hmac_key(self, secret=""):
        """Generate and return HMAC key (bytes) based on secret."""
        secret = util.cast_str(secret, "Secret phrase")
        secret_hash_512 = hashlib.sha512(secret).digest()   # make lots of bits
        return secret_hash_512[0:(config.HMAC_KEY_BITS/8)]  # (use all 512 bits for A variant)


class Footer(ProtocolElement):
    """Footer protocol element."""

    MAGIC         = "HX"
    VARIANT       = "A"
    LENGTH        = len(MAGIC)       # 2
    
    def __init__(self):
        pass

    @classmethod
    def from_serialized(cls, encstr):
        """Construct and return new object by unserializing string. Raise UnserializeError on errors."""
        o = Footer()
        o.unserialize(encstr)
        return o

    def serialize(self):
        """Serialize self into string and return. Raise SerializeError on errors."""
        return "{magic}".format(magic=Footer.MAGIC)

    def unserialize(self, encstr):
        """Unserialize string into self. Raise UnserializeError on errors."""
        if not isinstance(encstr, basestring):
            raise TypeError("Footer can only unserialize from strings, but {0} given".format(type(encstr)))
        if len(encstr) != Footer.LENGTH:
            raise error.UnserializeError("Footer length {0} is not {1}".format(len(encstr), Footer.LENGTH))
        if encstr[0:2] != Footer.MAGIC:
            raise error.UnserializeError("Footer magic '{0}' is not '{1}'".format(encstr[0:2], Footer.MAGIC))
    

class Body(ProtocolElement):
    """Body protocol element."""

    VARIANT       = "A"
    
    def __init__(self):
        self.iv = None                # 16 bytes crypto initialization vector
        self.data = ""                # data byte string

    @classmethod
    def from_serialized(cls, encstr, secret=""):
        """Construct and return new object by unserializing string. Raise UnserializeError on errors."""
        o = Body()
        o.unserialize(encstr, secret=secret)
        return o

    def serialize(self, secret=""):
        """Serialize self into string and return. Raise SerializeError on errors."""
        if secret == "":
            raise error.SerializeError("No secret specific for body serialization")
        
        if not self.iv:               # if have iv then use it, else generate one
            self._random_iv()
            
        zdata = zlib.compress(self.data, 9)
        zdata_padded = util.rpad_string_crypto(zdata, block_size=config.AES_BLOCK_BITS/8)

        try:
            aes = AES.new(self._aes_key(secret), config.AES_MODE, self.iv)
        except TypeError as e:
            raise error.SerializeError("Unable to compute body AES key: {0!r}".format(e))
        encrypted = aes.encrypt(zdata_padded)
        dstr = "{iv}{enc}".format(iv=self.iv, enc=encrypted)
        s = util.ub64encode(dstr)
        return s

    def unserialize(self, encstr, secret=""):
        """Unserialize string into self. Raise UnserializeError on errors."""
        if not isinstance(encstr, basestring):
            raise TypeError("Body can only unserialize from strings, but {0} given".format(type(encstr)))
        if secret == "":
            raise error.UnserializeError("No secret specific for body unserialization")

        try:
            dstr = util.ub64decode(encstr)
        except TypeError as e:
            raise error.UnserializeError("Error decoding body: {0!r}".format(e))
            
        if len(dstr) < (config.AES_IV_BITS/8):
            raise error.UnserializeError("Decoded body too short for iv ({0})".format(len(dstr)))
        self.iv = dstr[0:config.AES_IV_BITS/8]
        encrypted = dstr[config.AES_IV_BITS/8:]
        try:
            aes = AES.new(self._aes_key(secret), config.AES_MODE, self.iv)
        except TypeError as e:
            raise error.UnserializeError("Unable to compute body AES key: {0!r}".format(e))

        try:
            decrypted_zdata = aes.decrypt(encrypted)
        except ValueError as e:
            raise error.UnserializeError("Body decryption error: {0!r}".format(e))
            
        if len(decrypted_zdata) < (config.AES_BLOCK_BITS/8):
            raise error.UnserializeError("Padded compressed body too short ({0})".format(len(decrypted_zdata)))

        try:
            unpadded_zdata = util.unrpad_string_crypto(decrypted_zdata, block_size=config.AES_BLOCK_BITS/8)
        except ValueError as e:
            raise error.UnserializeError("Decryption failed (body data padding invalid): {0!r}".format(e))
            
        try:
            self.data = zlib.decompress(unpadded_zdata)
        except zlib.error as e:
            raise error.UnserializeError("Decrypted compressed data invalid: {0!r}".format(e))

    def _aes_key(self, secret=""):
        """Generate and return AES key (bytes) based on secret."""
        secret = util.cast_str(secret, "Secret phrase")
        secret_hash_256 = hashlib.sha256(secret).digest()
        return secret_hash_256[0:(config.AES_KEY_BITS/8)]

    def _random_iv(self):
        """Generate random RNG-shielded initialization vector bytes."""
        self.iv = hashlib.sha256(os.urandom(config.AES_IV_BITS/8)).digest()[:config.AES_IV_BITS/8]


# ----------------------------------------------------------------------------


#
# Protocol Envelope
#


class Envelope(object):
    """Protocol envelope wrapping header, body, footer."""

    VARIANT       = "A"
    
    def __init__(self, secret=""):
        self.header = Header()
        self.body = Body()
        self.footer = Footer()

    @classmethod
    def from_serialized(cls, encstr, secret=""):
        """Construct and return new object by unserializing string. Raise UnserializeError on errors."""
        o = Envelope()
        o.unserialize(encstr, secret=secret)
        return o

    def serialize(self, secret=""):
        """Serialize self into string and return. Raise SerializeError on errors."""
        if secret == "":
            raise error.SerializeError("No secret specific for envelope serialization")

        # Serialize body and calc/store HMAC in header:
        s_body = self.body.serialize(secret=secret)
        try:
            self.header.body_hmac = self.header.compute_body_hmac(s_body, secret=secret)
        except TypeError as e:
            raise error.SerializeError("Unable to compute body HMAC: {0!r}".format(e))
        
        # Serialize remainder:
        s_header = self.header.serialize()
        s_footer = self.footer.serialize()
        
        # Combine and return:
        envelope = "{h}{b}{f}".format(h=s_header, b=s_body, f=s_footer)
        return envelope

    def unserialize(self, encstr, secret=""):
        """Unserialize string into self. Raise UnserializeError on errors."""
        if not isinstance(encstr, basestring):
            raise TypeError("Envelope can only unserialize from strings, but {0} given".format(type(encstr)))
        if secret == "":
            raise error.UnserializeError("No secret specific for envelope unserialization")

        # Break envelope into chunks (fixed size header and footer, variable body):
        enc_header = encstr[:Header.LENGTH]
        enc_footer = encstr[-Footer.LENGTH:]
        enc_body = encstr[Header.LENGTH:-Footer.LENGTH]

        # Unserialize header and verify HMAC against computed body HMAC:
        self.header.unserialize(enc_header)
        try:
            body_hmac = self.header.compute_body_hmac(enc_body, secret=secret)
        except TypeError as e:
            raise error.UnserializeError("Unable to compute body HMAC: {0!r}".format(e))
        if self.header.body_hmac != body_hmac:
            raise error.DataTamperedError("Body HMAC ({0!r}) does not match header's ({1!r}).".format(body_hmac, self.header.body_hmac))

        # Unserialize and verify remainder:
        self.body.unserialize(enc_body, secret=secret)
        self.footer.unserialize(enc_footer)


