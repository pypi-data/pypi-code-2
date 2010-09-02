### -*- coding: utf-8 -*- ####################################################
##############################################################################
#
# Copyright (c) 2008-2010 Thierry Florac <tflorac AT ulthar.net>
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

__docformat__ = "restructuredtext"

# import standard packages

# import Zope3 interfaces

# import local interfaces

# import Zope3 packages

# import local packages
from ztfy.blog.crontab.zodb import ZODBPackingTask
from ztfy.skin.menu import MenuItem
from ztfy.scheduler.browser.task import BaseTaskAddForm

from ztfy.blog import _


class ZODBPackingTaskAddFormMenu(MenuItem):
    """ZODB packing task add form menu"""

    _title = _(" :: Add ZODB packing task...")


class ZODBPackingTaskAddForm(BaseTaskAddForm):
    """ZODB packing task add form"""

    def create(self, data):
        return ZODBPackingTask()
