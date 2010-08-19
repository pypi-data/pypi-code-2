# -*- coding: latin-1 -*-
# Copyright (c) 2008-2010 Michael Howitz
# See also LICENSE.txt
# $Id: base.py 873 2010-03-19 20:23:45Z icemac $

from icemac.addressbook.i18n import MessageFactory as _
import icemac.addressbook.browser.search.interfaces
import z3c.form.button
import z3c.form.field
import z3c.formui.form
import zope.interface


class BaseView(object):

    search_params = None

    @property
    def result(self):
        if not self.search_params:
            return
        return self.search()

    def search(self):
        search = icemac.addressbook.browser.search.interfaces.ISearch(self)
        return search.search(**self.search_params)


class BaseSearchForm(z3c.formui.form.Form):

    interface = None # to be set in child class

    ignoreContext = True
    formErrorsMessage = _('There were some errors.')

    @property
    def fields(self):
        return z3c.form.field.Fields(self.interface)

    @z3c.form.button.buttonAndHandler(_('Search'), name='search')
    def search(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return
        self.__parent__.search_params = data


class BaseSearch(object):
    """Base class for search adapter."""

    zope.interface.implements(
        icemac.addressbook.browser.search.interfaces.ISearch)

    def __init__(self, *args):
        pass

    def search(self, **kw):
        raise NotImplementedError
