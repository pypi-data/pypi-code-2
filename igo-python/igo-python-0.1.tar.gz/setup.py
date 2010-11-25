#!/usr/bin/env python
# encoding: utf-8

from setuptools import setup

desc = '''\
================
 Igo for Python
================

Igo_ is a Japanese morphological analyzer written in Java and Common Lisp.
This software is Python port of Igo(Java version).

  Notice
============
Dictionary builder is not provided. You need to use Igo Java version to build the dictionary for Igo.

 How To Use
============
You can use Igo Python easily
::
 >>> from igo.Tagger import Tagger
 >>> t = Tagger("ipadic")
 >>> for m in t.parse(u"すもももももももものうち"):
 ...     print m.surface, m.feature
 ...
 すもも 名詞,一般,*,*,*,*,すもも,スモモ,スモモ
 も 助詞,係助詞,*,*,*,*,も,モ,モ
 もも 名詞,一般,*,*,*,*,もも,モモ,モモ
 も 助詞,係助詞,*,*,*,*,も,モ,モ
 もも 名詞,一般,*,*,*,*,もも,モモ,モモ
 の 助詞,連体化,*,*,*,*,の,ノ,ノ
 うち 名詞,非自立,副詞可能,*,*,*,うち,ウチ,ウチ
 >>>

.. _Igo: http://igo.sourceforge.jp/
'''

setup(
    name='igo-python',
    version='0.1',
    description='Python port of Igo Japanese morphological analyzer',
    long_description = desc,
    author='Hideaki Takahashi',
    author_email='mymelo@gmail.com',
    url='https://code.launchpad.net/~hideaki-t/+junk/igo-py/',
    classifiers=['Development Status :: 4 - Beta',
                 'Intended Audience :: Developers',
                 'License :: OSI Approved :: MIT License',
                 'Natural Language :: Japanese',
                 'Operating System :: OS Independent',
                 'Operating System :: Microsoft :: Windows',
                 'Operating System :: POSIX :: Linux',
                 'Programming Language :: Python :: 2',
                 'Programming Language :: Python :: 2.5',
                 'Programming Language :: Python :: 2.6',
                 'Topic :: Scientific/Engineering :: Information Analysis',
                 'Topic :: Software Development :: Libraries :: Python Modules',
                 'Topic :: Text Processing :: Linguistic',
                 ],
    keywords=['japanese', 'morphological analyzer',],
    license='MIT',
    packages=['igo'],
    )
