# -*- coding: utf-8 -*-
"""
configure_clickbank.py - configure ClickBank add-on
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
"""

from zope.component import getUtility
from zope.formlib import form

from plone.app.controlpanel.form import ControlPanelForm

from niteoweb.clickbank import ClickBankMessageFactory
from niteoweb.clickbank.interfaces import IClickBankSettings


_ = ClickBankMessageFactory

def configure_clickbank(context):
    return getUtility(IClickBankSettings)

class ConfigureClickBankForm(ControlPanelForm):
    """A ControlPanelForm BrowserView for ClickBank configuration configlet."""
    form_fields = form.Fields(IClickBankSettings)
    form_name = _("Configure ClickBank")
    label = _(u"Configure ClickBank add-on")
    description = _(u"Enter your ClickBank settings.")