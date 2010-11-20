from django.test import TestCase
from util.monitor import ArgSet
import datetime
import dateutil.parser

class ArgSetTests(TestCase):
    # def setUp(self):
    #     pass
        
    def test_argset_defaults(self):
        """testing ArgSet default values"""
        arg_set = ArgSet()
        self.assertTrue(arg_set)
        self.assertEquals(arg_set.list_of_arguments(), [])
        self.assertEquals(arg_set.__str__(), "")

    def test_argset_items(self):
        "testing setting single ArgSet items"
        arg_set = ArgSet()
        arg_set.add_argument('--help')
        self.assertEquals(arg_set.list_of_arguments(), ['--help'])
        self.assertEquals(arg_set.__str__(), "--help ")
        arg_set.add_argument('now')
        self.assertEquals(arg_set.list_of_arguments(), ['--help', 'now'])
        self.assertEquals(arg_set.__str__(), "--help now ")

    def test_argset_pairs(self):
        "testing setting ArgSet pairs"
        arg_set = ArgSet()
        arg_set.add_argument_pair('-H', 'localhost')
        self.assertEquals(arg_set.list_of_arguments(), ['-H', 'localhost'])
        self.assertEquals(arg_set.__str__(), "-H localhost ")
        arg_set.add_argument('now')
        self.assertEquals(arg_set.list_of_arguments(), ['-H', 'localhost', 'now'])
        self.assertEquals(arg_set.__str__(), "-H localhost now ")

    def test_argset_json(self):
        "testing json export of ArgSet"
        arg_set = ArgSet()
        arg_set.add_argument_pair('-H', 'localhost')
        self.assertEquals(arg_set.json(), '[{"-H": "localhost"}]')
        arg_set.add_argument('now')
        self.assertEquals(arg_set.json(), '[{"-H": "localhost"}, {"now": null}]')

    def test_argset_jsonload(self):
        """testing correct loading of json input and equiv with created elements"""
        arg_set = ArgSet()
        arg_set.add_argument_pair('-H', 'localhost')
        arg_set.add_argument('now')
        json_out = arg_set.json()
        
        new_arg_set = ArgSet()
        new_arg_set.loadjson(json_out)
        self.assertEquals(new_arg_set.json(), arg_set.json())
        self.assertEquals(new_arg_set.json(), '[{"-H": "localhost"}, {"now": null}]')
        self.assertEquals(new_arg_set.list_of_arguments(), ['-H', 'localhost', 'now'])
        self.assertEquals(new_arg_set.__str__(), "-H localhost now ")

    def test_argset_failed_jsonload1(self):
        """ testing the various raise/validation of json inputs - extra list"""
        arg_set = ArgSet()
        broken_json_1 = '[{"-H": "localhost"}, [{"now": null}]]'
        self.assertRaises(ValueError, arg_set.loadjson, broken_json_1)

    def test_argset_failed_jsonload2(self):
        """ testing the various raise/validation of json inputs - numeric value"""
        arg_set = ArgSet()
        broken_json_2 = '[{"-H": "localhost"}, {"now": 123}]'
        self.assertRaises(ValueError, arg_set.loadjson, broken_json_2)

    def test_argset_failed_jsonload3(self):
        """ testing the various raise/validation of json inputs - numeric key"""
        arg_set = ArgSet()
        broken_json_3 = '[{123: "localhost"}, {"now": "fred"}]'
        self.assertRaises(ValueError, arg_set.loadjson, broken_json_3)

    def test_argset_failed_jsonload4(self):
        """ testing the various raise/validation of json inputs - numeric key"""
        arg_set = ArgSet()
        broken_json_3 = '[{123: "localhost"}, {5: "fred"}]'
        self.assertRaises(ValueError, arg_set.loadjson, broken_json_3)

    def test_argset_failed_jsonload5(self):
        """ testing the various raise/validation of json inputs - outer list"""
        arg_set = ArgSet()
        broken_json_4 = '{123: "localhost"}'
        self.assertRaises(ValueError, arg_set.loadjson, broken_json_4)
        self.assertEquals(arg_set.json(), ArgSet().json())

    def test_argset_failed_jsonload6(self):
        """ testing the various raise/validation of json inputs - outer list"""
        arg_set = ArgSet()
        broken_json_4 = '{123: "localhost"}'
        try:
            arg_set.loadjson(broken_json_4)
            self.fail("should have raised a ValueError")
        except ValueError:
            pass

class DateTimeParsingTests(TestCase):
    def test_timeparser(self):
        now = datetime.datetime.now()
        string_out = now.isoformat()
        new_now = dateutil.parser.parse(string_out)
        self.assertEquals(now.year, new_now.year)
        self.assertEquals(now.month, new_now.month)
        self.assertEquals(now.day, new_now.day)
        self.assertEquals(now.hour, new_now.hour)
        self.assertEquals(now.minute, new_now.minute)
        self.assertEquals(now.second, new_now.second)