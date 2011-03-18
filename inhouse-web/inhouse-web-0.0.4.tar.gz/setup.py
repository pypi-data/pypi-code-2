# -*- coding: utf-8 -*-

from setuptools import setup, find_packages


setup(
    name='inhouse-web',
    version=__import__('inhouse').__version__,
    description='Web based time recording and management application',
    long_description="""Inhouse-Web is web-based time recording and tracking
    software built for companies, that want to track their projects worktime
    to get an accurate time billing for their customers""",
    author='Henning Kage',
    author_email='henning.kage@googlemail.com',
    url='http://code.google.com/p/inhouse-web',
    packages=find_packages(),
    install_requires=[
        'Django>=1.2',
        'django-pagination>=1.0',
        'django-issue-synchronisation'],
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python'
        ],
)
