from setuptools import setup
import my_xml

setup(
    name = "my_xml",
    version = "0.1.2",
    py_modules=["my_xml"],

    # metadata for uploading to PyPI
    author = "Erez Bibi",
    author_email = "erezbibi@users.sourceforge.net",
    description = "Easy to use parser for simple XML",
    keywords = "Simple XML Parser",
    long_description = my_xml.__doc__,
    classifiers = [
    'Intended Audience :: Developers',
    'License :: Public Domain',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Topic :: Text Processing :: Markup :: XML',
    'Topic :: Utilities'
    ]
)
