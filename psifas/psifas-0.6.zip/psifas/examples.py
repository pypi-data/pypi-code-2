# Copyright 2010 Oren Zomer <oren.zomer@gmail.com>
#
# This file is part of pypsifas.

# pypsifas is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# pypsifas is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with pypsifas.  If not, see <http://www.gnu.org/licenses/>.

"""
Some examples that use Psifas.

After installation, you can use 'from psifas import *'
without specifying every module (see __init__.py).

After installation, you can execute this file by running:
python -m psifas.examples
"""
from psifas_exceptions import *
from utils import *
from base import *
from multifield import *
from arithmetic import *
from repeater import *
from switch import *

try:
    from scapy_wrapper import *
except ImportWarning, w:
    import warnings
    warnings.warn(w)

from functools import wraps

test_functions = []

def test_decorator(func):
    @wraps(func)
    def decorated_func():
        print "**** %s *****" % (func.__name__,)
        try:
            return func()
        except:
            print "!!! test failed on %s !!!" % (func.__name__,)
            raise
        else:
            print "**** %s succeeded ****" % (func.__name__,)
    test_functions.append(decorated_func)
    return decorated_func

@test_decorator
def test_base_constant():
    MY_CONSTANT = Constant(7)
    print "parsing an empty buffer: %r" % (MY_CONSTANT.parse(''),)
    print "building a buffer: %r" % (MY_CONSTANT.build(7),)

@test_decorator
def test_base_segment():
    FIXED_SIZE_SEGMENT = Segment(15)
    print "parsing 'pypsifas.sf.net' using Segment(15): %r" % (FIXED_SIZE_SEGMENT.parse("pypsifas.sf.net"),)
    print "building '!!masterpiece!!' using Segment(15): %r" % (FIXED_SIZE_SEGMENT.build("!!masterpiece!!"),)

@test_decorator
def test_base_leftover():
    LEFTOVER = Leftover()
    print "parsing 'read-until-the-end': %r" % (LEFTOVER.parse("read-until-the-end"),)
    print "building 'write-until-the-end': %r" % (LEFTOVER.build("write-until-the-end"),)

# @test_decorator
# def test_multifield_struct_with_link_to_size():
#     MY_STRUCT = Struct('my_segment', Segment(11),
#                        'my_leftover', Leftover(),
#                        'my_segment_size', Link('my_segment/size'),
#                        'my_leftover_size', Link('my_leftover/size')
#                        )
#     print "parsing 'sourceforgeSoUrCeFoRgE': %r" % (MY_STRUCT.parse('sourceforgeLeFtOvEr'),)
#     my_container = Container(my_segment = 'masterpiece', my_leftover = 'LeFtOvEr')
#     print "building %r:" % (my_container,)
#     print repr(MY_STRUCT.build(my_container))
#     print "the container after the build: %r" % (my_container,)

@test_decorator
def test_multifield_struct_merging_structs():
    OLD_STRUCT = Struct('segment_a', Segment(4),
                        'segment_b', Segment(4))
    EXTENDED_STRUCT = Struct('header', Segment(6),
                             '.', OLD_STRUCT,
                             'sub_container', OLD_STRUCT)
    print "parsing 'HEADerSegASegBabc1ABC2': %r" % (EXTENDED_STRUCT.parse('HEADerSegASegBabc1ABC2'),)
    my_container = Container(header = 'hhhhhh',
                             sub_container = Container(segment_a = '1234',
                                                       segment_b = '4567'),
                             segment_a = 'abcd',
                             segment_b = 'efgh')
    
    print "building %r:" % (my_container,)
    print repr(EXTENDED_STRUCT.build(my_container))

@test_decorator
def test_multifield_struct_weak_struct():
    MY_STRUCT = Struct('choice', UBInt(1),
                       '.', Switch('choice',
                                   {0: Struct('switch_result', Segment(45)),
                                    1: Segment(38)}))
    parse_buffer = "\x00switch result does not override the container"
    print "parsing %r: %r" % (parse_buffer, MY_STRUCT.parse(parse_buffer))
    parse_buffer = "\x01the result does override the container"
    print "parsing %r: %r" % (parse_buffer, MY_STRUCT.parse(parse_buffer))

@test_decorator
def test_arithmetic_ints():
    parse_buf = '\x01\x02\x03\x04'
    for int_class in (UBInt, ULInt):
        print 'testing %s' % (int_class.__name__,)
        for size in xrange(1, 5):
            print "parsing %r with %s(%s): 0x%x" % (parse_buf, int_class.__name__, size, int_class(size).parse(parse_buf, ignore_leftover = True))
            build_number = 0x01020304 & ((1 << (size * 8)) - 1)
            print "building 0x%x with %s(%s): %r" % (build_number, int_class.__name__, size, int_class(size).build(build_number))

@test_decorator
def test_arithmetic_ubint_on_arbitrary_size():
    MY_STRUCT = Struct('my_segment', Segment(5),
                       'to_ubint', UBInt('my_segment'))
    parse_buf = '\x00\x00\x00\x00\x03'
    print "parsing %r: %r" % (parse_buf, MY_STRUCT.parse(parse_buf))
    build_container = Container(to_ubint = 7)
    print "building: %r" % (build_container,)
    print repr(MY_STRUCT.build(build_container))
    print "container after build: %r" % (build_container,)

@test_decorator
def test_base_segment_with_dynamic_size():
    MY_STRUCT = Struct('sizer', UBInt(1),
                       'segment', Segment('sizer'))
    parse_buf = '\x06PaScAl'
    print "parsing %r: %r" % (parse_buf, MY_STRUCT.parse(parse_buf))
    build_container = Container(segment = 'This is a pascal string builder')
    print "building: %r" % (build_container,)
    print repr(MY_STRUCT.build(build_container))
    print "container after build: %r" % (build_container,)

@test_decorator
def test_base_segment_with_dynamic_size_explicit():
    MY_PASCAL = Segment(UBInt(1))
    parse_buf = '\x06PaScAl'
    print "parsing %r: %r" % (parse_buf, MY_PASCAL.parse(parse_buf))
    build_string = 'Explicit pascal string builder'
    print "building: %r" % (build_string,)
    print repr(MY_PASCAL.build(build_string))

@test_decorator
def test_multifield_struct_payload_field_name():
    SUB_STRUCT = Struct('sub_a', UBInt(4),
                        'sub_b', UBInt(2),
                        payload_field_name = 'sub_payload')
    MY_STRUCT = Struct('field_a', Segment(2),
                       'sub_struct', SUB_STRUCT,
                       'field_b', Segment(2))
    parse_buf = 'AB\x00\x00\x00\x01\x00\x02CD'
    print "parsing %r: %r" % (parse_buf, MY_STRUCT.parse(parse_buf))
    build_container = Container(field_a = 'XY',
                                sub_struct = Container(sub_payload = '\x00\x00\x00\x03\x00\x04'),
                                field_b = 'ZW')
    print "building: %r" % (build_container,)
    print repr(MY_STRUCT.build(build_container))
    print "container after build: %r" % (build_container,)

@test_decorator
def test_base_on():
    INNER_STRUCT = Struct('num_a', UBInt(2),
                          'num_b', UBInt(2))
    
    MY_STRUCT = Struct('some_string', Segment(10),
                       '.', INNER_STRUCT.on('some_string', leftover_field_name = 'inner_struct_leftover'))
    # TODO: when using ('a', INNER_STRUCT.on(...)) we need to use '../somestring' and not '.../somestring'
    
    parse_buf = '\x00\x01\x00\x02hello!'
    print "parsing %r: %r" % (parse_buf, MY_STRUCT.parse(parse_buf))
    
    build_container = Container(num_a = 3, num_b = 4, inner_struct_leftover = 'YELLOW')
    # build_container = Container(a = Container(x = '1234567890'))
    print "building: %r" % (build_container,)
    print repr(MY_STRUCT.build(build_container))
    print "container after build: %r" % (build_container,)

@test_decorator
def test_base_copy():
    MY_STRUCT = Struct('my_string', Segment(UBInt(1)),
                       'my_string_size', Copy('my_string/size'))
    parse_buf = '\x06PaScAl'
    print "parsing %r: %r" % (parse_buf, MY_STRUCT.parse(parse_buf))
    build_container = Container(my_string = 'No Idea')
    print "building %r" % (build_container,)
    print repr(MY_STRUCT.build(build_container))
    print "container after build: %r" % (build_container,)

@test_decorator
def test_base_clink():
    """
    In Copy only the value is copied & verifeid.
    In CLink, there shouldn't be other values under the link's name.
    """
    MY_STRUCT = Struct('my_string', Segment(UBInt(1)),
                       'my_string_size', CLink().my_string.size)
    parse_buf = '\x06PaScAl'
    print "parsing %r: %r" % (parse_buf, MY_STRUCT.parse(parse_buf))
    build_container = Container(my_string = 'No Idea')
    print "building %r" % (build_container,)
    print repr(MY_STRUCT.build(build_container))
    print "container after build: %r" % (build_container,)

@test_decorator
def test_multifield_bitfield():
    MY_BIT_FIELD = BitField(UBInt(4),
                            (5, 'lower_bits'),
                            (20, 'middle_bits'),
                            (7, 'upper_bits'))
    parse_buf = '\xFE\x00\x00\x01'
    print "parsing %r: %r" % (parse_buf, MY_BIT_FIELD.parse(parse_buf))
    build_container = Container(lower_bits = 2**5 - 1,
                                middle_bits = 0,
                                upper_bits = 1)
    print "building %r" % (build_container,)
    print repr(MY_BIT_FIELD.build(build_container))

@test_decorator
def test_switch_mappingswitch():
    """
    MappingSwitch is for advanced users.
    See Switch for the normal cases.
    """
    class MyMappingSwitch(MappingSwitch):
        def mapping(self, switch_number):
            if is_abstract(switch_number):
                return super(MyMappingSwitch, self).mapping(switch_number) # NoProcess()
            if switch_number > 0:
                return Segment(switch_number)
            else:
                return Constant(-switch_number)

        def reverse_mapping(self, solution_value):
            if is_abstract(solution_value):
                return Bottom
            if isinstance(solution_value, str):
                return len(solution_value)
            return -solution_value

    MY_STRUCT = Struct('x', SBInt(1),
                       'switch_value', MyMappingSwitch(This.x))
    for parse_buf in ['\x05HeLlO', '\xFF']:
        print "parsing %r: %r" % (parse_buf, MY_STRUCT.parse(parse_buf))

    for build_container in [Container(switch_value = 'lalalala'),
                            Container(switch_value = 128)]:
        print "building %r" % (build_container,)
        print repr(MY_STRUCT.build(build_container))
        print "container after build: %r" % (build_container,)


@test_decorator
def test_switch_switch_of_constants():
    MY_STRUCT = Struct('x', UBInt(1),
                       'y', Switch(This.x, # the This is used because of the hirerchy of 'y'
                                   {1: 'ONE',
                                    2: 'TWO'},
                                   default = 'OTHER'))
    for parse_buf in ['\x01', '\x08']:
        print "parsing %r: %r" % (parse_buf, MY_STRUCT.parse(parse_buf))

    build_container = Container(y = 'TWO')
    print "building %r" % (build_container,)
    print repr(MY_STRUCT.build(build_container))
    print "container after build: %r" % (build_container,)

@test_decorator
def test_switch_switch_of_non_constants():
    """
    In this case, building is not possible.
    Psifas does not have the AI required for solving such complex hueristics.
    """
    MY_STRUCT = Struct('x', Segment(3),
                       '.', Switch('x', # no 'This' here, because we're working in the same hirerchy. you can also use CLink().x
                                   one = Struct('a', UBInt(4)),
                                   two = Struct('a', UBInt(2),
                                                'b', UBInt(2)),
                                   default = Struct('left', Segment(4))))
    for parse_buf in ['one\x00\x01\x00\x02',
                      'two\x00\x01\x00\x02',
                      'zzz\x00\x01\x00\x02']:
        print "parsing %r: %r" % (parse_buf, MY_STRUCT.parse(parse_buf))
        

@test_decorator
def test_switch_enum():
    class MyEnum(Enum):
        ONE = 1
        TWO = 2
        THREE = 3
        # when written in lowercase, the constant must be put
        # inside the "constants" dictionary.
        constants = {'four': 4}

    MY_STRUCT = Struct('a', MyEnum(UBInt(1)),
                       'b', MyEnum(UBInt(2)),
                       'c', MyEnum(UBInt(3)),
                       'd', MyEnum(UBInt(4)))

    parse_buf = '\x01\x00\x02\x00\x00\x03\x00\x00\x00\x04'
    print "parsing %r: %r" % (parse_buf, MY_STRUCT.parse(parse_buf))

    build_container = Container(a = 'four',
                                b = 'TWO',
                                c = 'THREE',
                                d = 'ONE')
    print "building %r" % (build_container,)
    print repr(MY_STRUCT.build(build_container))

@test_decorator
def test_switch_try():
    MY_TRY = Try(Struct('should_be_seven', UBInt(4), Constant(7)),
                 except_psifas = Struct('should_be_seven', Segment(4)),
                 exception_field_name = 'why_not')
    for parse_buf in ['\x00\x00\x00\x07',
                      'waka']:
        print "parsing %r" % (parse_buf,)
        print repr(MY_TRY.parse(parse_buf, ignore_leftover = True))

    for build_container in [Container(should_be_seven = 7),
                            Container(should_be_seven = 'NOT7')]:
        bc = deepcopy(build_container)
        print "building %r" % (bc,)
        print repr(MY_TRY.build(bc))
        # Try stores a deepcopy of the container before it executes
        # and if an exception is raised, it switches to the stored
        # container (the clone). Therefore, the original container
        # will not contain the full building results (from the
        # exception on..)
        # If you really want to check the exceptions raised
        # while building, you can use build_debug()
        print "container after build: %r" % (bc,)

@test_decorator
def test_switch_dynamic():
    MY_DYNAMIC = Struct('endian', Segment(1),
                        'endian_class', Switch(This.endian, B = UBInt, L = ULInt),
                        'value', Dynamic(This.endian_class, 4))
    
    for parse_buf in ['B\x00\x00\x00\x01',
                      'L\x02\x00\x00\x00']:
        print "parsing: %r: %r" % (parse_buf, MY_DYNAMIC.parse(parse_buf))

    for build_container in [Container(endian = 'B', value = 0x100),
                            Container(endian_class = ULInt, value = 0xFF)]:
        print "building %r" % (build_container,)
        print repr(MY_DYNAMIC.build(build_container))
        print "container after build: %r" % (build_container,)
    


@test_decorator
def test_repeater_constant_repeater():
    MY_REPEATER = Repeater(5, UBInt(2))
    parse_buf = "\x00\x01\x00\x02\x00\x03\x00\x04\x00\x05"
    print "parsing %r: %r" % (parse_buf, MY_REPEATER.parse(parse_buf))
    print "building range(4,9): %r" % (MY_REPEATER.build(range(4,9)),)

@test_decorator
def test_repeater_pascal_repeater():
    MY_REPEATER = Repeater(UBInt(1), UBInt(2))
    parse_buf = "\x03\x00\x00\x00\x01\x00\x02"
    print "parsing %r: %r" % (parse_buf, MY_REPEATER.parse(parse_buf))
    print "building xrange(2,9): %r" % (MY_REPEATER.build(xrange(2,9)),)

@test_decorator
def test_repeater_repeat_until_term():
    MY_REPEATER = RepeatUntilTerm(Struct('x', UBInt(2)), This.x > 7)
    parse_buf = "\x00\x01\x00\x02\x00\x10\x00\x01"
    print "parsing %r: %r" % (parse_buf, MY_REPEATER.parse(parse_buf, ignore_leftover = True))
    build_list = [Container(x = 1), Container(x = 2), Container(x = 3), Container(x = 9)]
    print "building %r: %r" % (build_list, MY_REPEATER.build(build_list))

@test_decorator
def test_repeater_repeat_until():
    MY_REPEATER = RepeatUntil(UBInt(2), 0)
    parse_buf = "\x00\x01\x00\x02\x00\x07\x00\x00"
    print "parsing %r" % (parse_buf,)
    print "result: %r" % (MY_REPEATER.parse(parse_buf, ignore_leftover = True),)
    build_list = [1,2,3,9,0]
    print "building %r" % (build_list,)
    print "result: %r" % (MY_REPEATER.build(build_list),)

@test_decorator
def test_repeater_repeat_until_not_including():
    MY_REPEATER = RepeatUntil(UBInt(2), 0, including = False)
    parse_buf = "\x00\x01\x00\x02\x00\x07\x00\x00"
    print "parsing %r: %r" % (parse_buf, MY_REPEATER.parse(parse_buf))
    build_list = [1,1,1,9]
    print "building %r: %r" % (build_list, MY_REPEATER.build(build_list))

@test_decorator
def test_repeater_cstring():
    CSTRING = CString()
    parse_buf = "hello\x00"
    print "parsing %r: %r" % (parse_buf, CSTRING.parse(parse_buf))
    build_buf = "world"
    print "building %r: %r" % (build_buf, CSTRING.build(build_buf))

@test_decorator
def test_repeater_pascal_string():
    PASCAL_STRING = PascalString(sizer_size = 2)
    parse_buf = "\x00\x05hello"
    print "parsing %r: %r" % (parse_buf, PASCAL_STRING.parse(parse_buf))
    build_buf = "world!!!!"
    print "building %r: %r" % (build_buf, PASCAL_STRING.build(build_buf))

@test_decorator
def test_arithmetic_sum():
    MY_STRUCT = Struct('a', UBInt(1),
                       'b', UBInt(2),
                       'c', UBInt(4),
                       'abc_sum', Sum(This.a, This.b, This.c))
    parse_buf = "\x00\x00\x02\x00\x00\x00\x06"
    print "parsing %r: %r" % (parse_buf, MY_STRUCT.parse(parse_buf))
    build_container = Container(a = 1, b = 2, abc_sum = 8)
    print "building: %r" % (build_container,)
    print repr(MY_STRUCT.build(build_container))
    print "container after build: %r" % (build_container,)

@test_decorator
def test_arithmetic_modulosum_on_payload():
    MY_STRUCT = Struct('checksum', UBInt(1), ModuloSum(0x100, Ord(This['.checksum_payload'])),
                       '.', Struct('a', Segment(5),
                                   'b', UBInt(1),
                                   'c', Segment(UBInt(1)),
                                   payload_field_name = '.checksum_payload'))
    parse_buf = "\x93hello\x05\x06pascal"
    print "parsing %r: %r" % (parse_buf, MY_STRUCT.parse(parse_buf))
    build_container = Container(a = "WORLD", b = 7, c = "Auto Complete Checksum!")
    print "building: %r" % (build_container,)
    print repr(MY_STRUCT.build(build_container))
    print "container after build: %r" % (build_container,)

@test_decorator
def test_arithmetic_length_on_payload():
    MY_STRUCT = Struct('length', UBInt(1), Length(Ord(This['.length_payload'])),
                       '.', Struct('a', Segment(5),
                                   'b', UBInt(1),
                                   'c', Segment(UBInt(1)),
                                   payload_field_name = '.length_payload'))
    parse_buf = "\x0dhello\x05\x06pascal"
    print "parsing %r: %r" % (parse_buf, MY_STRUCT.parse(parse_buf))
    build_container = Container(a = "WORLD", b = 7, c = "Auto Complete Length!")
    print "building: %r" % (build_container,)
    print repr(MY_STRUCT.build(build_container))
    print "container after build: %r" % (build_container,)

@test_decorator
def test_arithmetic_negative():
    MY_NUMBER = -UBInt(1)
    parse_buf = '\xFF'
    print "parsing %r: %r" % (parse_buf, MY_NUMBER.parse(parse_buf))
    build_number = -5
    print "building %r: %r" % (build_number, MY_NUMBER.build(build_number))

@test_decorator
def test_arithmetic_invert():
    MY_NUMBER = ~UBInt(1)
    parse_buf = '\x00'
    print "parsing %r: %r" % (parse_buf, MY_NUMBER.parse(parse_buf))
    build_number = -0xF1
    print "building %r: %r" % (build_number, MY_NUMBER.build(build_number))

@test_decorator
def test_arithmetic_reversed():
    MY_REVERSE = Reversed(Segment(UBInt(1)))
    parse_buf = '\x0bhello world'
    print "parsing %r: %r" % (parse_buf, MY_REVERSE.parse(parse_buf))
    build_buf = 'reverse this text'
    print "building %r: %r" % (build_buf, MY_REVERSE.build(build_buf))

@test_decorator
def test_scapy():
    """
    This is a parser and builder for cap files!
    """
    try:
        import scapy.all
    except ImportError:
        print "scapy is not installed - cannot test the scapy wrapper"
        return
    # pcap_header.endian is True iff we're working with big-endian

    pcap_file = 'd4c3b2a1020004000000000000000000ffff000001000000885eb3410dd804003a0100003a010000ffffffffffff000b8201fc4208004500012ca8360000fa11178b00000000ffffffff004400430118591f0101060000003d1d00000000000000000000' \
                '00000000000000000000000b8201fc42000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000' \
                '00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000' \
                '000000000000000000000000000000000000638253633501013d0701000b8201fc4232040000000037040103062aff00000000000000885eb34134d904005601000056010000000b8201fc42000874adf19b0800450001480445000080110000c0a80001' \
                'c0a8000a00430044013422330201060000003d1d0000000000000000c0a8000ac0a8000100000000000b8201fc42000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000' \
                '00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000' \
                '000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000638253633501020104ffffff003a04000007083b0400000c4e330400000e103604c0a80001ff0000000000000000000000000000' \
                '000000000000000000000000885eb3419ce905003a0100003a010000ffffffffffff000b8201fc4208004500012ca8370000fa11178a00000000ffffffff0044004301189fbd0101060000003d1e0000000000000000000000000000000000000000000b' \
                '8201fc42000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000' \
                '00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000' \
                '000000000000638253633501033d0701000b8201fc423204c0a8000a3604c0a8000137040103062aff00885eb341d6ea05005601000056010000000b8201fc42000874adf19b0800450001480446000080110000c0a80001c0a8000a004300440134dfdb' \
                '0201060000003d1e0000000000000000c0a8000a0000000000000000000b8201fc42000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000' \
                '00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000' \
                '000000000000000000000000000000000000000000000000000000000000000000000000638253633501053a04000007083b0400000c4e330400000e103604c0a800010104ffffff00ff0000000000000000000000000000000000000000000000000000'
    pcap_file = pcap_file.decode('hex')

    for scapy_class in (Scapy, ScapyStruct,): 
        print "testing class %s" % (scapy_class.__name__,)
        PCAP_ETHER = Struct('pcap_header', Struct('magic_number', UBInt(4),
                                                  'endian', Switch(This.magic_number,
                                                                   {0xa1b2c3d4: 'BIG',
                                                                    0xd4c3b2a1: 'LITTLE'}),
                                                  'version_major', UInt(This.endian, 2),
                                                  'version_minor', UInt(This.endian, 2),
                                                  'thiszone', SInt(This.endian, 4),
                                                  'sigfigs', UInt(This.endian, 4),
                                                  'snaplen', UInt(This.endian, 4),
                                                  'network', UInt(This.endian, 4), Constant(1)),
                            'packets', RepeatUntilTerm(Struct('_endian', Constant('LITTLE'),
                                                              'ts_sec', UInt(This._endian, 4),
                                                              'ts_usec', UInt(This._endian, 4),
                                                              'incl_len', UInt(This._endian, 4),
                                                              'orig_len', UInt(This._endian, 4),
                                                              'packet', scapy_class(scapy.all.Ether, Segment(This.incl_len)),
                                                              ),
                                                       IsEOF()
                                                       ))
        scapy_class.stop = False
        
        print "parsing the dhcp.pcap file from: http://wiki.wireshark.org/SampleCaptures"
        dhcp_packets = PCAP_ETHER.parse(pcap_file)
        print "header:"
        print dhcp_packets.pcap_header
        print "packets:"
        packets = dhcp_packets.packets
            
        for packet in packets:
            print packet

        print "rebuiding and validating that the result is identical to the original content of dhcp.pcap"
        assert PCAP_ETHER.build(dhcp_packets) == pcap_file, "rebuild failure"
        print "rebuilding succeeded"


def test_all():
    for func in test_functions:
        func()
        print ''

def test_specific(name):
    for func in test_functions:
        if name == func.__name__:
            func()
            break
    else:
        print "test %r not found" % (name,)

if __name__ == "__main__":
    import sys
    import os.path
    sys.path.insert(0, os.path.dirname(__file__))
    
    if len(sys.argv) <= 1:
        test_all()
    else:
        for name in sys.argv[1:]:
            test_specific(name)


