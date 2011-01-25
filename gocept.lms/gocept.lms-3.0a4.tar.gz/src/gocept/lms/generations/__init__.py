# -*- coding: latin-1 -*-
# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id: __init__.py 1726 2009-02-03 13:26:25Z ctheune $

import zope.app.generations.generations

SchemaManager = zope.app.generations.generations.SchemaManager(
    minimum_generation=1, generation=1,package_name=__name__)
