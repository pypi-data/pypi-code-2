import os
from setuptools import setup, find_packages

this_dir = os.path.dirname(__file__)

setup(
    version='0.1.2',
    name='gocept.arecibologger',
    author='Christian Theune',
    author_email='ct@gocept.com',
    license='ZPL',
    description='Arecibo patch for Zope 2\'s site error log.',
    long_description=(open('README.txt').read() +
                      '\n\n' +
                      open('CHANGES.txt').read()),
    keywords="logging",
    classifiers=[
    'Framework :: Plone',
    'Framework :: Zope2',
    'Intended Audience :: Developers',
    'Intended Audience :: System Administrators',
    'Topic :: System :: Logging',
    ], 
    packages=find_packages('src'),
    package_dir = {'': 'src'},
    zip_safe=False,
    include_package_data=True)
