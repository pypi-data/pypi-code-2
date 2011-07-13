"""
python 3.1 module for accessing .dbf tables
"""
# imports
import sys
import codecs
import locale
import datetime
import time
import datetime

from array import array

# utility functions

def translator(frm='', to='', delete='', lstrip='', rstrip='', keep=None):
    if len(to) == 1:
        to = to * len(frm)
    trans = string.maketrans(frm, to)
    if keep is not None:
        allchars = string.maketrans('', '')
        delete = allchars.translate(allchars, keep.translate(allchars, delete)+frm)
    def translate(s):
        s.lstrip(lstrip)
        s.rstrip(rstrip)
        return s.translate(trans, delete)
    return translate

non_int = translator(delete='0123456789', lstrip(' -'))
non_flt = translator(delete='0123456789', lstrip(' -.'))
non_date = translator(delete='0123456789')
non_ascii = translator(delete=''.join[chr(x) for x in range(32, 127)])


ascii = codecs.getencoder('ascii')

# Exceptions, Warnings, and Unusual data values

class Warning(Exception):
    pass
class Bof(Warning):
    "attempted to navigated before first record"
    pass
class Eof(Warning):
    "attempted to navigate past last record"
    pass
class Error(Exception):
    pass
class EmptyTable(Error):
    "no records in table"
    pass
class FieldMissing(Error):
    "field not in table"
    pass
class InvalidValue(Error):
    "data [attempting to be] stored in field invalid"
    pass
class CorruptMemo(Error):
    "problem with memo record or file"
    pass
class Null():
    "value if data item has been set to Null"
    pass
class NotSet(Null):
    "value if data item never initialized"
    pass
Null = Null()
NotSet = NotSet()

# Custom data types

class Bytes():
    "data storage for dbf records"
    __slots__ = ['_data']
    def __new__(cls, size, data=None):
        record = super(Record, cls).__new__(cls)
        record._data = array('B', b' ' * size)
        return record
    def __init__(yo, size, data=None):
        if data is not None:
            if len(data) != len(yo._data):
                raise ValueError("Record instance data should be %d bytes, but received %d" % (len(yo._data), len(data)))
            yo._data[:] = array('B', data)
    def __getitem__(yo, number):
        if isinstance(number, int):
            number = slice(number, number+1, None)
        if number.step is not None:
            raise ValueError('step value not allowed for Record access')
        if isinstance(number, slice):
            return yo._data[number].tostring()
        raise TypeError('Record indices must be integers, not %r' % type(number))
    def __setitem__(yo, number, new_value):
        if isinstance(number, int):
            number = slice(number, number+1, None)
        if not isinstance(number, slice):
            raise TypeError('Record indices must be integers, not %r' % type(number))
        if number.step is not None:
            raise ValueError('step value not allowed for Record access')
        if len(yo._data[number]) != len(new_value):
            raise ValueError('attempted to replace %d bytes with %d bytes' % (len(yo._data[number]), len(new_value)))
        yo._data[number] = array('B', new_value)
    def __repr__(yo):
        return "Bytes(%d, %r)" % (len(yo._data), yo._data.tostring())

version_map = {
        '\x02' : 'FoxBASE',
        '\x03' : 'dBase III Plus',
        '\x04' : 'dBase IV',
        '\x05' : 'dBase V',
        '\x30' : 'Visual FoxPro',
        '\x31' : 'Visual FoxPro (auto increment field)',
        '\x43' : 'dBase IV SQL',
        '\x7b' : 'dBase IV w/memos',
        '\x83' : 'dBase III Plus w/memos',
        '\x8b' : 'dBase IV w/memos',
        '\x8e' : 'dBase IV w/SQL table',
        '\xf5' : 'FoxPro w/memos'}

code_pages = {
        '\x00' : ('ascii', "plain ol' ascii"),
        '\x01' : ('cp437', 'U.S. MS-DOS'),
        '\x02' : ('cp850', 'International MS-DOS'),
        '\x03' : ('cp1252', 'Windows ANSI'),
        '\x04' : ('mac_roman', 'Standard Macintosh'),
        '\x08' : ('cp865', 'Danish OEM'),
        '\x09' : ('cp437', 'Dutch OEM'),
        '\x0A' : ('cp850', 'Dutch OEM (secondary)'),
        '\x0B' : ('cp437', 'Finnish OEM'),
        '\x0D' : ('cp437', 'French OEM'),
        '\x0E' : ('cp850', 'French OEM (secondary)'),
        '\x0F' : ('cp437', 'German OEM'),
        '\x10' : ('cp850', 'German OEM (secondary)'),
        '\x11' : ('cp437', 'Italian OEM'),
        '\x12' : ('cp850', 'Italian OEM (secondary)'),
        '\x13' : ('cp932', 'Japanese Shift-JIS'),
        '\x14' : ('cp850', 'Spanish OEM (secondary)'),
        '\x15' : ('cp437', 'Swedish OEM'),
        '\x16' : ('cp850', 'Swedish OEM (secondary)'),
        '\x17' : ('cp865', 'Norwegian OEM'),
        '\x18' : ('cp437', 'Spanish OEM'),
        '\x19' : ('cp437', 'English OEM (Britain)'),
        '\x1A' : ('cp850', 'English OEM (Britain) (secondary)'),
        '\x1B' : ('cp437', 'English OEM (U.S.)'),
        '\x1C' : ('cp863', 'French OEM (Canada)'),
        '\x1D' : ('cp850', 'French OEM (secondary)'),
        '\x1F' : ('cp852', 'Czech OEM'),
        '\x22' : ('cp852', 'Hungarian OEM'),
        '\x23' : ('cp852', 'Polish OEM'),
        '\x24' : ('cp860', 'Portugese OEM'),
        '\x25' : ('cp850', 'Potugese OEM (secondary)'),
        '\x26' : ('cp866', 'Russian OEM'),
        '\x37' : ('cp850', 'English OEM (U.S.) (secondary)'),
        '\x40' : ('cp852', 'Romanian OEM'),
        '\x4D' : ('cp936', 'Chinese GBK (PRC)'),
        '\x4E' : ('cp949', 'Korean (ANSI/OEM)'),
        '\x4F' : ('cp950', 'Chinese Big 5 (Taiwan)'),
        '\x50' : ('cp874', 'Thai (ANSI/OEM)'),
        '\x57' : ('cp1252', 'ANSI'),
        '\x58' : ('cp1252', 'Western European ANSI'),
        '\x59' : ('cp1252', 'Spanish ANSI'),
        '\x64' : ('cp852', 'Eastern European MS-DOS'),
        '\x65' : ('cp866', 'Russian MS-DOS'),
        '\x66' : ('cp865', 'Nordic MS-DOS'),
        '\x67' : ('cp861', 'Icelandic MS-DOS'),
        '\x68' : (None, 'Kamenicky (Czech) MS-DOS'),
        '\x69' : (None, 'Mazovia (Polish) MS-DOS'),
        '\x6a' : ('cp737', 'Greek MS-DOS (437G)'),
        '\x6b' : ('cp857', 'Turkish MS-DOS'),
        '\x78' : ('cp950', 'Traditional Chinese (Hong Kong SAR, Taiwan) Windows'),
        '\x79' : ('cp949', 'Korean Windows'),
        '\x7a' : ('cp936', 'Chinese Simplified (PRC, Singapore) Windows'),
        '\x7b' : ('cp932', 'Japanese Windows'),
        '\x7c' : ('cp874', 'Thai Windows'),
        '\x7d' : ('cp1255', 'Hebrew Windows'),
        '\x7e' : ('cp1256', 'Arabic Windows'),
        '\xc8' : ('cp1250', 'Eastern European Windows'),
        '\xc9' : ('cp1251', 'Russian Windows'),
        '\xca' : ('cp1254', 'Turkish Windows'),
        '\xcb' : ('cp1253', 'Greek Windows'),
        '\x96' : ('mac_cyrillic', 'Russian Macintosh'),
        '\x97' : ('mac_latin2', 'Macintosh EE'),
        '\x98' : ('mac_greek', 'Greek Macintosh') }

class FieldType(tuple):
    def __init__(yo, field_type, retrieve, update, blank, init):
        yo._settings = field_type, retrieve, update, blank, init
    def __getitem__(yo, index):
        return yo._settings[index]
    @property
    def field_type(yo):
        return yo._settings[0]
    @property
    def retrieve(yo):
        return yo._settings[1]
    @property
    def update(yo):
        return yo._settings[2]
    @property
    def blank(yo):
        return yo._settings[3]
    def init(yo):
        return yo._settings[4]

# Mixin class

class navigation_mixin():
    """Mixin class that adds current, bof, eof, first, last, next, prev methods
    expects main class to have data structure _records with list-like behavior
    and method _get_record that, when given an index into _records, returns the actual record"""
    __current = 0
    def current(yo):
        if yo._records and yo.__current > len(yo._records):
            yo.__current = len(yo._records) - 1
        return yo._get_record(yo.__current)
    def bof(yo):
        "True if current record is 1"
        if yo._records and yo.__current > len(yo._records):
            yo.__current = len(yo._records) - 1
        return yo.__current == 1
    def eof(yo):
        "True if current record is last"
        if yo._records and yo.__current > len(yo._records):
            yo.__current = len(yo._records) - 1
        return len(yo._records) - yo.__current == 1
    def first(yo):
        "sets current to first record"
        yo.__current = 0
    def last(yo):
        "sets current to last record"
        yo.__current = len(yo._records) - 1
    def next(yo):
        "sets current to next record; raises Eof if already at last record"
        if yo.eof():
            raise Eof
        yo.__current += 1
    def prev(yo):
        "sets current to previous record; raises Bof if already at first record"
        if yo.bof():
            raise Bof
        yo.__current -= 1

class DbfTable(navigation_mixin):
    def __init__(yo, ):
        pass

class _Record():
    """Record layout
       name C(40)       -- 0:40
       age N(3,0)       -- 40:43
       male L           -- 43:44
       income N(9,2)    -- 44:53
       birthdate D      -- 53:61
       lifestory M      -- 61:71
       """
    __slots__ = ['_data', '_number', '_master', '__weakref__']
    decoder = codecs.getdecoder('cp1252')
    encoder = codecs.getencoder('cp1252')

    def __new__(cls, data, recnum, master):
        record = super(_Record, cls).__new__(cls)
        record._data = Bytes(71, data)
        record._number = recnum
        record._master = master
        return record
    def __getattr__(yo, attr):
        if attr[:2] == attr[2:] == '__':
            return NotImplemented
        raise FieldMissing("Field <%s> not in table" % attr)
    def __str__(yo):
        return repr(yo._data)
    @property
    def name(yo):
        return yo.decoder(yo._data[0:40]).rstrip(' ')
    @name.setter
    def name(yo, new_value):
        try:
            new_value = yo.encoder(new_value).rstrip(b' ')
        except TypeError as e:
            raise InvalidValue("Record %d - <name C(40)>: %s" % (yo._number, e.message))
        try:
            yo._data[0:40] = new_value + b' ' * (40 - len(new_value))
        except ValueError as e:
            raise InvalidValue("Record %d - <name C(40)>: Value %r too big" % (yo._number, new_value))
    @property
    def age(yo):
        data = yo._data[40:43]
        if non_int(data):
            raise InvalidValue("Record %d - <age N(3)>: found invalid value: %r" % (yo._number, data))
        return int(data)
    @age.setter
    def age(yo, new_value): # 1 for sign
        if not -10**2 < new_value < 10**2:       # 2 = number of digits in field - 1 for sign
            raise InvalidValue("Record %d - <age N(3)>: %d too big" % (yo._number, new_value))
        digits = ascii("%3d" % new_value)
        yo._data[40:43] = digits
    @property
    def male(yo):
        if yo._data[43] in ('YyTt'):
            return True
        elif yo._data[43] in ('NnFf'):
            return False
        elif yo._data[43] == '?':
            return NotSet()
        raise InvalidValue("Record %d - <male L>: found invalid value %r" % (yo._number, yo._data[43]))
    @male.setter
    def male(yo, boolean):
        if boolean not in ('Y', 'y', 'T', 't', 'N', 'n', 'F', 'f', 0, 1):
            raise InvalidValue("Attempted to store %s in Logical field" % boolean)
        yo._data[43] = b'T' if boolean in ('Y', 'y', 'T', 't', 1) else b'F'
    @property
    def income(yo):
        data = yo._data[44:53]
        if non_flt(data):
            raise InvalidValue("Record %d - <income N(9,2)>: found invalid value: %r" % (yo._number, data))
        return float(data)
    @income.setter
    def income(yo, new_value):
        if not -10**5 < new_value < 10**5:       # 5 = number of digits in field - 1 for sign - 1 for period - 2 for decimals
            raise InvalidValue("Record %d - <income N(9,2)>: %d too big" % (yo._number, new_value))
        digits = ascii("%6.2f" % new_value)
        yo._data[44:53] = digits
    @property
    def birthdate(yo):
        data = yo._data[53:61]
        if data == b' ' * 8:
            return NotSet
        elif non_date(data):
            raise InvalidValue("Record %d - <birthdate D>: found invalid value: %r" % (yo._number, data))
        return datetime.date(int(data[:4]), int(data[4:6]), int(data[6:]))
    @birthdate.setter
    def birthdate(yo, new_value):
        if new_value.year < 0 or new_value.year > 9999 or \
           new_value.month < 0 or new_value.month > 12 or \
           new_value.day < 0 or new_value.day > 31:
               raise ValueError("Record %d - <birthdate D>: %s-%s-%s" % (yo._number, new_value.year, new_value.month, new_value.day))
        digits = ascii("%04d%02d%02d" % (new_value.year, new_value.month, new_value.day))
        yo._data[53:61] = digits
    @property
    def lifestory(yo):
        block = int(bytes[61:71]) * 512 # block number * block size
        memofile = yo._master._memofile
        memofile.seek(block)
        EOM = False
        data = ''
        while not EOM:
            new_data = memofile.read(512)
            if not new_data:
                raise CorruptMemo("Record %d - <lifestory M>: missing memo-ending ^Z^Z characters" % yo._number)
            data += new_data
            end = data.find('\x1a\x1a')
            EOM = end != -1
        try:
            if data[end+2] == '\x1a':   # was a CTRL-Z the last character of the memo?
                end += 1                #   then return it
        except IndexError:
            new_data = memofile.read(1)
            if new_data and new_data == '\x1a':
                end += 1
        return yo.decoder(data[:end])
    @lifestory.setter
    def lifestory(yo, new_value):
        new_value = yo.encoder(new_value)
        if new_value.find(b'\x1a\x1a') != -1:
            raise CorruptMemo("Record %d - <lifestory M>: attempted to store memo with ^Z^Z characters" % yo._number)
        new_value += b'\x1a\x1a'
        memofile = yo._master._memofile
        blocks = len(new_value) // 512 + bool(len(new_value) % 512)
        memofile.seek(0)
        target = struct.unpack('<L', memofile.read(4))[0]
        memofile.seek(0)
        memofile.write(struct.pack('<L', target + blocks))
        memofile.seek(target * 512)
        memofile.write(new_value)
