import tempita
from PIL import Image
from StringIO import StringIO
from dateutil.tz import tzutc
from dateutil.parser import parse as dateutil_parse
from datetime import datetime, date
from calendar import day_name
import time
from os.path import basename
from decimal import Decimal
from uuid import uuid4
import re
import string
from webhelpers.html import literal, tags
import logging

log = logging.getLogger( __name__ )
if not logging.root.handlers:
    logging.basicConfig()
log.setLevel( logging.DEBUG )

def date_parse( str_or_datetime ):
    return ( str_or_datetime
              if isinstance( str_or_datetime,
                             datetime )
                  or str_or_datetime is None
              else dateutil_parse( str_or_datetime ))

def is_dst( dt ):
    return ( time.localtime( time.mktime( dt.timetuple()))
                 .tm_isdst )

def s( template,
       *args,
       **kwargs ):
    return tempita.Template( template ).substitute( *args,
                                                    **kwargs )

def xpath_node( node,
                xpath ):
    return node.xpath( xpath )[ 0 ]

def xpath_str( node,
               xpath,
               optional=False ):
    if optional:
        if not len( node.xpath( xpath )):
            return None
    return xpath_node( node,
                       xpath ).text

def time_id_int():
    return int( time.time())

def time_id_str():
    return str( time_id_int())

def time_str( dt,
              space=True,
              lower=True ):
    return s( "{{ dt.hour % 12 }}"
               "{{if dt.minute }}"
                   ":{{ dt.strftime( '%M' ) }}"
               "{{endif}}"
               "{{if space }}"
                   " "
               "{{endif}}"
               "{{if lower }}"
                   "{{ dt.strftime( '%p' ).lower() }}"
               "{{else}}"
                   "{{ dt.strftime( '%p' ) }}"
               "{{endif}}",
              dt=dt,
              space=space,
              lower=lower )

def date_str( dt,
              smusher="/",
              weekday=True,
              year_opt=True,
              time_space=True,
              time_lower=True ):
   return s( "{{if weekday }}"
                  "{{ dt.strftime( '%A' ) }}"
                  "{{if not smusher }}"
                      ","
                  "{{endif}}"
                  " "
              "{{endif}}"
              "{{if smusher }}"
                  "{{ dt.month }}{{ smusher }}"
              "{{else}}"
                  "{{ dt.strftime( '%B' ) }} "
              "{{endif}}"
              "{{ dt.day }}"
              "{{if not year_opt or dt.year != now.year }}"
                  "{{if smusher }}"
                      "{{ smusher }}{{ dt.strftime( '%y' ) }}"
                  "{{else}}"
                      ", {{ dt.year }}"
                  "{{endif}}"
              "{{endif}}"
              " at {{ time_str }}",
             weekday=weekday,
             dt=dt,
             smusher=smusher,
             now=now(),
             year_opt=year_opt,
             time_str=time_str( dt,
                                space=time_space,
                                lower=time_lower ))

def scale_image( image_data,
                 scale ):
    def _scaled( this,
                 other ):
        return this * scale / other
    def _dimensions( image ):
        return (( _scaled( image.size[ 0 ],
                           image.size[ 1 ] ),
                  scale )
                 if image.size[ 1 ] >
                     image.size[ 0 ]
                 else ( scale,
                         _scaled( image.size[ 1 ],
                                  image.size[ 0 ] )))

    image = Image.open( StringIO( image_data ))
    ret = StringIO()
    image.resize( _dimensions( image )).save( ret,
                                              image.format )
    return ret.getvalue()

class Ago( object ):
    def __init__( self,
                  dt ):
        if isinstance( dt,
                       basestring ):
            dt = date_parse( dt )
        delta = datetime.now( tzutc()) - dt
        self.year = delta.days / 365
        self.month = delta.days / 30
        self.day = delta.days
        self.hour = delta.seconds / 3600
        self.minute = delta.seconds / 60
        self.second = delta.seconds

    def __str__( self ):
        return self.format()

    def format( self ):
        for period in ( 'year',
                        'month',
                        'day',
                        'hour',
                        'minute',
                        'second' ):
            num = getattr( self,
                           period )
            if num > 0 or period == "second":
                return s( "{{ num }} {{ period }}{{ plural }} ago",
                          num=num,
                          period=period,
                          plural="s" if num > 1 or num == 0 else "" )

class Duration( object ):
    def __init__( self,
                  seconds ):
        seconds = int( seconds )
        self.hours, seconds = divmod( seconds, 3600 )
        self.minutes, self.seconds = divmod( seconds, 60 )

    def __str__( self ):
        return self.format()

    def format( self ):
        return s( "{{if d.hours}}"
                      """{{ d.hours }}:{{ "%02d" % d.minutes }}"""
                  "{{else}}"
                      "{{ d.minutes }}"
                  "{{endif}}"
                  """:{{ "%02d" % d.seconds }}""",
                  d=self )

def cleanup_filename( filename ):
    return basename( filename.replace( "\\",
                                       "/" )
                             .replace( " ",
                                       "" ))

class grouped( object ):
    def __init__( self,
                  it,
                  num ):
        self.it = iter( it )
        self.num = num
    def __iter__( self ):
        return self
    def next( self ):
        item = self.it.next()
        return self._grouper( item )
    def _grouper( self,
                  item ):
        yield item
        for i in xrange( self.num - 1 ):
            yield self.it.next()

def create_or_append( item,
                      obj,
                      attr ):
    if not hasattr( obj,
                    attr ) or getattr( obj,
                                       attr ) is None:
        setattr( obj,
                 attr,
                 [ item ] )
    else:
        getattr( obj,
                 attr ).append( item )

class _Proxy( object ):
    def __init__( self,
                  obj ):
        self._obj = obj
    def __getattr__( self,
                     name ):
        return getattr( self._obj,
                        name )
    _class_cache = {}
    _special_names = ( "__abs__",
                       "__add__",
                       "__and__",
                       "__bool__",
                       "__call__",
                       "__cmp__",
                       "__coerce__",
                       "__contains__",
                       "__delitem__",
                       "__delslice__",
                       "__div__",
                       "__divmod__",
                       "__eq__",
                       "__float__",
                       "__floordiv__",
                       "__ge__",
                       "__getitem__",
                       "__getslice__",
                       "__gt__",
                       "__hash__",
                       "__hex__",
                       "__iadd__",
                       "__iand__",
                       "__idiv__",
                       "__idivmod__",
                       "__ifloordiv__",
                       "__ilshift__",
                       "__imod__",
                       "__imul__",
                       "__int__",
                       "__invert__",
                       "__ior__",
                       "__ipow__",
                       "__irshift__",
                       "__isub__",
                       "__iter__",
                       "__itruediv__",
                       "__ixor__",
                       "__le__",
                       "__len__",
                       "__long__",
                       "__lshift__",
                       "__lt__",
                       "__mod__",
                       "__mul__",
                       "__ne__",
                       "__neg__",
                       "__nonzero__",
                       "__oct__",
                       "__or__",
                       "__pos__",
                       "__pow__",
                       "__radd__",
                       "__rand__",
                       "__rdiv__",
                       "__rdivmod__",
                       "__reduce__",
                       "__reduce_ex__",
                       "__repr__",
                       "__reversed__",
                       "__rfloordiv__",
                       "__rlshift__",
                       "__rmod__",
                       "__rmul__",
                       "__ror__",
                       "__rpow__",
                       "__rrshift__",
                       "__rshift__",
                       "__rsub__",
                       "__rtruediv__",
                       "__rxor__",
                       "__setitem__",
                       "__setslice__",
                       "__str__",
                       "__sub__",
                       "__truediv__",
                       "__xor__",
                       "next" )
    _strip_args = ( "__eq__",
                    "__ne__",
                    "__ge__",
                    "__gt__",
                    "__le__",
                    "__lt__",
                    "__cmp__" )

def _raw( obj ):
    return getattr( obj,
                    "_obj",
                    obj )

def _proxy( obj ):
    def _meth( name ):
        if name in _Proxy._strip_args:
            return ( lambda meth:
                      lambda self,
                             *args,
                             **kwargs:
                       meth( self._obj,
                             *( _raw( arg )
                                 for arg
                                 in args ),
                             **dict(( k,
                                      _raw( v ))
                                     for k,
                                         v
                                     in kwargs.items())))
        else:
            return ( lambda meth:
                      lambda self,
                             *args,
                             **kwargs:
                       meth( self._obj,
                             *args,
                             **kwargs ))

    return type( s( "{{ klass }}Proxy",
                    klass=obj.__class__.__name__ ),
                 ( _Proxy, ),
                 dict(( name,
                        _meth( name )( getattr( obj.__class__,
                                                name )))
                       for name
                       in _Proxy._special_names
                       if hasattr( obj.__class__,
                                   name )))( obj )

def proxy( obj,
           **attrs ):
    pr = _proxy( obj )
    [ setattr( pr,
               key,
               val )
      for key, val
      in attrs.items() ]
    return pr

# from Python Decimal module docs
def moneyfmt( value,
              places=2,
              curr="",
              sep=",",
              dp=".",
              pos="",
              neg="-",
              trailneg="" ):
    q = Decimal( 10 ) ** -places
    sign, digits, exp = value.quantize( q ).as_tuple()
    result = []
    digits = map( str,
                  digits )
    build, next = result.append, digits.pop
    if sign:
        build( trailneg )
    for i in range( places ):
        build( next()
                if digits
                else "0" )
    build( dp )
    if not digits:
        build( "0" )
    i = 0
    while digits:
        build( next())
        i += 1
        if i == 3 and digits:
            i = 0
            build( sep )
    build( curr )
    build( neg
            if sign
            else pos )
    return "".join( reversed( result ))

def day_abbr( day ):
    if isinstance( day,
                   date ):
        day = day.weekday()
    return day_name[ day ][ : 3 ].upper()

today = date.today
now = datetime.now

def today_day():
    return today().weekday()

def today_abbr():
    return day_abbr( today_day())

def day_num( name ):
    for ( num, day ) in enumerate( day_name ):
        if day.lower().startswith( name.lower()):
            return num

class Day( object ):
    def __init__( self,
                  num_or_name ):
        try:
            num = int( num_or_name )
        except ValueError:
            num = day_num( num_or_name )
        try:
            self.name = day_name[ num ]
        except IndexError:
            self.name = "Every Day"
        self.num = num
        self.today = today_day() == self.num
    def __eq__( self,
                other ):
        return self.id == other.id
    def __str__( self ):
        return self.name

def today_Day():
    return Day( today_day())

written_ints = ( "zero",
                 "one",
                 "two",
                 "three",
                 "four",
                 "five",
                 "six",
                 "seven",
                 "eight",
                 "nine",
                 "ten",
                 "eleven",
                 "twelve",
                 "thirteen",
                 "fourteen",
                 "fifteen",
                 "sixteen",
                 "seventeen",
                 "eighteen",
                 "nineteen",
                 "twenty",
                 "twenty-one",
                 "twenty-two",
                 "twenty-three",
                 "twenty-four",
                 "twenty-five" )

def rfc3339_strftime( dt ):
    return dt.strftime( "%Y-%m-%dT%H:%M:%SZ%z" )

def rfc3339_now():
    return rfc3339_strftime( now())

def _total_seconds_diff_from_micro( td,
                                    diff=6 ):
    return (( td.microseconds
               + ( td.seconds
                    + td.days
                       * 24
                       * 3600 )
                  * 10
                     ** 6 )
             / 10
                ** diff )

def total_seconds( td ):
    try:
        return td.total_seconds()
    except AttributeError:
        return _total_seconds_diff_from_micro( td )

def total_milliseconds( td ):
    return _total_seconds_diff_from_micro( td,
                                           3 )

def _stretch( regex ):
    return re.compile( regex.pattern
                        + "$",
                       re.X )

# originally from django.utils.html
def force_unicode( x ):
    if isinstance( x,
                   unicode ):
        return x
    if hasattr( x,
                '__unicode__' ):
        return unicode( x )
    else:
        return unicode( str( x ), encoding="utf-8" )

LEADING_PUNCTUATION  = ( "(",
                         "<",
                         "&lt;" )
TRAILING_PUNCTUATION = ( ".",
                         ",",
                         ")",
                         ">",
                         "\n",
                         "&gt;" )

word_split_re = re.compile( r"(\s+)" )
punctuation_re = re.compile( s( r"""
                                  (?P<lead>
                                    (?:
                                      {{ leading }}
                                    ) *
                                  )
                                  (?P<middle>
                                    . *?
                                  )
                                  (?P<trail>
                                    (?:
                                      {{ trailing }}
                                    ) *
                                  )
                                  $
                                 """,
                                leading="|".join( re.escape( x )
                                                   for x
                                                   in LEADING_PUNCTUATION ),
                                trailing="|".join( re.escape( x )
                                                    for x
                                                    in TRAILING_PUNCTUATION )),
                             re.X )

host_re = re.compile( r"""
                        [\w.-] +
                        \.
                        \w {2,6}
                       """,
                      re.X )

email_re = re.compile( s( r"""
                            \S +
                            @
                            {{ host }}
                           """,
                          host=host_re.pattern ),
                       re.X )

email_re_ = _stretch( email_re )

uri_sans_protocol_re = re.compile( s( r"""
                                        (?P<host>
                                          {{ host }}
                                        )
                                        (?:
                                          :
                                          (?P<port>
                                            \d +
                                          )
                                        ) ?
                                        (?P<path>
                                          /
                                          [\w;/@&+$-.!~*'()%] *
                                        ) ?
                                        (?:
                                          \?
                                          (?P<params>
                                            [\w;/@&+$-.!~*'()%?] *
                                          )
                                        ) ?
                                        (?:
                                          \#
                                          (?P<fragment>
                                            [\w;/@&+$-.!~*'()%] *
                                          )
                                        ) ?
                                       """,
                                      host=host_re.pattern ),
                                   re.X )

uri_sans_protocol_re_ = _stretch( uri_sans_protocol_re )

uri_re = re.compile( s( r"""
                          (?P<protocol>
                            [\w+] +
                          )
                          :
                          //
                          {{ uri_sans_protocol }}
                         """,
                        uri_sans_protocol=uri_sans_protocol_re.pattern ),
                     re.X )

uri_re_ = _stretch( uri_re )

punctuated_uri_re = re.compile( s( r"""
                                     (?P<preceding>
                                       (?:
                                         \s +
                                          | ^
                                       )
                                   #     | \b
                                       (?:
                                         {{ leading }}
                                       ) *
                                     )
                                     (?P<uri>
                                       {{ uri }}
                                     )
                                     (?=
                                       (?:
                                         {{ trailing }}
                                       ) *
                                       (?:
                                         \s +
                                          | $
                                       )
                                   #     | \b
                                     )
                                    """,
                                   uri=uri_re.pattern,
                                   leading="|".join( re.escape( x )
                                                      for x
                                                      in LEADING_PUNCTUATION ),
                                   trailing="|".join( re.escape( x )
                                                       for x
                                                       in TRAILING_PUNCTUATION )),
                                re.X )

punctuated_uri_sans_protocol_re = re.compile( s( r"""
                                                   (?P<preceding>
                                                     (?:
                                                       \s +
                                                        | ^
                                                     )
                                                 #     | \b
                                                     (?:
                                                       {{ leading }}
                                                     ) *
                                                   )
                                                   (?P<uri>
                                                     {{ uri_sans_protocol }}
                                                   )
                                                   (?=
                                                     (?:
                                                       {{ trailing }}
                                                     ) *
                                                     (?:
                                                       \s +
                                                        | $
                                                     )
                                                 #     | \b
                                                   )
                                                  """,
                                                 uri_sans_protocol=uri_sans_protocol_re.pattern,
                                                 leading="|".join( re.escape( x )
                                                                    for x
                                                                    in LEADING_PUNCTUATION ),
                                                 trailing="|".join( re.escape( x )
                                                                     for x
                                                                     in TRAILING_PUNCTUATION )),
                                              re.X )

def to_url( word,
            force=False ):
    word = _raw( word )

    if uri_re_.match( word ):
        return word
    if ( force
          or uri_sans_protocol_re_.match( word )):
        return s( "http://{{ word }}",
                  word=word )
    if email_re_.match( word ):
        return s( "mailto:{{ word }}",
                  word=word )
    return None

def trimmed_word( word,
                  limit=None ):
    return ( s( "{{ start }}...",
                 start=word[ : max( 0,
                                    limit
                                     - 3 ) ] )
               if limit is not None
                   and len( word )
                        > limit
               else word )

def urlized_link( word,
                  url,
                  trim_url_limit=None,
                  class_=()):
    return tags.link_to( trimmed_word( word,
                                       limit=trim_url_limit ),
                         url,
                         class_=tags.css_classes((( "urlized",
                                                    True ), )
                                                  + tuple( class_ )))

def urlize_word( word,
                 trim_url_limit=None,
                 class_=()):
    word = force_unicode( word )
    match = punctuation_re.match( word )
    if not match:
        return word
    ( lead,
      middle,
      trail ) = match.groups()
    url = to_url( middle )
    if not url:
        return word
    return u"".join(( lead,
                      urlized_link( middle,
                                    url,
                                    trim_url_limit=trim_url_limit,
                                    class_=class_ ),
                      trail ))

def urlize( text,
            trim_url_limit=None,
            class_=()):
    """
    Converts any URLs in text into clickable links.

    Links can have trailing punctuation (periods, commas, close-parens)
    and leading punctuation (opening parens) and it'll still do the right
    thing.

    If trim_url_limit is not None, the URLs in link text longer than this limit
    will truncated to trim_url_limit-3 characters and appended with an elipsis.
    """
    return literal( u"".join( urlize_word( word,
                                           trim_url_limit,
                                           class_ )
                               for word
                               in word_split_re.split( force_unicode( text ))))

uri_and_trailing_re = re.compile( s( r"""
                                       (?P<uri>
                                         . +?
                                       )
                                       (?P<trailing>
                                         (?:
                                           {{ trailing }}
                                         ) *
                                       )
                                       $
                                      """,
                                      trailing="|".join( re.escape( x )
                                                          for x
                                                          in TRAILING_PUNCTUATION )),
                                  re.X )

def markdown( text,
              inline=False,
              p_class=None ):
    from sleepy.markdown2 import markdown as _markdown

    def _repl( add_protocol=False ):
        def repl( match ):
            trailed = uri_and_trailing_re.match( match.group( "uri" ))

            return s( "{{ preceding }}{{ link }}{{ trailing }}",
                      preceding=match.group( "preceding" ),
                      link=urlized_link( trailed.group( "uri" ),
                                         trailed.group( "uri" )
                                          if not add_protocol
                                          else s( "http://{{ uri }}",
                                                  uri=trailed.group( "uri" ))),
                      trailing=trailed.group( "trailing" ))

        return repl

    return literal( _markdown( _raw( text ),
                               extras=( "smarty-pants",
                                        "link-patterns" ),
                               inline=inline,
                               p_class=p_class,
                               link_patterns=(( punctuated_uri_re,
                                                _repl(),
                                                False ),
                                              ( punctuated_uri_sans_protocol_re,
                                                _repl( add_protocol=True ),
                                                False ))))

def dictize( seq,
             val=None ):
    if seq is None:
        return dict()
    if isinstance( seq,
                   dict ):
        return seq
    return dict(( x, val )
                 for x
                 in seq )

_unixy_re = re.compile( r""" \r\n
                            | \r """,
                        re.X )

def unixy( text ):
    return _unixy_re.sub( "\n",
                          text )

_detab_re = re.compile( r"""
                          (.*?)
                          \t
                         """,
                        re.X )

def detab( text,
           tab_width=4 ):
    return _detab_re.sub( lambda match:
                           match.group( 1 )
                            + " "
                               * ( tab_width
                                    - len( match.group( 1 ))
                                       % tab_width ),
                          text )

_blank_line_re = re.compile( r"^[ \t]+$",
                               re.M )

