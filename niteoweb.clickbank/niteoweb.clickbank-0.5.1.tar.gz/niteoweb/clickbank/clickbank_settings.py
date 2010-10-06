# -*- coding: utf-8 -*-
"""
clickbank_settings.py - store ClickBank add-on settings
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
"""

from persistent import Persistent
from zope.interface import implements

from niteoweb.clickbank.interfaces import IClickBankSettings


class ClickBankSettings(Persistent):
    """A ZCA local utility for storing information from ClickBank configuration configlet."""
    implements(IClickBankSettings)

    secret_key = ''