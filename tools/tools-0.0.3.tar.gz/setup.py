import os
from setuptools import setup, find_packages

setup(
    name = 'tools',
    description = 'Private seo tools',
    version = '0.0.3',
    url = 'http://bitbucket.org/lorien/tools/',
    author = 'Grigoriy Petukhov',
    author_email = 'lorien@lorien.name',

    packages = find_packages(),
    include_package_data = True,

    license = "BSD",
    keywords = "seo scraping captcha antigate parsing",
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Utilities'
    ],
)
