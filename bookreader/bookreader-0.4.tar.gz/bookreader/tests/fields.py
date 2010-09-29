import unittest

from django.utils.datastructures import MultiValueDict
from django.utils.simplejson import  dumps

from bookreader.fields import MultiValueDictField



class MVDTest(unittest.TestCase):
    def setUp(self):
        self.field = MultiValueDictField('test field')
        self.data = {'a': [1,2,3],
                     'b': 'test',
                     'c': ['a','b','c']}
    
    def test_to_python_string(self):
        """ MultiValueDictField to_python with string input """
        self.assertEqual(self.field.to_python(dumps(self.data)),
                         MultiValueDict(self.data))
    
    def test_to_python_dict(self):
        """ MultiValueDictField to_python with dict input """
        self.assertEqual(self.field.to_python(self.data),
                         MultiValueDict(self.data))
    
    def test_to_python_mvd(self):
        """ MultiValueDictField to_python with MultiValueDict input """
        self.assertEqual(self.field.to_python(MultiValueDict(self.data)),
                         MultiValueDict(self.data))
    
    def test_to_python_false(self):
        """ MultiValueDictField to_python with bool(value) == False input """
        self.assertEqual(self.field.to_python(False),
                         MultiValueDict())
        self.assertEqual(self.field.to_python(None),
                         MultiValueDict())
        self.assertEqual(self.field.to_python(''),
                         MultiValueDict())
        self.assertEqual(self.field.to_python([]),
                         MultiValueDict())
        self.assertEqual(self.field.to_python({}),
                         MultiValueDict())
    
    def test_to_python_invalid(self):
        """ MultiValueDictField to_python with invalid input """
        self.assertRaises(ValueError,
                          self.field.to_python,
                          ['a','b','c'])
        self.assertRaises(ValueError,
                          self.field.to_python,
                          12345)
    
    def test_get_prep_value_mvd(self):
        """ MultiValueDictField get_prep_value with MultiValueDict input """
        self.assertEqual(self.field.get_prep_value(MultiValueDict(self.data)),
                         dumps(self.data))
        
    def test_get_prep_value_dict(self):
        """ MultiValueDictField get_prep_value with dict input """
        self.assertEqual(self.field.get_prep_value(self.data),
                         dumps(self.data))
    
    def test_get_prep_value_string(self):
        """ MultiValueDictField get_prep_value with string input """
        self.assertEqual(self.field.get_prep_value(dumps(self.data)),
                         dumps(self.data))
    
    def test_get_prep_value_false(self):
        """ MultiValueDictField get_prep_value with bool(value) == False input """
        self.assertEqual(self.field.get_prep_value(None),None)
        self.assertEqual(self.field.get_prep_value(False),None)
        self.assertEqual(self.field.get_prep_value(''),None)
    
    def test_get_prep_value_invalid(self):
        """ MultiValueDictField get_prep_value with invalid input """
        self.assertRaises(ValueError,
                          self.field.get_prep_value,
                          123)
        self.assertRaises(ValueError,
                          self.field.get_prep_value,
                          ['a','b','c'])
    


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.TestLoader().loadTestsFromTestCase(MVDTest))
    return suite

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(test_suite())
