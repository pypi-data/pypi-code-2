#!/usr/bin/env python

import unittest
import logging
import re
import time
import unittest

import nonblockingloghandler

# Define a Logging Handler we can call and inspect.
class MockHandler(logging.Handler):
    def __init__(self):
        self.contents = []
        logging.Handler.__init__(self)

    def _store(self, name, sleep_period, *args, **kwargs):
        #print "MOCK CALLED %s()" % name
        time.sleep(sleep_period)
        self.contents.append("MockHandler::%s(%s, %s)" % (
            str(name),
            ((", ".join([str(arg) for arg in args])) if args else ""),
            kwargs if kwargs else ""
            )
        )
        return None

    @staticmethod
    def _dump(method_name="unspecified", sleep_period = 0):
        return lambda self, args=None: self._store(method_name, sleep_period, args)

MockHandler.close = MockHandler._dump("close")
MockHandler.format = MockHandler._dump("format")
MockHandler.createLock = MockHandler._dump("createLock")
MockHandler.acquire = MockHandler._dump("acquire")
MockHandler.release = MockHandler._dump("release")
MockHandler.setFormatter = MockHandler._dump("setFormatter")
MockHandler.flush = MockHandler._dump("flush")
MockHandler.emit = MockHandler._dump("emit", 0.01)
MockHandler.setLevel = MockHandler._dump("setLevel")
# MockHandler.handle = MockHandler._dump("handle") # Let the standard handler do its thing.
MockHandler.handleError = MockHandler._dump("handleError")

# Test utility
def assert_list_like_template(actual, desired):
    """Compare an actual list of strings with a desired list of regular expressions, and assert they are the same."""
    assert len(actual) == len(desired), "List is different length to desired: %s" % actual
    for index, actual in enumerate(actual):
        assert re.match(desired[index], actual), "Actual doesn't match desired (row = %s):\n %s\n %s\n" % (index, actual, desired[index])

class TestNonblockingLogHandler(unittest.TestCase):

    def setUp(self):
        logging.basicConfig()
        for handler in logging.getLogger("").handlers[:]:
            logging.getLogger("").removeHandler(handler)
            handler.close()

    def test_mock_handler(self):
        # Make sure we have the test harness working before we start.
        mh = MockHandler()
        logging.getLogger("").addHandler(mh)
        logging.error("Error message")
        logging.getLogger("").removeHandler(mh)
        mh.close()
        time.sleep(2)
        assert_list_like_template(mh.contents, ['MockHandler::createLock\(None, \)',
                                                'MockHandler::acquire\(None, \)',
                                                'MockHandler::emit\(<LogRecord: root, 40, [^,]*, \d+, "Error message"\>, \)',
                                                'MockHandler::release\(None, \)',
                                                'MockHandler::close\(None, \)'])

    def test_straightforward_usage(self):
        # Straight forward, single log message.
        mh = MockHandler()
        nh = nonblockingloghandler.NonblockingLogHandler(mh)
        logging.getLogger("").addHandler(nh)
        start_time = time.clock()
        logging.error("Error message")
        end_time = time.clock()
        assert end_time - start_time < 0.005, "Spent too long: %s" % (end_time - start_time)
        time.sleep(0.02) # Give logging a chance before checking on it.
        logging.getLogger("").removeHandler(nh)
        nh.close()
        mh.close()
        assert_list_like_template(mh.contents, ['MockHandler::createLock\(None, \)',
                                                'MockHandler::acquire\(None, \)',
                                                'MockHandler::emit\(<LogRecord: root, 40, [^,]*, \d+, "Error message"\>, \)',
                                                'MockHandler::release\(None, \)',
                                                'MockHandler::close\(None, \)',
                                                ]
                                  )

    def test_basic_formatting(self):
        # Ensure substitutions are performed before the call is made.
        mh = MockHandler()
        nh = nonblockingloghandler.NonblockingLogHandler(mh)
        logging.getLogger("").addHandler(nh)
        logging.error("The wages of %s is %s", "sin", "death")
        time.sleep(0.05) # Give logging a chance before checking on it.
        logging.getLogger("").removeHandler(nh)
        nh.close()
        mh.close()
        assert_list_like_template(mh.contents, ['MockHandler::createLock\(None, \)',
                                                'MockHandler::acquire\(None, \)',
                                                'MockHandler::emit\(<LogRecord: root, 40, [^,]*, \d+, "The wages of sin is death"\>, \)',
                                                'MockHandler::release\(None, \)',
                                                'MockHandler::close\(None, \)',
                                                ]
                                  )

    def test_multiple_calls(self):
        # Ensure that calls are queued.
        mh = MockHandler()
        nh = nonblockingloghandler.NonblockingLogHandler(mh)
        logging.getLogger("").addHandler(nh)
        start_time = time.clock()
        for i in range(30):
            logging.info("Info message") # Below threshold.
            logging.critical("Critical message")
            logging.warning("Warning message")
        end_time = time.clock()
        assert end_time - start_time < 60 * 0.005 # Delay of 0.25 is too much.
        time.sleep(10.030) # Give logging a chance before checking on it.
        logging.getLogger("").removeHandler(nh)
        nh.close()
        mh.close()
        result_prefix = ['MockHandler::createLock\(None, \)']
        result_middle = 30 * [
            'MockHandler::acquire\(None, \)',
            'MockHandler::emit\(<LogRecord: root, 50, [^,]+, \d+, "Critical message">, \)',
            'MockHandler::release\(None, \)',
            'MockHandler::acquire\(None, \)',
            'MockHandler::emit\(<LogRecord: root, 30, [^,]+, \d+, "Warning message">, \)',
            'MockHandler::release\(None, \)',
        ]
        result_suffix =  ['MockHandler::close\(None, \)',]
        assert_list_like_template(mh.contents, result_prefix + result_middle + result_suffix)

    def test_set_formatter(self):
        # Ensure that setFormat gets through.
        mh = MockHandler()
        nh = nonblockingloghandler.NonblockingLogHandler(mh)
        logging.getLogger("").addHandler(nh)
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        nh.setFormatter(formatter)
        logging.error("The wages of %s is %s", "sin", "death")
        time.sleep(0.05) # Give logging a chance before checking on it.
        logging.getLogger("").removeHandler(nh)
        nh.close()
        mh.close()
        assert_list_like_template(mh.contents, ['MockHandler::createLock\(None, \)',
                                                'MockHandler::setFormatter\(<logging.Formatter[^,]*, \)',
                                                'MockHandler::acquire\(None, \)',
                                                'MockHandler::emit\(<LogRecord: root, 40, [^,]*, \d+, "The wages of sin is death"\>, \)',
                                                'MockHandler::release\(None, \)',
                                                'MockHandler::close\(None, \)',
                                                ]
                                  )

if __name__ == "__main__":
    unittest.main()
