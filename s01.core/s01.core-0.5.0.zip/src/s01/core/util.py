###############################################################################
#
# Copyright (c) 2011 Projekt01 GmbH and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
###############################################################################
"""mongodb configuration helper

$Id:$
"""
__docformat__ = "reStructuredText"

import os

from zope.app.appsetup.product import getProductConfiguration


def getConfig(product, confKey, envKey, required=True):
    """Get product configuration based on zope.app.appsetup or env variable."""
    value = None
    config = getProductConfiguration(product)
    if config is not None:
        value = config.get(confKey)
    else:
        value = os.environ.get(envKey)
    if value is None and required:
        raise ValueError(
            "You must define '%s' product config '%s' in buildout.cfg" % (
                confKey, product))
    if value:
        return unicode(value)


def asBool(obj):
    if isinstance(obj, basestring):
        obj = obj.lower()
        if obj in ('1', 'true', 'yes', 't', 'y'):
            return True
        if obj in ('0', 'false', 'no', 'f', 'n'):
            return False
    return bool(obj)
