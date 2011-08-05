##############################################################################
#
# Copyright (c) 2006 ROBOTECH Logistiksysteme GmbH
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
from zope import interface
from zope import schema
from zope.configuration.fields import GlobalObject


class IEngineDirective(interface.Interface):
    """Define an engine.
    """
    url = schema.URI(
        title = u'Databse URL',
        description = u'RFC-1738 compliant URL for the database connection',
        required = True,
        )
    name = schema.Text(
            title = u'Engine name',
            description = u'Empty if this engine is the default engine.',
            required = False,
            default = u'',
            )
    echo = schema.Bool(
            title = u'Echo SQL statements',
            required = False,
            default=False
            )

# Arbitrary keys and values are allowed to be passed to the engine.
IEngineDirective.setTaggedValue('keyword_arguments', True)


class ITableConnectDirective(interface.Interface):
    """Connect a table to an engine.

    This is only neccessary if a table should not be uses in the default
    database.
    """
    table = schema.TextLine(
            title = u'Table',
            description = u'The name of the table to connect an engine to.',
            required = True,
            )
    engine = schema.TextLine(
            title = u'Engine',
            description = u'The name of an engine to connect the table to.',
            required = True,
            )


class IClassConnectDirective(interface.Interface):
    """Connect a class to an engine.

    This is only neccessary if a class should not be uses in the default
    database.

    The class must be mapped to a table.
    """
    class_ = GlobalObject(
            title = u'Class',
            description = u'The class to connect an engine to.',
            required = True,
            )
    engine = schema.TextLine(
            title = u'Engine',
            description = u'The name of an engine to connect the table to.',
            required = True,
            )


class ICreateTableDirective(interface.Interface):
    """Create a table if not exist.
    """
    table = schema.TextLine(
            title = u'Table',
            description = u'The name of the table.',
            required = True,
            )
    engine = schema.TextLine(
            title = u'Engine',
            description = u"""
                The name of an engine in which the table should be
                created.
                """,
            required = True,
            )

