from distutils.core import setup

setup(
    name='wget',
    version='0.7',
    author='anatoly techtonik <techtonik@gmail.com>',
    url='http://bitbucket.org/techtonik/python-wget/',

    description="python -m wget <URL>",
    license="Public Domain",
    classifiers=[
        'Environment :: Console',
        'License :: Public Domain',
        'Operating System :: OS Independent',
        'Topic :: System :: Networking',
        'Topic :: Utilities',
    ],

    py_modules=['wget'],

    long_description= """
ChangeLog
=========
0.7 (2011-03-01)
 * compatibility fix for Python 2.5
 * limit width of progress bar to 100 chars

0.6 (2010-04-24)
 * it detects console width on POSIX

0.5 (2010-04-23)
 * it detects console width on Windows

0.4 (2010-04-15)
 * it shows cute progress bar

0.3 (2010-04-05)
 * it creates temp file in current dir

0.2 (2010-02-16)
 * it tries to detect filename from URL

0.1 (2010-02-04)
 * it can download file
"""
)
