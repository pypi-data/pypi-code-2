##############################################################################
#
# Copyright (c) 2006 ROBOTECH Logistiksysteme GmbH and Contributors.
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

import zope.deferredimport

zope.deferredimport.define(
    getSession='z3c.zalchemy.datamanager:getSession',
    inSession='z3c.zalchemy.datamanager:inSession',
    assignTable='z3c.zalchemy.datamanager:assignTable',
    assignClass='z3c.zalchemy.datamanager:assignClass',
    createTable='z3c.zalchemy.datamanager:createTable',
    metadata='z3c.zalchemy.datamanager:metadata',
    getEngineForTable='z3c.zalchemy.datamanager:getEngineForTable')


import zope.i18nmessageid

_ = zope.i18nmessageid.MessageFactory('z3c.zalchemy')

