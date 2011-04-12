from distutils.core import setup, Extension

setup (
        name = 'apache_conf_parser',
        version = '1.0.1',
        description = 'Parse and manipulate apache conf files.',
        author = "Eric Snow",
        author_email = "ericsnowcurrently@gmail.com",
        url = "https://bitbucket.org/ericsnowcurrently/apache_conf_parser/overview",
        py_modules = [
                "apache_conf_parser", 
                "test_apache_conf_parser", 
                ],
        )
