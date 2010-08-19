# -*- coding: latin-1 -*-
# Copyright (c) 2008-2010 Michael Howitz
# See also LICENSE.txt
# $Id: evolve3.py 783 2010-01-09 14:28:06Z icemac $

__docformat__ = "reStructuredText"


import icemac.addressbook.generations.utils


generation = 3


def evolve(context):
    """Installs the authentication utility.
    """
    icemac.addressbook.generations.utils.update_address_book_infrastructure(
        context)
