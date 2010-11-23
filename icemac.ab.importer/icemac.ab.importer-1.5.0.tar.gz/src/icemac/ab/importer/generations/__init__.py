# Copyright (c) 2008-2010 Michael Howitz
# See also LICENSE.txt
# $Id: __init__.py 1091 2010-09-18 12:23:11Z icemac $
"""Database initialisation and upgrading."""

import zope.generations.generations


GENERATION = 0


manager = zope.generations.generations.SchemaManager(
    minimum_generation=GENERATION,
    generation=GENERATION,
    package_name='icemac.ab.importer.generations')
