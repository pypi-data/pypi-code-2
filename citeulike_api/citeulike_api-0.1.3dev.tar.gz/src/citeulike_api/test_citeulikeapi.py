#!/usr/bin/env python
# encoding: utf-8
"""
test_citeulikeapi.py

Created by dan mackinlay on 2010-12-10.
Copyright (c) 2010 __MyCompanyName__. All rights reserved.
"""

import nose
from nose.tools import *
import citeulike_api

if __name__ == '__main__':
    nose.main()

def test_keygeneration():
    """test author year title key generation"""
    source_dest = (
        ({
            "article_id": "330004",
            "title": "Information and Randomness : An Algorithmic Perspective",
            "published": ["2002"],
        }, "Anonymous2002Information", None),
        ({
            "article_id": "1296581",
            "title": "Draft Ecological Risk Assessment for the Effects of Fishing: South East Trawl and Danish Seine Fishery",
            "published": ["2004"],
            "editors": [ "Hobday", "Smith", "Stobutzki"],
        }, "Hobday2004Draft", None),
        ({
            "article_id": "1301808",
            "title": "Algorithmic information theory",
            "published": ["1987"],
            "authors": [ "Gregory J. Chaitin"],
        }, "Chaitin1987Algorithmic", None),
        ({
            "article_id": "606459",
            "username": "livingthingdan",
            "title": "The Evolution of Cooperation",
            "published": ["1985","10","01"],
            "authors": [ "Robert Axelrod"]
        },"Axelrod1985Evolution", "complex date")
    )
    for (src, dest, test_name) in source_dest:
        yield assert_equals, citeulike_api.create_key(src), dest, test_name
