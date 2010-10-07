import unittest
import os
from any2fixed import Any2Fixed, FieldMappingError, FieldLenError

def renderer_field1(value):
    vlen = len(value)
    if vlen > 12:
        raise FieldLenError("Field 1 length %s is more than 12" % vlen)

    return "%12s" % value

def renderer_field2(value):
    import decimal
    return '%012.2f' % decimal.Decimal('10.2047842'
            ).quantize(decimal.Decimal('0.01'))

def renderer_field3(value):
    vlen = len(value)
    if vlen > 15:
        raise FieldLenError("Field 1 length %s is more than 15" % vlen)

    return "%15s" % value

class TestAny2Fixed(unittest.TestCase):
    
    def setUp(self):
        class Foo(object):
            def __init__(self, value):
                self.field1 = 'foo1_%s' % value
                self.field2 = 'foo1_%s' % value

        class Bar(object):
            def __init__(self, value):
                self.field1 = 'bar1_%s' % value
                self.field2 = 'bar2_%s' % value
                self.foo = Foo(value)

        class Dummy(object):
            def __init__(self, value):
                self.field1 = 'dummy1_%s' % value
                self.field2 = 'dummy2_%s' % value
                self.bar = Bar(value)

        class ErrorObject(object):
            def __init__(self):
                self.field1 = 'AZERTYUIOPQSDFGHJ'
                self.field2 = 'KLMWXCVBN?.//////'

        self.foo_list = [Foo('d1'), Foo('d2'), Foo('d3'), Foo('d4')]
        self.bar_list = [Bar('b1'), Bar('b2'), Bar('b3'), Bar('b4')]
        self.dummy_list = [Dummy('r1'), Dummy('r2'), Dummy('r3'), Dummy('r4')]
        self.error_list = [ErrorObject(), ErrorObject()]

    def tearDown(self):
        try:
            os.unlink('test/test.txt')
        except:
            pass

    def test_instanciation(self):
        any2fixed = Any2Fixed(
                target_filename='test/test.txt',
                field_mappings=[
                    {'attr':'field1', 'fieldname':'field 1'},
                    {'attr':'field2', 'fieldname':'field 2'},
                    ])
                
        assert isinstance(any2fixed, Any2Fixed)


    def test_write_simple_fixed_with_renderer(self):

        any2fixed = Any2Fixed(
                target_filename='test/test.txt',
                field_mappings=[
                    {'attr':'field1', 'fieldname':'field 1', 'renderer':renderer_field1},
                    {'attr':'field2', 'fieldname':'field 2', 'renderer':renderer_field2},
                    ])

        any2fixed.write(self.foo_list)

        require = [
                '     foo1_d1000000010.20\n',
                '     foo1_d2000000010.20\n',
                '     foo1_d3000000010.20\n',
                '     foo1_d4000000010.20\n',
                ]
        
        result = open('test/test.txt').readlines()
        print require
        print result
        assert require == result

    def test_write_simple_txt_with_sub_object(self):
        any2fixed = Any2Fixed(
                target_filename='test/test.txt',
                field_mappings=[
                    {'attr':'foo.field1', 'fieldname':'field 1', 'renderer':renderer_field1},
                    {'attr':'field2', 'fieldname':'field 2', 'renderer':renderer_field2},
                    ])

        any2fixed.write(self.bar_list)

        # here we also test the default line separator
        require = '     foo1_b1000000010.20\r\n     foo1_b2000000010.20\r\n     foo1_b3000000010.20\r\n     foo1_b4000000010.20\r\n'
        
        # read the file in binary format to make sure
        # we can compare the line separators
        result = open('test/test.txt', 'rb').read()
        print "%s" % repr(require)
        print "%s" % repr(result)
        assert require == result

    def test_write_simple_txt_with_sub_double_level_object(self):
        any2fixed = Any2Fixed(
                target_filename='test/test.txt',
                field_mappings=[
                    {'attr':'field1', 'fieldname':'field1', 'renderer':renderer_field1},
                    {'attr':'bar.field2', 'fieldname':'field2', 'renderer':renderer_field2},
                    {'attr':'bar.foo.field1', 'fieldname':'field3', 'renderer':renderer_field3},
                    ])

        any2fixed.write(self.dummy_list)

        require = [
                '   dummy1_r1000000010.20        foo1_r1\n',
                '   dummy1_r2000000010.20        foo1_r2\n',
                '   dummy1_r3000000010.20        foo1_r3\n',
                '   dummy1_r4000000010.20        foo1_r4\n']
        
        result = open('test/test.txt').readlines()
        print require
        print result
        assert require == result

    def test_complex_1(self):

        any2fixed = Any2Fixed(
                target_filename='test/test.txt',
                field_mappings=[
                    {'attr':'field1', 'fieldname':'field1', 'renderer':renderer_field1},
                    {'fieldname':'field2', 'renderer':u'23'},
                    {'fieldname':'field3', 'attr':'bar.foo.field1', 'renderer':renderer_field3},
                    {'fieldname':'field4', 'renderer':u'Hello World !!!'}
                    ])

        any2fixed.write(self.dummy_list)
        require = [
                '   dummy1_r123        foo1_r1Hello World !!!\n',
                '   dummy1_r223        foo1_r2Hello World !!!\n',
                '   dummy1_r323        foo1_r3Hello World !!!\n',
                '   dummy1_r423        foo1_r4Hello World !!!\n'
                ]
        
        result = open('test/test.txt').readlines()
        print require
        print result
        assert require == result

    def test_error_1(self):
        error_found = False
        try:
            any2fixed = Any2Fixed(
                target_filename='test/test.txt',
                field_mappings=[
                    {'fieldname':'field4'}
                    ])
            any2fixed.write(self.dummy_list)

        except FieldMappingError, e:
            error_found = True

        assert error_found == True

    def test_error_2(self):
        error_found = False
        try:
            any2fixed = Any2Fixed(
                target_filename='test/test.txt',
                field_mappings=[
                    {'renderer':'field1'}
                    ])
            any2fixed.write(self.dummy_list)

        except FieldMappingError, e:
            error_found = True

        assert error_found == True

    def test_error_3(self):
        def foo(param):
           return param

        error_found = False
        try:
            any2csv = Any2Fixed(
                target_filename='test/test.txt',
                field_mappings=[
                    {'fieldname':'field1', 'renderer':foo}
                    ])
            any2fixed.write(self.dummy_list)

        except FieldMappingError, e:
            error_found = True

        assert error_found == True

    def test_overlength_error(self):
        error_found = False

        any2fixed = Any2Fixed(
                target_filename='test/test.txt',
                field_mappings=[
                    {'attr':'field1', 'fieldname':'field 1', 'renderer':renderer_field1},
                    {'attr':'field2', 'fieldname':'field 2', 'renderer':renderer_field2},
                    ])

        try:
            any2fixed.write(self.error_list)
        except FieldLenError, e:
            error_found = True

        assert error_found == True
    
