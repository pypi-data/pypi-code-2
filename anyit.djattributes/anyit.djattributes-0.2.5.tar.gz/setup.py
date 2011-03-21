import os
from setuptools import setup

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "anyit.djattributes",
    version = "0.2.5",
    author = "Jan Hoehn",
    author_email = "jan@anyit.de",
    description = ("Attributes for django models in a JQuery inspired syntax."),
    license = "BSD",
    keywords = "django atributes generic",
    packages=['anyit', 'anyit.djattributes', 'anyit.djattributes.attributes'],
    long_description=read('README'),
    classifiers = [
        'Development Status :: 4 - Beta',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP',
    ]

)

