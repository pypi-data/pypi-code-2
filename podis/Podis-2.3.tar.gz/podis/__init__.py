# -*- coding: utf-8 -*-


# Podis -- Retrieve INSEE codes of french communes from their postal distributions
# By: Romain Soufflet <rsoufflet@easter-eggs.com>
#
# Copyright (C) 2010 Easter-eggs
#
# This file is part of Podis.
#
# Podis is free software; you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# Podis is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


"""Retrieve INSEE codes of french communes from their postal distributions"""


import os
import pymongo


collection_name = 'podis'
db = None # To initialize before using Podis.


def setup_db():
    """Setup MongoDb database."""
    collection = db[collection_name]
    # If indexes already exists, ensure_index ignore 'sparse' value
    collection.drop_indexes()

    collection.ensure_index('territory.code')
    collection.ensure_index('common_code')
    collection.ensure_index('simple_name')
    collection.ensure_index([('common_code', pymongo.ASCENDING), ('simple_name', pymongo.ASCENDING)])
    collection.ensure_index('simple_words')

    collection.ensure_index('bounding_territories.code')
    collection.ensure_index('bounding_territories.kind')

    # index for sort result of autocompleter
    collection.ensure_index([
        ('highest_score', pymongo.DESCENDING),
        ('pobox_ratio', pymongo.ASCENDING),
        ('population', pymongo.DESCENDING),
        ('simple_name', pymongo.ASCENDING),
        ('common_code', pymongo.ASCENDING),
        ])

    # Add levenshtein as a stored function
    with open(os.path.join(os.path.dirname(__file__), 'js/levenshtein_min.js'), 'r') as js_file:
        db.system_js.levenshtein = js_file.read()

