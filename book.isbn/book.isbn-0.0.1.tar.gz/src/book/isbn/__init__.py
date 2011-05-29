# -*- coding: utf-8 -*-


__all__ = ['check10',
           'check13',
           'modulus11weight10to2',
           'modulus11weight3',
           'encode10to13',
           'encode13to10',
           ]


def check10(isbn10):
    u"""
    >>> check10(u'0306406152')
    True
    """

    if len(isbn10) != 10:
        raise ValueError(len(isbn10))

    check_sum = modulus11weight10to2(isbn10[:-1])
    if isbn10[-1] == check_sum:
        return True
    else:
        return False


def check13(isbn13):
    u"""
    >>> check13(u'9780306406157')
    True
    """

    if len(isbn13) != 13:
        raise ValueError(len(isbn13))

    check_sum = modulus11weight3(isbn13[:-1])
    if isbn13[-1] == check_sum:
        return True
    else:
        return False


def modulus11weight10to2(c9):
    u"""
    >>> modulus11weight10to2(u'030640615')
    u'2'
    """

    if len(c9) != 9:
        raise ValueError(len(c9))

    sum = 0
    for i in range(len(c9)):
        try:
            c = int(c9[i])
        except ValueError:
            return False
        weight = 10 - i
        sum += weight * c

    remainder = sum % 11
    result = 11 - remainder

    if result == 10:
        return u'X'
    else:
        return unicode(result)


def modulus11weight3(c12):
    u"""
    >>> modulus11weight3(u'978030640615')
    u'7'
    """

    if len(c12) != 12:
        raise ValueError(len(c12))

    sum = 0
    for i in range(len(c12)):
        try:
            c = int(c12[i])
        except ValueError:
            return False
        if i % 2:
            weight = 3
        else:
            weight = 1
        sum += weight * c

    remainder = sum % 10
    result = 10 - remainder

    if result == 10:
        return u'0'
    else:
        return unicode(result)


def encode10to13(isbn10):
    u"""
    >>> encode10to13(u'0306406152')
    u'9780306406157'
    >>> encode10to13(u'487311361X')
    u'9784873113616'
    >>> encode10to13(u'4873114209')
    u'9784873114200'
    """

    if len(isbn10) != 10:
        raise ValueError(len(isbn10))

    prefix = u'978' + isbn10[:-1]
    check_digit = modulus11weight3(prefix)
    return prefix + check_digit


def encode13to10(isbn13):
    u"""
    >>> encode13to10(u'9780306406157')
    u'0306406152'
    >>> encode13to10(u'9784873113616')
    u'487311361X'
    >>> encode13to10(u'9784873114200')
    u'4873114209'
    """

    if len(isbn13) != 13:
        raise ValueError(len(isbn13))

    prefix = isbn13[3:-1]
    check_digit = modulus11weight10to2(prefix)
    return prefix + check_digit
