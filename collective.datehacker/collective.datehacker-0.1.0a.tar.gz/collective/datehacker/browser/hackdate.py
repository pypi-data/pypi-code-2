# -*- coding: utf-8 -*-

import re
from datetime import datetime
from DateTime import DateTime

from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from collective.datehacker import hackdateMessageFactory as _
from Products.CMFCore.utils import getToolByName

DATETIME_FORMAT = r'''^\d{4}/\d{2}/\d{2} \d{2}:\d{2}:\d{2}$'''
datetime_pattern = re.compile(DATETIME_FORMAT)
DATE_FORMAT = r'''^\d{4}/\d{2}/\d{2}$'''
date_pattern = re.compile(DATE_FORMAT)

class HackDateView(BrowserView):
    """The view for sorting folders"""

    template = ViewPageTemplateFile("hack_dates.pt")

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.request.set('disable_border', True)

    def creation_date(self):
        return self.context.created().strftime('%Y/%m/%d %H:%M:%S')

    def modification_date(self):
        return self.context.modified().strftime('%Y/%m/%d %H:%M:%S')

    def __call__(self, *args, **kw):
        if self.request.form and self.request.form.get('Save'):
            context = self.context
            putils = getToolByName(context, 'plone_utils')
            err = []
            err.append(self._validate(self.request.form.get('creation_date')))
            err.append(self._validate(self.request.form.get('modification_date')))
            stateOk = True
            for e in err:
                if e:
                    putils.addPortalMessage(e, type='error')
                    stateOk = False
                    break;
            if stateOk:
                # Now I can change dates
                # I don't use setters method because they are cmf.ManagePortal protected
                if self.request.get('creation_date'):
                    context.getField('creation_date').set(context,
                                                          context._datify(self.request.get('creation_date')))
                    context.reindexObject(idxs=['created', 'CreationDate'])
                if self.request.get('modification_date'):
                    context.getField('modification_date').set(context,
                                                              context._datify(self.request.get('modification_date')))
                    context.reindexObject(idxs=['modified', 'ModificationDate'])
                putils.addPortalMessage(_(u'Dates changed'))
            self.request.response.redirect(context.absolute_url() + '/@@hackdates')
            return
        return self.template()
    
    def _validate(self, datestr):
        """Validate a date string and return the error message, or nothing"""
        invalid = True
        if datetime_pattern.match(datestr):
            invalid = False
            d = datestr
        elif date_pattern.match(datestr):
            invalid = False
            d = datestr + ' 00:00:00'
        if invalid:
            return _('date_format_invalid',
                     default=u"The string ${date} is not in the right format. Please fill dates field "
                             u"as 'aaaa/mm/dd hh:mm:ss' or simply 'aaaa/mm/dd'.",
                     mapping={'date': datestr});
        try:
            d = (int(d[:4]), int(d[5:7]), int(d[8:10]), int(d[11:13]), int(d[14:16]), int(d[17:19]))
            datetime(*d)
        except ValueError:
            return _('date_invalid',
                     default=u"The date ${date} is an invalid date.",
                     mapping={'date': datestr});
        return None
