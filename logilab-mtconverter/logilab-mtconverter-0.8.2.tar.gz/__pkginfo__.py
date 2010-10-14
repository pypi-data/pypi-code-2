# copyright 2006-2010 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
# contact http://www.logilab.fr/ -- mailto:contact@logilab.fr
#
# This file is part of logilab-mtconverter.
#
# logilab-mtconverter is free software: you can redistribute it and/or modify it
# under the terms of the GNU Lesser General Public License as published by the
# Free Software Foundation, either version 2.1 of the License, or (at your
# option) any later version.
#
# logilab-mtconverter is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License
# for more details.
#
# You should have received a copy of the GNU Lesser General Public License along
# with logilab-mtconverter. If not, see <http://www.gnu.org/licenses/>.
"""mtconverter packaging information"""

modname = "mtconverter"
distname = "logilab-mtconverter"
subpackage_of = 'logilab'
numversion = (0, 8, 2)
version = '.'.join([str(num) for num in numversion])

license = 'LGPL'

author = "Sylvain Thenault"
author_email = "contact@logilab.fr"

short_desc = "a library to convert from a MIME type to another"
long_desc = """This package is originally a backport of Zope's PortalTransforms tool with
all Zope's internal removed (e.g. most of the code).
"""
web = "http://www.logilab.org/project/logilab-mtconverter"
