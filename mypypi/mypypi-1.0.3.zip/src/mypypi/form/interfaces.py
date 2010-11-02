##############################################################################
#
# Copyright (c) 2009 Projekt01 GmbH and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################

from z3c.form import interfaces


class ITextLinesWidget(interfaces.IWidget):
    """Text lines widget."""


class IMultiWidget(interfaces.IWidget):
    """None Term based sequence widget base.

    The multi widget is used for ITuple or IList if no other widget is defined.

    Some IList or ITuple are using another specialized widget if they can
    choose from a collection. e.g. a IList of IChoice. The base class of such
    widget is the ISequenceWidget.

    This widget can handle none collection based sequences and offers add or
    remove values to or from the sequence. Each sequence value get rendered by
    it's own relevant widget. e.g. IList of ITextLine or ITuple of IInt
    """
