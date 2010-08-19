# -*- coding: latin-1 -*-
# Copyright (c) 2008-2010 Michael Howitz
# See also LICENSE.txt
# $Id: evolve10.py 1009 2010-08-15 14:20:55Z icemac $

import icemac.addressbook.generations.utils


def evolve(context):
    """Install default preferences provider.
    """
    icemac.addressbook.generations.utils.update_address_book_infrastructure(
        context)

