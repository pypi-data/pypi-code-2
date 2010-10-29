# -*- coding: iso-8859-15 -*-
# Copyright (c) 2003-2006 Ingeniweb SAS

# This software is subject to the provisions of the GNU General Public
# License, Version 2.0 (GPL).  A copy of the GPL should accompany this
# distribution.  THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL
# EXPRESS OR IMPLIED WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF TITLE, MERCHANTABILITY,
# AGAINST INFRINGEMENT, AND FITNESS FOR A PARTICULAR PURPOSE

# More details in the ``LICENSE`` file included in this package.

"""
Interfaces for external usage and registering retrievers.
$Id: interfaces.py 225402 2010-10-27 16:03:38Z glenfant $
"""

__author__  = 'Gilles Lenfant <gilles.lenfant@ingeniweb.com>'
__docformat__ = 'restructuredtext'

from Interface import Interface, Attribute


class IFieldRetriever(Interface):
    """Provides binary data information on a field"""

    field_type = Attribute("The field type this retriever can handle.")

    def __init__(field, content):
        """Field and content to be managed"""

    def fileName():
        """The given file name - if any. MUST return a file name whatever happens"""

    def relativePathFrom(base_content, portal_url=None):
        """Relative path from the base content to the field id in order to
        avoid potential duplicates.
        If the base content path is /docs/basecontent' and the field has id
        'somefile' in the 'sub' subcontent, this should return '/sub/somefile'"""

    def mimeType():
        """The standard MIME type for the file like 'application/pdf' or other"""

    def fileBody():
        """The raw file data or file like object"""


class ITypeRetriever(Interface):
    """Provides binary data information on a meta_type"""

    meta_type = Attribute("The meta_type this retriever can handle")

    def __init__(content):
        """content to be managed"""

    def getFieldRetrievers():
        """Provides a sequence of IFieldRetriever objects"""

class IZipStructurePolicy(Interface):
    """
        Provides policy of inner zip structuration
    """
    id =  Attribute("policy id")
    label =  Attribute("title message")
    label_msgid =  Attribute("title message i18n id")
    help = Attribute("help message")
    help_msgid = Attribute("help message i18n id")

    def getZipFilePath(**kwargs):
        """ returns the file path in the archive """
