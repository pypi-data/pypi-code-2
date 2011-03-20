# encoding: utf-8
from distutils.core import setup

setup(
    name='json-store',
    version='1.1',
    packages=['json_store',],
    scripts=['bin/shelve2json.py',],
    license='MIT License',
    description="A shelve-like store using JSON serialization.",
    long_description="JSON store is a simple replacement for shelve. It writes"
                     " JSON serialized files and can accept unicode keys.",
    author='jeremy avnet',
    author_email='brainsik-code@theory.org',
    url='https://github.com/brainsik/json-store',
)
