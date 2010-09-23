# -*- coding: utf-8 -*-
#
#  setup.py
#  iterxml
# 
#  Created by Lars Yencken on 13-07-2010.
#  Copyright 2010 Lars Yencken. All rights reserved.
#

from setuptools import setup

setup(
        name='iterxml',
        description="Stream data from large XML documents with minimal memory.",
        long_description = """
        Provides a method for iterating over repeated elements of large XML
        documents without storing them in memory.
        """,
        url="http://bitbucket.org/lars512/iterxml/",
        version='0.1.1',
        author="Lars Yencken",
        author_email="lljy@csse.unimelb.edu.au",
        license="BSD",
        py_modules=['iterxml'],
    )

# vim: ts=4 sw=4 sts=4 et tw=78:
