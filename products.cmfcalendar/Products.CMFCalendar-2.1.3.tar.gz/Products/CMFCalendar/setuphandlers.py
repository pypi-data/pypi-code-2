##############################################################################
#
# Copyright (c) 2005 Zope Foundation and Contributors.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
""" CMFCalendar setup handlers.

$Id: setuphandlers.py 110663 2010-04-08 15:59:45Z tseaver $
"""

from zope.component import getUtility

from Products.CMFCore.interfaces import IMetadataTool

from exceptions import MetadataError


def importVarious(context):
    """ Import various settings for CMF Calendar.

    This provisional handler will be removed again as soon as full handlers
    are implemented for these steps.
    """
    site = context.getSite()
    mdtool = getUtility(IMetadataTool)

    # Set up a MetadataTool element policy for events
    try:
        _ = str # MetadataTool ist not aware of Message objects
        mdtool.DCMI.addElementPolicy(
            element='Subject',
            content_type='Event',
            is_required=0,
            supply_default=0,
            default_value='',
            enforce_vocabulary=0,
            allowed_vocabulary=(_('Appointment'),
                                _('Convention'),
                                _('Meeting'),
                                _('Social Event'),
                                _('Work'),
                               ),
            REQUEST=None)
    except MetadataError:
        pass

    return 'Various settings for CMF Calendar imported.'
