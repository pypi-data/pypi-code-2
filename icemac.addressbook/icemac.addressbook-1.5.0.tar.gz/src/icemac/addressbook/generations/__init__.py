# Copyright (c) 2008-2010 Michael Howitz
# See also LICENSE.txt
# $Id: __init__.py 1152 2010-10-28 18:48:52Z icemac $
"""Database initialisation and upgrading."""

import zope.generations.generations


GENERATION = 16


manager = zope.generations.generations.SchemaManager(
    minimum_generation=GENERATION,
    generation=GENERATION,
    package_name='icemac.addressbook.generations')
