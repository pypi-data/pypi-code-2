from setuptools import setup, find_packages
import sys, os

version = '0.5'

setup(name='encoding_repair',
      version=version,
      description="Helpers to repair encodings (especially umlauts)",
      long_description="""
It is alarming, that very often, special characters like umlauts break when
converting through different encodings. (You might want to take a look at the
German Amazon Marketplace.)
A broken umlaut is still valid in the target encoding and therefore can only be
detect through heuristics (magic).

Version 0.5: supporting utf-8 and latin1
For a full changeset, take a look at bitbucket.org/niels_mfo/encoding_repair
(bug reports will also be accepted there)

A common case that breaks a special character is the following:
    - An input string is coded in utf-8 (which uses multibyte chars)
    - It is interpreted as being a valid latin1 string
    - Latin1 has a valid representation for nearly all bytes
    - Latin1 uses single-byte chars
    - Now both bytes of the multi-byte char are interpreted as chars
    - The special char broke off into two different (valid!) characters

This scenario has many pitfalls:
    - The characters are irreversebly broken.
    - ... regardless of what you do with the string.
    - You can convert it through all encodings and the umlauts won't come back.
    - Only through a few heuristical replaces, this module is able to help you.

This module assumes, that a few special characters are always correct. They are
stored in the list 'umlauts'. Furthermore, the module assumes, that their
representation, that would be correct in the other encoding, is always broken in
the target-encoding.

NOTE:
This only happens, because people don't use unicode. If everybody would
consequently use unicode strings, I would not have to write this module.
The best and actually only way to handle encodings correctly is the following:
    - An input string comes into your programm.
    - If it is unicode, jump to point 6.
    - If it isn't, you might already need to repair umlauts.
    - You need to make sure, that you know the right encoding of the input
        string, because it is hardly possible to guess.
    - Convert it to unicode.
    - Use the unicode string throuout your whole programm.
    - If you can return unicode, return unicode.
    - If you are in doubt, return unicode.
    - If you really need to return anything else, return utf-8.
    - If you are certain, that the programm, which will take your output is not
        able to handle neither unicode nor utf-8, you better write a bug report.
""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='encoding utf-8 latin1 character magic umlaut special unicode',
      author='Niels Ranosch',
      author_email='ranosch@mfo.de',
      url='bitbucket.org/niels_mfo/encoding_repair',
      license='MIT',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=True,
      install_requires=[
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
