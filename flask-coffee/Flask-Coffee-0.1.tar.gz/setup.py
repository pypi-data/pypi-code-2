"""
Flask-Coffee
-------------

Automatically compile CoffeeScript files while developing with the Flask framework.

"""
from setuptools import setup


setup(
    name='Flask-Coffee',
    version='0.1',
    url='http://terse-words.blogspot.com/',
    license='BSD',
    author='Col Wilson',
    author_email='colwilson@bcs.org',
    description='Fill your flask with coffee.',
    long_description=__doc__,
    packages=['flaskext'],
    namespace_packages=['flaskext'],
    zip_safe=False,
    platforms='any',
    install_requires=[
        'Flask'
    ],
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
