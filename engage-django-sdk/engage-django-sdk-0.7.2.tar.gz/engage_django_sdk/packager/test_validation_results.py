import unittest
import json
import traceback

from validation_results import *


class TestValidationResults(unittest.TestCase):
    def test_validation_results(self):
        """Do a round-trip of json serialization and parsing.
        """
        # first create a sample exception
        try:
            raise Exception("This is a test exception")
        except:
            (exc_type, exc_value, exc_traceback) = sys.exc_info()
        js = create_results_json(SETTINGS_VALIDATION_ERROR_RC,
                                 "test",
                                 error_messages=["this is an error message",],
                                 exception=traceback.format_exception(exc_type, exc_value, exc_traceback))
        data = json.dumps(js)
        r = ParsedJsonResults(json.loads(data))



if __name__ == '__main__':
    unittest.main()
