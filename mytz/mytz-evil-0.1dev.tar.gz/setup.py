"""
mytz
====

The original idea for this was based on my work on Rodrigo Moraes' `gae-pytz`_.
Limitations within pytz caused its performance to be unacceptable for
short-running applications, such as in Google App Engine. The issue, and
related issues to do with this remain un-addressed today.

The crux of this issue is based around the "all_timezones" and
"common_timezones" variables, which cause the entire timezone list to be loaded
(well over five hundred!) at import time. Beause it's done in __init__.py, it
cannot be avoided without hacks such as gae-pytz.

So this is a fork, but intends to be a drop-in replacement for the most part
for pytz. In the process will be a number of code cleanups, and unit testing.
"""

from distutils.core import setup

setup(
    name='mytz',
    version='0.1dev',
    url='http://bitbucket.org/crast/mytz/',
    license='BSD',
    author='James Crasta',
    author_email='mytz@simplecodes.com',
    description='A drop-in replacement for pytz.',
    long_description=__doc__,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    packages=[
        'pytz',
        'pytz.loaders',
    ],
        include_package_data=True,
            package_data={'': ['*.zip']},
)
