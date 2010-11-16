import doctest


def test_suite():
    return doctest.DocFileSuite(
        'README.txt',
        optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS)
