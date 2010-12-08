import os
import sys


class Matcher(object):
    """A Matcher encapsulates a value -- a primitive, the result of
    an expression or possibly a callable -- that would later be
    compared to another value.
    
    # It should initialize with primitives, native types and expressions
    >>> e = Matcher("Foo")
    >>> e.actual == "Foo"
    True
    
    >>> e = Matcher(['a', 'b'])
    >>> e.actual == ['a', 'b']
    True
    
    >>> Matcher(4 + 7).actual == 11
    True
    
    >>> Matcher(4 == 7).actual == False
    True
    """
    def __init__(self, value):
        self.actual = value
        
    def to_equal(self, expected):
        msg = "Expected '%s' to equal '%s'" % (self.actual, expected)
        compare(self.actual == expected, True, msg)

    def to_be(self, expected):
        msg = "Expected '%s' to be '%s'" % (self.actual, expected)
        compare(self.actual is expected, True, msg)
       
    def to_be_none(self):
        msg = "Expected '%s' to be 'None'" % self.actual
        compare(self.actual is None, True, msg)
    
    def to_return(self, expected):
        actual = self.actual()
        msg = "Expected callable to return '%s' but got '%s'" % (expected, actual)
        compare(actual == expected, True, msg)
        
    def to_raise(self, expected=None):
        raised_exception = False
        try:
            self.actual()
        except Exception as e:
            if not expected:
                raised_exception = True
            elif expected and e.message == expected:
                raised_exception = True
        if expected:
            msg = "Expected callable to raise exception \"%s\"" % expected
        else:
            msg = "Expected callable to raise an exception"
        compare(raised_exception, True, msg)


def compare(expr, outcome, message=""):
    """Compares the result of the given boolean expression the anticipated
    boolean outcome. If there is a match, all is well. If the comparison fails,
    it throws an AssersionError with the given message
    
    # it should stay quite if the comparison lines up
    >>> compare(5 == 5, True)
    
    # it should throw an error if the comparison fails
    >>> compare('Foo' == 'foo', True)
    Traceback (most recent call last):
        ...
    AssertionError
    
    # it should throw an error with the given message if the comparison fails
    >>> actual = 'Foo'
    >>> expected = 'foo'
    >>> message = "'%s' does not equal '%s'" % (actual, expected)
    >>> compare(actual == expected, True, message)
    Traceback (most recent call last):
        ...
    AssertionError: 'Foo' does not equal 'foo'
    """
    if expr != outcome:
        raise AssertionError(message)


def expect(value):
    """Creates an value (Matcher) object with matchers for the given value
    
    >>> e = expect(5 + 8)
    >>> type(e) == Matcher
    True
    >>> e.actual
    13
    """
    return Matcher(value)


def main():
    """A simple wrapper that calls nosetests
    with a regex of keywords to use in discovering specs
    """
    return os.system('nosetests --with-doctest -i "^(Describe|it|should)" -i "(Spec[s]?)$" -i "(specs?|examples?)(.py)?$" ' + ' '.join(sys.argv[1:]))
    
if __name__ == '__main__':
    main()
