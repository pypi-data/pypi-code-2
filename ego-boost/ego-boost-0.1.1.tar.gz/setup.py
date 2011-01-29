#!/usr/bin/python
from setuptools import setup, Command

class PyTest(Command):
    user_options = []
    def initialize_options(self):
        pass
    def finalize_options(self):
        pass
    def run(self):
        import sys, subprocess
        errno = subprocess.call([sys.executable, 'tests/runtests.py'])
        raise SystemExit(errno)

setup(name='ego-boost',
    version='0.1.1',
    description="Package to track your module's download statistics",
    long_description=open('README').read(),
    author='Sebastian Rahlf',
    author_email='basti at redtoad dot de',
    license='MIT', 
    url='http://pypi.python.org/pypi/ego-boost',
    packages=['egoboost'],
    scripts=['ego-boost'],
    install_requires=[
        'simplejson',
        'lxml'
    ],

    cmdclass = {'test' : PyTest},

    classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: System :: Archiving :: Packaging',
        'Topic :: System :: Logging', 
    ]
)
