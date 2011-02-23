#!/usr/bin/env python


## Module byteformat.py
##
## Copyright (c) 2011 Steven D'Aprano.
##
## Permission is hereby granted, free of charge, to any person obtaining
## a copy of this software and associated documentation files (the
## "Software"), to deal in the Software without restriction, including
## without limitation the rights to use, copy, modify, merge, publish,
## distribute, sublicense, and/or sell copies of the Software, and to
## permit persons to whom the Software is furnished to do so, subject to
## the following conditions:
##
## The above copyright notice and this permission notice shall be
## included in all copies or substantial portions of the Software.
##
## THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
## EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
## MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
## IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
## CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
## TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
## SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.


"""Format numbers of bytes in standards-compliant human-readable units, with
support for SI decimal units, IEC binary units, and classic units mixing
decimal prefixes with binary values.

Using byteformat as a Python library:

>>> from byteformat import ByteFormatter
>>> format = ByteFormatter()
>>> format(23500000000)
'23.5 GB'

And as a command line application:

$ python -m byteformat 23500000000
23.5 GB

For further information about using byteformat as a command line application,
call ``python -m byteformat --help``.


Schemes
=======

Bytes can be formatted as human-readable strings according to three standard
schemes. These schemes include two official standards, and one unofficial
de facto standard:

(1) The decimal SI units KB, MB, etc., based on powers of 1000. This official
    standard is frequently used by hard drive manufacturers for reporting
    disk capacity.

(2) The binary units KiB, MiB, etc., based on powers of 1024. This standard
    was proposed by IEC and has been accepted by a number of standards
    organisations around the world including NIST.

(3) The names of decimal units KB, MB, etc., combined with the values of the
    binary units based on powers of 1024. This de facto standard clashes
    with the SI standard for unit prefixes, but as of 2011 it is still in
    common use by memory manufacturers for reporting memory capacity.

See http://en.wikipedia.org/wiki/Binary_prefix for more information.

"""

from __future__ import division


__version__ = "0.1a"
__date__ = "2011-02-22"
__author__ = "Steven D'Aprano"
__author_email__ = "steve+python@pearwood.info"



# === Scheme and style names ===

SCHEMES = ('SI', 'IEC', 'CLASSIC')
SI, IEC, CLASSIC = SCHEMES

# Aliases for scheme names:
ALIASES = {'DECIMAL': SI, 'BINARY': IEC}

STYLES = ('SHORT', 'ABBREV', 'LONG')
SHORT, ABBREV, LONG = STYLES

if __debug__:
    for scheme in SCHEMES:
        assert scheme.isupper()
    for key, value in ALIASES.items():
        assert key.isupper() and value.isupper()
    for style in STYLES:
        assert style.isupper()
    del scheme, key, value, style



# === Unit prefixes ===

# For powers of ten (SI units) and classic powers of two:
PREFIXES = ['', 'K', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y']
LONG_PREFIXES = ['', 'kilo', 'mega', 'giga', 'tera',
                     'peta', 'exa', 'zetta', 'yotta']

# For new-style powers of two (IEC):
PREFIXES2 = ['', 'Ki', 'Mi', 'Gi', 'Ti', 'Pi', 'Ei', 'Zi', 'Yi']
LONG_PREFIXES2 = ['', 'kibi', 'mebi', 'gibi', 'tebi',
                      'pebi', 'exbi', 'zebi', 'yobi']

if __debug__:
    for prefix in (PREFIXES, LONG_PREFIXES, PREFIXES2, LONG_PREFIXES2):
        assert len(prefix) == 9
    del prefix



# === Byte formatter class ===

class ByteFormatter(object):
    """ByteFormatter([scheme]) -> formatter object

    Convert an integer number of bytes into a human-readable string.

    >>> format = ByteFormatter()
    >>> format(25000)
    '25 KB'

    By default the number is formatted in SI units. You can choose another
    scheme from these case-insensitive values:

    Scheme      Description                         Example
    ----------  ----------------------------------  -------------------
    'SI'        Use decimal SI units (default)      1000 bytes = 1 KB
    'IEC'       Use binary units                    1024 bytes = 1 KiB
    'classic'   Use SI units with binary values     1024 bytes = 1 KB
    'decimal'   Alias for 'SI'.
    'binary'    Alias for 'IEC'.

    The ByteFormatter class is optionally initialised with a scheme. If no
    scheme is given, SI units are used:

    >>> format = ByteFormatter('classic')
    >>> format(45097156608)
    '42 GB'

    You can change the scheme in use with the ``scheme`` attribute:

    >>> format.scheme = 'binary'
    >>> format(45097156608)
    '42 GiB'
    >>> format.scheme = 'decimal'
    >>> format(45097156608)
    '45.1 GB'


    Unit prefixes
    =============

    By default, the ByteFormatter instance will select the best unit to use
    for the given number of bytes. To force a specific unit, pass the unit
    prefix you want:

    >>> format(1000000)
    '1 MB'
    >>> format(1000000, prefix='K')
    '1000 KB'

    Valid prefixes are as follows:

    Prefix      Name                        Value
    ----------  --------------------------  --------------------
    '?'         N/A                         Auto-selected
    ''          bytes                       1
    'B'         bytes                       1
    'K'         kilobytes or kibibytes      1000 or 1024
    'M'         megabytes or mebibytes      1000**2 or 1024**2
    'G'         gigabytes or gibibytes      1000**3 or 1024**3
    'T'         terabytes or tebibytes      1000**4 or 1024**4
    'P'         petabytes or pebibytes      1000**5 or 1024**5
    'E'         exabytes or exbibytes       1000**6 or 1024**6
    'Z'         zettabytes or zebibytes     1000**7 or 1024**7
    'Y'         yottabytes or yobibytes     1000**8 or 1024**8

    All prefixes are case-insensitive.


    Display styles
    ==============

    Numbers can be formatted in three styles:

    Style           Example
    --------------  --------------------
    'short'         '45.25 MB'
    'abbrev'        '45.25 Mbytes'
    'long'          '45.25 megabytes'

    Styles are case-insensitive.

    Pass the style to the ByteFormatter instance when calling it:

    >>> format(1000000, style='long')
    '1 megabyte'


    Customisation
    =============

    The formatted strings can be futher customised by modifying these
    ByteFormatter attributes:

    Attribute           Description
    ------------------  -------------------------------------------
    baseunit            Change the name and symbol from "byte".
    decimal_places      Set the number of decimal places.
    exact_ints          Control display of exact integers.
    strict_si           Control the kilo- prefix (SI scheme only).
    template            Control overall format.


    baseunit
    --------

    The ``baseunit`` attribute is a pair of strings representing the base
    unit (i.e. bytes) used for the short style, together with that used for
    the abbrev and long styles. The default value is ('B', 'byte').

    To use ByteFormatter to display values in bits, you can change the
    baseunit. E.g. to format one million bytes using bits as the unit:

    >>> format = ByteFormatter()
    >>> format.baseunit = ('b', 'bit')
    >>> format(1000000*8, style='abbrev')
    '1 Mbit'

    (Note that ByteFormatter has no concept that there are eight bits in a
    byte. It will format whatever value you give it.)


    decimal_places
    --------------

    By default, ByteFormatter displays values to one decimal place. To
    change the number of places, set the ``decimal_places`` attribute to
    an integer.

    >>> format = ByteFormatter()
    >>> format.decimal_places = 3
    >>> format(1024)
    '1.024 KB'


    exact_ints
    ----------

    By default, ByteFormatter suppresses the fraction portion of exact
    integer values, e.g. '42 KB' rather than '42.0 KB'. To always show
    the fraction part, set ``exact_ints`` to False.

    >>> format(1000)
    '1 KB'
    >>> format.exact_ints = False
    >>> format(1000)
    '1.000 KB'


    strict_si
    ---------

    The SI standard specifies that the symbol for the kilo- prefix is written
    as a lowercase k, not uppercase. By default, ByteFormatter uses uppercase
    K, which is a violation of the standard but the conventional practice. To
    strictly follow the standard, set the ``strict_si`` attribute to True.

    >>> format.strict_si = True
    >>> format(2068)
    '2.068 kB'


    template
    --------

    The ``template`` attribute controls the overall display string. It must be a
    string containing exactly two %s formatting targets, the first (left-most)
    being taking the numeric value as a string, and the second (right-most) being
    the unit as a string.

    Other than that restriction, ``template`` can be any string. E.g. to format
    the number of bytes as a data transfer rate in bytes per second:

    >>> format = ByteFormatter()
    >>> format.template = '%s %s/sec'
    >>> format(2000000)
    '2 MB/sec'

    """
    baseunit = ('B', 'byte')
    decimal_places = 1
    exact_ints = False
    strict_si = False
    template = "%s %s"

    def __init__(self, scheme=SI, style=SHORT):
        self.scheme = scheme
        self._style = style

    def __call__(self, bytes, prefix='?', style=None):
        if bytes < 0:
            sgn = 1
            bytes = abs(bytes)
        else:
            sgn = 0
        if prefix == '?':
            prefix = self.choose_prefix(bytes)
        if style is None:
            style = self._style
        size = self.lookup(prefix)
        value = bytes/size
        s1 = self.format_value(value, sgn)
        s2 = self.format_prefix(prefix, style, plural=(value > 1))
        return self.template % (s1, s2)

    def choose_prefix(self, bytes):
        """Find the best prefix for the given number of bytes.

        >>> ByteFormatter().choose_prefix(3000)
        'K'

        Searches the table for the largest prefix not larger than bytes, and
        returns that prefix.
        """
        prefix = ''
        for u, size in self.table:
            if size <= bytes:
                prefix = u
            else: break
        return prefix

    def lookup(self, prefix):
        """Return the number of bytes associated with a particular prefix.

        >>> instance = ByteFormatter('SI')
        >>> instance.lookup('K')
        1000
        >>> instance.scheme = 'IEC'
        1024

        """
        prefix = prefix.upper()
        if prefix == 'B': prefix = ''
        for u, size in self.table:
            if u == prefix: return size
        raise ValueError('unrecognised prefix % "%s"' % prefix)

    def format_value(self, value, sgn):
        if not self.exact_ints and value == int(value):
            # Drop the decimal point and show no decimal places.
            s = "%d" % value
        else:
            s = "%.*f" % (self.decimal_places, value)
        if sgn: s = "-" +s
        return s

    def get_baseunit(self, style, plural):
        savearg, style = style, style.upper()
        if style not in STYLES:
            raise ValueError('bad style "%s"' % savearg)
        s = 's' if plural else ''
        if style == SHORT:
            return self.baseunit[0] + s
        else:
            return self.baseunit[1] + s

    def format_short(self, prefix, plural):
        # Like KB or KiB.
        B = self.get_baseunit(SHORT, plural)
        if self.scheme == IEC:
            p = PREFIXES.index(prefix)
            return PREFIXES2[p] + B
        if self.scheme == SI and prefix == 'K' and self.strict_si:
            prefix = 'k'
        return prefix + B

    def format_abbrev(self, prefix, plural):
        # Like Kbyte or Kibyte.
        B = self.get_baseunit(ABBREV, plural)
        if self.scheme == IEC:
            p = PREFIXES.index(prefix)
            return PREFIXES2[p] + B
        if self.scheme == SI and prefix == 'K' and self.strict_si:
            prefix = 'k'
        return prefix + B

    def format_long(self, prefix, plural):
        # Like kilobyte.
        B = self.get_baseunit(LONG, plural)
        p = PREFIXES.index(prefix)
        if self.scheme == IEC:
            return LONG_PREFIXES2[p] + B
        else:
            return LONG_PREFIXES[p] + B

    _DISPATCH = {SHORT: format_short, LONG: format_long,
                 ABBREV: format_abbrev}

    def format_prefix(self, prefix, style, plural):
        if prefix not in PREFIXES:
            raise ValueError('bad prefix "%s"' % unit)
        func = self._DISPATCH.get(style.upper())
        if func is None:
            raise ValueError('bad style "%s"' % style)
        return func(self, prefix, plural)

    # === Properties ===

    def _getscheme(self):
        s = self._scheme
        assert s in SCHEMES
        return s

    def _setscheme(self, scheme):
        scheme = scheme.upper()
        s = ALIASES.get(scheme, scheme)
        if s not in SCHEMES:
            raise ValueError('unknown scheme "%s"' % scheme)
        self._scheme = s
        self._table = None

    scheme = property(_getscheme, _setscheme)

    @property
    def table(self):
        table = self._table
        if table is None:
            base = self.base
            assert base in (1000, 1024)
            table = [(k, base**i) for i,k in enumerate(PREFIXES)]
            self._table = table
        return table

    @property
    def base(self):
        if self.scheme == SI: return 10**3
        else: return 2**10


# === Command line tool support ===

USAGE = 'Usage:\npython -m byteformat [options] [scheme] n [...]'
LONG_VERSION = "byteformat %s %s" % (__version__, __date__)

HELP = __doc__  # FIXME

SHORT_OPTIONS = 'hVtvq'
LONG_OPTIONS = ['help', 'version', 'test', 'verbose', 'quiet']


def setup(args):
    import getopt
    return getopt.getopt(args, SHORT_OPTIONS, LONG_OPTIONS)


def selftest(module=None, verbose=None):
    import doctest
    result = doctest.testmod(module, verbose=verbose)
    if result[1] == 0:
        raise ValueError('no doctests defined, cannot run self-test')
    return result


def get_scheme(args):
    """Get the scheme from the first argument in list args, if present,
    removing it from the argument list.

    >>> args = 'SI 1 2 3'.split()
    >>> get_scheme(args)
    'SI'
    >>> args
    ['1', '2', '3']

    """
    scheme = 'SI'
    if args:
        a = args[0].upper()
        if a in SCHEMES or a in ALIASES:
            scheme = args.pop(0)
    return scheme


def get_style(args):
    """Get the style from the first argument in list args, if present,
    removing it from the argument list.

    >>> args = 'long 1 2 3'.split()
    >>> get_style(args)
    'long'
    >>> args
    ['1', '2', '3']

    """
    style = 'SHORT'
    if args:
        a = args[0].upper()
        if a in STYLES:
            style = args.pop(0)
    return style


def main(argv=None):
    """Run byteformat as a command-line tool."""
    if argv is None:
        import sys
        argv = sys.argv[1:]
    test = verbose = quiet = False
    opts, args = setup(argv)
    for o,a in opts:
        if o in ('-h', '--help'):
            print(HELP)
            return
        elif o in ('-V', '--version'):
            print(LONG_VERSION)
            return
        elif o in ('-t', '--test'):
            test = True
        elif o in ('-v', '--verbose'):
            verbose = True
            quiet = False
        elif o in ('-q', '--quiet'):
            quiet = True
            verbose = False
    assert not (quiet and verbose)
    if test:
        failed, total = selftest(verbose=verbose)
        if not quiet:
            if failed == 0:
                print("Successfully ran %d tests." % total)
        return
    scheme = get_scheme(args)
    style = get_style(args)
    if not args:
        print(USAGE)
        return 1
    formatter = ByteFormatter(scheme, style)
    args = map(float, args)
    for arg in args:
        print(formatter(arg))
    return


if __name__ == '__main__':
    import sys
    sys.exit(main())

