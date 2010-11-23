# -*- coding: latin-1 -*-
# Copyright (c) 2008-2010 Michael Howitz
# See also LICENSE.txt
# $Id: evolve11.py 1183 2010-11-23 17:17:09Z icemac $

import icemac.addressbook.generations.utils


def evolve(context):
    """Install batch size in default preferences provider.
    """
    icemac.addressbook.generations.utils.update_address_book_infrastructure(
        context)
