"""
Ax_Handoff Object Wrapper.

Provides high-level support for encodeing/decoding Python objects for handoff.

This module contains the Ax_Handoff class, which is the suggested public 
interface to this library.

Suggested Usage:

  from axonchisel.handoff.object import Ax_Handoff
  
  encstr = Ax_Handoff.encode(obj, secret)
  obj = Ax_Handoff.decode(encstr, secret)

------------------------------------------------------------------------------
Author: Dan Kamins <dos at axonchisel dot net>
Copyright (c) 2011 Dan Kamins, AxonChisel.net
"""


# ----------------------------------------------------------------------------


import json

import axonchisel.handoff.util as util
import axonchisel.handoff.protocol as protocol
import axonchisel.handoff.error as error


# ----------------------------------------------------------------------------


class Ax_Handoff(object):
    """
    High-level wrapper for Ax_Handoff encoding/decoding of JSON-congruent objects.
    
    This class encodes and decodes objects that are "JSON-congruent", which is
    another way of saying objects that have direct JSON equivalents, e.g.
    primarily strings, numbers, bools, and lists and dicts of those primitives.
    
    The encoding is done with a secret pass-phrase and uses highly secure
    modern encryption technology, compression, and filtering, to provide
    a URL-safe tamperproof string that can only be decoded with the same
    secret pass-phrase.
    
    Lower level functionality of this package is available if desired,
    but this module provides the most user-friendly wrapper.
    """
    
    def __init__(self):
        raise NotImplementedError("Abstract Class")
        
    @classmethod
    def encode(cls, obj, secret):
        """
        Encode JSON-congruent object as URL-safe string.
        This method is the complement to decode().
        
        Params:
          obj    :  JSON-congruent object (dict, list, string, number, etc.)
          secret :  Secret pass-phrase string.

        Returns:
          URL-safe encoded string representing data.
        
        Raises:
          error.SerializeError on serialization errors.
        """

        e = protocol.Envelope()

        try:
            e.body.data = json.dumps(obj)
        except TypeError as e:
            raise error.SerializeError("Object not JSON-congruent: {0!r}".format(e))

        encstr = e.serialize(secret=secret)
        return encstr
        
    @classmethod
    def decode(cls, encstr, secret):
        """
        Decode JSON-congruent object from URL-safe string.
        This method is the complement to encode().
        
        Params:
          obj    :  JSON-congruent object (dict, list, string, number, etc.)
          secret :  Secret pass-phrase string.

        Returns:
          URL-safe encoded string representing data.
        
        Raises:
          error.UnserializeError on serialization errors.
        """

        if not isinstance(encstr, basestring):
            raise TypeError("Ax_Handoff can only unserialize from strings, but {0} given".format(type(encstr)))

        e = protocol.Envelope.from_serialized(encstr, secret=secret)

        try:
            obj = json.loads(e.body.data)
        except ValueError as e:
            raise error.UnserializeError("Invalid JSON detected: {0!r}".format(e))

        return obj



