"""
tipfy.ext.debugger
==================

This extension provides a middleware that enables a useful debugger for
`tipfy <http://www.tipfy.org/>`_.

Links
-----
* `Documentation <http://www.tipfy.org/wiki/extensions/debugger/>`_
* `Source Code Repository <http://code.google.com/p/tipfy-ext-debugger/>`_
* `Issue Tracker <http://code.google.com/p/tipfy-ext-debugger/issues/list>`_

About tipfy
-----------
* `Home page <http://www.tipfy.org/>`_
* `Extension list <http://www.tipfy.org/wiki/extensions/>`_
* `Discussion Group <http://groups.google.com/group/tipfy>`_
"""
from setuptools import setup

setup(
    name = 'tipfy.ext.debugger',
    version = '0.6.1',
    license = 'BSD',
    url = 'http://www.tipfy.org/',
    description = 'Debugger extension for tipfy',
    long_description = __doc__,
    author = 'Rodrigo Moraes',
    author_email = 'rodrigo.moraes@gmail.com',
    zip_safe = False,
    platforms = 'any',
    packages = [
        'tipfy',
        'tipfy.ext',
        'tipfy.ext.debugger',
    ],
    namespace_packages = [
        'tipfy',
        'tipfy.ext',
    ],
    include_package_data = True,
    install_requires = [
        'tipfy',
        'jinja2',
    ],
    classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ]
)
