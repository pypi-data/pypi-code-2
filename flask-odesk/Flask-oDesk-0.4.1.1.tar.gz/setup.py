"""
Flask-oDesk
-----------
Adds oDesk API support to Flask.

flask-odesk version 0.4.1
(C) 2011 oDesk
"""

import os
from setuptools import setup, find_packages

readme = open(os.path.join(os.path.dirname(__file__), 'README'))
README = readme.read()
readme.close()

version = __import__('flaskext').get_version()

setup(
    name='Flask-oDesk',
    version='0.4.1.1',
    download_url ='http://github.com/odesk/flask-odesk',
    url='https://github.com/odesk/flask-odesk',
    license='BSD',
    author='Artem Gnilov',
    author_email='boobsd@gmail.com',
    maintainer='Volodymyr Hotsyk',
    maintainer_email='gotsyk@gmail.com',
    description='Adds oDesk API support to Flask',
    long_description=README,
    packages=['flaskext'],
    namespace_packages=['flaskext'],
    zip_safe=False,
    platforms='any',
    install_requires=[
        'Flask',
        'oauth2',
        'python-odesk>=0.4'
    ],
    test_suite='tests',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
