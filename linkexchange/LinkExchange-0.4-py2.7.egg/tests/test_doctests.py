import doctest

def load_tests(loader, tests, ignore):
    tests.addTests(doctest.DocTestSuite('linkexchange.config'))
    tests.addTests(doctest.DocTestSuite('linkexchange.db_drivers'))
    tests.addTests(doctest.DocTestSuite('linkexchange.formatters'))
    tests.addTests(doctest.DocTestSuite('linkexchange.platform'))
    tests.addTests(doctest.DocTestSuite('linkexchange.utils'))
    tests.addTests(doctest.DocTestSuite('linkexchange.tests'))
    return tests
