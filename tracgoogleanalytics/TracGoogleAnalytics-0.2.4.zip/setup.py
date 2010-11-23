#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: sw=4 ts=4 fenc=utf-8 et
# ==============================================================================
# Copyright © 2008 UfSoft.org - Pedro Algarvio <ufs@ufsoft.org>
#
# Please view LICENSE for additional licensing information.
# ==============================================================================

import re
from setuptools import setup
import tracext.google.analytics as tg

setup(
    name = tg.__packagename__,
    version = tg.__version__,
    author = tg.__author__,
    author_email = tg.__email__,
    description = tg.__summary__,
    license = tg.__license__,
    url = tg.__url__,
    download_url = 'http://python.org/pypi/%s' % tg.__package__,
    long_description = re.sub(r'(\.\.[\s]*[\w]*::[\s]*[\w+]*\n)+', r'::\n',
                              open('README.txt').read()),
    packages = ['tracext', 'tracext.google', 'tracext.google.analytics'],
    namespace_packages = ['tracext', 'tracext.google'],
    package_data = {'tracext.google.analytics': ['templates/*.html',
                                                 'htdocs/*.css']},
    include_package_data = True,
    install_requires = ['Trac>=0.11'],
    keywords = "trac plugin google analytics",
    entry_points = """
    [trac.plugins]
      tracext.google.analytics = tracext.google.analytics
      tracext.google.analytics.admin = tracext.google.analytics.admin
      tracext.google.analytics.web_ui = tracext.google.analytics.web_ui
    """,
    classifiers = ['Framework :: Trac']
)
