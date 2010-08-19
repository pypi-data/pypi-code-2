# -*- coding: latin-1 -*-
# Copyright (c) 2008-2010 Michael Howitz
# See also LICENSE.txt
# $Id: interfaces.py 1009 2010-08-15 14:20:55Z icemac $

import z3c.form.interfaces
import z3c.formui.interfaces
import z3c.layer.pagelet
import z3c.preference.interfaces


class IAddressBookLayer(
    z3c.form.interfaces.IFormLayer,
    z3c.layer.pagelet.IPageletBrowserLayer,
    z3c.preference.interfaces.IPreferenceLayer):
    """Address book browser layer with form support."""


class IAddressBookBrowserSkin(
    z3c.formui.interfaces.IDivFormLayer,
    IAddressBookLayer):
    """The address book browser skin using the div-based layout."""
