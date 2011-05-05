import os
from setuptools import setup

def read(fname):
  return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "pswinpy",
    version = "0.0.1",
    author = "Torbjorn Maro",
    author_email = "torbjorn@pswin.com",
    description = "A package for sending SMS messages using the PSWinCom SMS Gateway.",
    license = "MIT License",
    keywords = "SMS",
    url = "https://github.com/tormaroe/pswinpy",
    packages = ['pswinpy'],
    long_description = read('README.md'),
    classifiers = [
      "Development Status :: 4 - Beta",
      "Programming Language :: Python",
      "Programming Language :: Python :: 3",
      "Intended Audience :: Developers",
      "Topic :: Communications :: Telephony",
      "Topic :: Software Development :: Libraries :: Python Modules",
      "License :: OSI Approved :: MIT License",
      "Operating System :: OS Independent",
    ],
)
