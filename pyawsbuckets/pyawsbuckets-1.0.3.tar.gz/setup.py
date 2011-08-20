import os
from setuptools import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name='pyawsbuckets',
    version='1.0.3',
    author='Mark Henwood',
    author_email='mark@mcbh.co.uk',
    description='Handle Amazon S3 PUT/DELETE/sign interactions',
    license='MIT',
    keywords='amazon aws s3 buckets',
    url='http://packages.python.org/pyawsbuckets',
    packages=['pyawsbuckets'],
    long_description=read('README.rst'),
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Plugins',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.6',
        'Topic :: Utilities'
    ]
)