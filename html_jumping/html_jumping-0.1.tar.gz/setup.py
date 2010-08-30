# -*- coding: utf-8 -*-
import os
from setuptools import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
  name = "html_jumping",
  version = "0.1",
  author = "Daniel Perez Rada",
  author_email = "daniel@zappedy.com",
  description = ("Allows to get an HTML, passing previously for several URL. This is sometimes needed because some webpages need cookies or a HTTP referrer to get a certain page."),
  license = "BSD",
  keywords = "html_jumping cookies html get post form referrer",
  url = "http://packages.python.org/html2data",
  packages=['html_jumping', 'tests'],
  long_description=read('README'),
  classifiers=[
      "Development Status :: 3 - Alpha",
      "Topic :: Utilities",
      "Intended Audience :: Developers",
      "License :: OSI Approved :: BSD License",
  ],
)
