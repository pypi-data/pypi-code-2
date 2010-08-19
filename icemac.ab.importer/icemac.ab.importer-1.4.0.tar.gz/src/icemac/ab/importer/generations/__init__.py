# Copyright (c) 2008-2010 Michael Howitz
# See also LICENSE.txt
# $Id: __init__.py 781 2010-01-09 14:24:30Z icemac $
"""Database initialisation and upgrading."""

import zope.app.generations.generations


GENERATION = 0


manager = zope.app.generations.generations.SchemaManager(
    minimum_generation=GENERATION,
    generation=GENERATION,
    package_name='icemac.ab.importer.generations')
