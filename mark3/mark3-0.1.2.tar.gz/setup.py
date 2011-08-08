import os
from setuptools import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name='mark3',
    version=__import__('mark3').VERSION,
    author='Joseph Marshall',
    author_email='marshallpenguin@gmail.com',
    url='https://bitbucket.org/jlm/mark3',
    description='A lightweight markdown to html converter.',
    keywords = 'markdown html',
    packages=['mark3'],
    long_description=read('README'),
    classifiers = [
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Development Status :: 4 - Beta",
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Topic :: Text Processing :: Markup :: HTML',
        ],
)
