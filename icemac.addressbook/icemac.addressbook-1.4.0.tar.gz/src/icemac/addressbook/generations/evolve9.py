# -*- coding: latin-1 -*-
# Copyright (c) 2008-2010 Michael Howitz
# See also LICENSE.txt
# $Id: evolve9.py 865 2010-03-07 15:52:31Z icemac $

__docformat__ = "reStructuredText"


import icemac.addressbook.generations.utils


generation = 9


def evolve(context):
    """Install orders utility.
    """
    icemac.addressbook.generations.utils.update_address_book_infrastructure(
        context)

