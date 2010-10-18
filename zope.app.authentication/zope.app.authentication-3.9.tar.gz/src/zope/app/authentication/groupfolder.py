##############################################################################
#
# Copyright (c) 2004 Zope Foundation and Contributors.
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
"""Zope Groups Folder implementation

$Id: groupfolder.py 117633 2010-10-18 09:40:31Z janwijbrand $

"""
# BBB using zope.pluggableauth.plugin.groupfolder
from zope.pluggableauth.plugins.groupfolder import (
    GroupCycle,
    GroupFolder,
    GroupInfo,
    GroupInformation,
    IGroupContained,
    IGroupFolder,
    IGroupInformation,
    IGroupPrincipalInfo,
    IGroupSearchCriteria,
    InvalidGroupId,
    InvalidPrincipalIds,
    nocycles,
    setGroupsForPrincipal,
    setMemberSubscriber,
    specialGroups,
    )
