#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2011, Jussi Judin
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
# 3. Neither the name of the authors nor the names of its contributors
#    may be used to endorse or promote products derived from this software
#    without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS
# OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED
# AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY
# WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

"""python-libguess is a Python wrapper for libguess.

libguess enables finding out in what encoding some text is for
given language. This library is especially useful for short text strings
that themselves don't carry reliable encoding information, like ID3
tags in MP3 files. For example we can encode the same Japanese string
in 3 different encodings (UTF-8, SHIFT-JIS, EUC-JP) and libguess will
hopefully guess the encoding correctly just by looking at the first
few bytes of the given string.

You can also use this as a regular command line program by giving
region as the first parameter and possible target files after that:

  Usage: python -m guess REGION [INPUT_FILE]

  If input file name is not given, this program reads from the standard input.
"""

import ctypes
import optparse
import sys

_VERSION = "1.1"

# These region names are currently known while writing this wrapper library.
_REGIONS = (
    ('REGION_JP', "japanese"),
    ('REGION_TW', "taiwanese"),
    ('REGION_CN', "chinese"),
    ('REGION_KR', "korean"),
    ('REGION_RU', "russian"),
    ('REGION_AR', "arabic"),
    ('REGION_TR', "turkish"),
    ('REGION_GR', "greek"),
    ('REGION_HW', "hebrew"),
    ('REGION_PL', "polish"),
    ('REGION_BL', "baltic"),
    )
_REGIONS_DICT = dict(_REGIONS)
globals().update(_REGIONS)

_LIBRARY_NAME = "NO-LIBRARY-USED"
try:
    _LIBRARY_NAME = "libguess.so.1"
    _LIBRARY = ctypes.cdll.LoadLibrary(_LIBRARY_NAME)
except AttributeError, e:
    # TODO maybe support other other library types than .so?
    raise RuntimeError("Could not find standard C library loader. This system is not supported.")
except OSError, e:
    raise RuntimeError("""Could not find %s. Make sure that you have libguess installed and that it is compiled as dynamic library.""" % _LIBRARY_NAME)


_determine_encoding = _LIBRARY.libguess_determine_encoding
_determine_encoding.argtypes = [ctypes.c_char_p, ctypes.c_int, ctypes.c_char_p]
_determine_encoding.restype = ctypes.c_char_p

def determine_encoding(in_string, region):
    """Determines encoding of a string for the given language region.

    Arguments:
    in_string -- a raw byte string for which encoding needs to be guessed.
    region -- one of the REGION_* constants for which encoding is guessed.

    Returns:
    String value indicating the guessed encoding of in_string argument
    for given region or None if error happened.

    As an usage example we might see what happens when given Japanese
    text in 2 different encodings:

    >>> import guess
    >>> guess.determine_encoding(u'\u3042'.encode('euc-jp'), guess.REGION_JP)
    'EUC-JP'
    >>> guess.determine_encoding(u'\u3042'.encode('utf-8'), guess.REGION_JP)
    'UTF-8'

    The output string of this function can be given directly
    to iconv_open() C function and the resulting names should be
    compatible with the encoding string of str.decode() function:

    >>> encoded_value = u'\u3042'.encode('shift-jis')
    >>> encoding = guess.determine_encoding(encoded_value, guess.REGION_JP)
    >>> encoding
    'SJIS'
    >>> encoded_value.decode(encoding)
    u'\u3042'

    In case the given region name is invalid or the underlying
    libguess_determine_encoding() call fails for any other reason,
    None value is returned:

    >>> encoding = guess.determine_encoding("asdf", "UNKNOWN")
    >>> encoding is None
    True

    Use REGION_* constants for region names.
    """
    str_in_string = str(in_string)
    return _determine_encoding(str_in_string, len(str_in_string), region)


_validate_utf8 = _LIBRARY.libguess_validate_utf8
_validate_utf8.argtypes = [ctypes.c_char_p, ctypes.c_int]
_validate_utf8.restype = ctypes.c_int

def validate_utf8(in_string):
    """Checks if the given string is a valid UTF-8 byte sequence.

    Arguments:
    in_string -- a raw byte string to be inspected for UTF-8 validity.

    Return value:
    True if given string is a valid UTF-8 byte sequence, False otherwise.

    This function is included here for the completeness with libguess
    interface. It gives more precise results for UTF-8 validity than
    for example functions in glib.

    >>> import guess
    >>> guess.validate_utf8(u'\u3042'.encode('EUC-JP'))
    False
    >>> guess.validate_utf8(u'\u3042'.encode('UTF-8'))
    True
    """
    str_in_string = str(in_string)
    return bool(_validate_utf8(str_in_string, len(str_in_string)))


def _main(argv=sys.argv):
    usage = """python -m guess REGION [INPUT_FILE]

If input file name is not given, this program reads from the standard input.

Use '-' to use standard input as input file if you need to specify file name.

Return values:

  0 - everything went OK.
  1 - undefined program error.
  2 - option parser error.
  3 - file could not be opened.
  4 - invalid region name was given."""
    parser = optparse.OptionParser(usage=usage,
                                   version=(u'%%prog %s' % _VERSION))
    args = parser.parse_args(argv[1:])[1]

    if len(args) < 1:
        parser.error("You must give at least the target region!\n\n"
                     "Valid region names are:\n\n"
                     "  %s" % ("\n  ".join(["%s (%s)" % (y, x) for x, y in _REGIONS])))

    if len(args) > 2:
        parser.error("Too many parameters given!")

    # Do not do any checks for region name validity, as underlying
    # libguess might enable more regions that are not listed here.
    region = _REGIONS_DICT.get(args[0], args[0])

    source_file = "-"
    if len(args) == 2:
        source_file = args[1]

    if source_file == "-":
        fp = sys.stdin
    else:
        try:
            fp = open(source_file, "rb")
        except IOError, e:
            sys.stderr.write(str(e) + "\n")
            print ''
            return 3

    data = fp.read()
    fp.close()
    result = determine_encoding(data, region)
    if result is None:
        print ''
        return 4
    else:
        print result
        return 0

if __name__ == "__main__":
    sys.exit(_main())

