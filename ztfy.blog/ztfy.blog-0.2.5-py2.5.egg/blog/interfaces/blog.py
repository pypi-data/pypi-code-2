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
from zope.app.folder.interfaces import IFolder

# import local interfaces
from category import ICategoryManagerTarget
from container import IOrderedContainer
from topic import ITopic, ITopicContainer
from ztfy.blog.interfaces import IBaseContent, IMainContent

# import Zope3 packages
from zope.app.container.constraints import contains
from zope.interface import Interface
from zope.schema import Bool, List, Object

# import local packages

from ztfy.blog import _


#
# Blog management
#

class IBlogFolder(IFolder):
    """Custom topics container"""

    contains('ztfy.blog.interfaces.blog.IBlogFolder',
             ITopic)


class IBlogInfo(IBaseContent):
    """Base blog interface"""

    visible = Bool(title=_("Visible ?"),
                   description=_("Check to keep blog visible..."),
                   default=True,
                   required=True)


class IBlogWriter(Interface):
    """Blog writer interface"""


class IBlog(IBlogInfo, IBlogWriter, ITopicContainer, IMainContent, ICategoryManagerTarget):
    """Blog full interface"""

    contains(IBlogFolder)


class IBlogContainerInfo(Interface):
    """Blog container marker interface"""

    blogs = List(title=_("Blogs list"),
                 value_type=Object(schema=IBlog),
                 readonly=True)


class IBlogContainer(IBlogContainerInfo, IOrderedContainer):
    """Blog container full interface"""
