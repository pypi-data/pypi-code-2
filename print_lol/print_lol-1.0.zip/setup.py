#import setup function from Python's distribution utilities
from distutils.core import setup

setup(
	#Name of the file after being packed
    name = 'print_lol',
    version = '1.0',
	#Name of the module to be called later, this is the name of the .py file
    py_modules = ['chapter1'],
    author = 'Khang Nguyen',
    )
