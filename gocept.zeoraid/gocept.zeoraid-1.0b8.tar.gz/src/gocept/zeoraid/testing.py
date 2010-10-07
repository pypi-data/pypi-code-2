##############################################################################
#
# Copyright (c) 2007-2008 Zope Foundation and Contributors.
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
"""Test harness for gocept.zeoraid."""

## Uncomment this to get helpful logging from the ZEO servers on the console
#import logging
#logging.getLogger().addHandler(logging.StreamHandler())
#logging.getLogger().setLevel(0)

import ZEO.ClientStorage


class ZEOOpener(object):

    def __init__(self, name, addr, **kwargs):
        self.name = name
        self.addr = addr
        self.kwargs = kwargs or {}

    def open(self):
        return ZEO.ClientStorage.ClientStorage(self.addr, **self.kwargs)
