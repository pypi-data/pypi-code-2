import os
import unittest2
import yamlconfig

dummy_yaml = """
main:
    name: 'Napoleon'
    age: 15
    skills: ['Ninja', 'Dancing', 'Nunchucks', $default_skills]
    net_worth: $10
"""

def create_dummy_config():
    with open('dummy_config.yaml', 'w') as config:
        config.write(dummy_yaml)

class TestYamlConfig(unittest2.TestCase):

    def setUp(self):
        create_dummy_config()
        self.infile = 'dummy_config.yaml'
        self.defaults = {'default_skills': 'Kickball'} 
        self.config = yamlconfig.YamlConfig(self.infile, self.defaults)

    def tearDown(self):
        os.remove('dummy_config.yaml')

    def test_get_config(self):
        expected_config = {
            'main': {
                'name': 'Napoleon',
                'age': 15,
                'skills': ['Ninja', 'Dancing', 'Nunchucks', 'Kickball'],
                'net_worth': '$10'
                }
        }
        self.assertDictEqual(expected_config, self.config)

    def test_list_type(self):
        self.assertIsInstance(self.config['main']['skills'], list)

    def test_int_type(self):
        self.assertIsInstance(self.config['main']['age'], int)

    def test_str_type(self):
        self.assertIsInstance(self.config['main']['name'], str)

    def test_keyerror(self):
        def getoption(option):
            return self.config['main'][option]
        self.assertRaises(KeyError, getoption, 'girlfriend')

    def test_safe_substitute(self):
        self.assertEqual(self.config['main']['net_worth'], '$10')

    def test_with_no_defaults(self):
        create_dummy_config()
        infile = 'dummy_config.yaml'
        config = yamlconfig.YamlConfig(infile)
        expected_config = {
            'main': {
                'name': 'Napoleon',
                'age': 15,
                'skills': ['Ninja', 'Dancing', 'Nunchucks', '$default_skills'],
                'net_worth': '$10'
                }
        }
        self.assertDictEqual(expected_config, config)

if __name__ == '__main__':
    unittest2.main()
