# Copyright (c) 2008-2011 Michael Howitz
# See also LICENSE.txt
# $Id: __init__.py 1229 2011-01-29 17:07:16Z icemac $
"""Database initialisation and upgrading."""

import zope.generations.generations


GENERATION = 16


manager = zope.generations.generations.SchemaManager(
    minimum_generation=GENERATION,
    generation=GENERATION,
    package_name='icemac.addressbook.generations')
