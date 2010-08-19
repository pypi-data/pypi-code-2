# -*- coding: latin-1 -*-
# Copyright (c) 2008-2010 Michael Howitz
# See also LICENSE.txt
# $Id: root.py 783 2010-01-09 14:28:06Z icemac $

import icemac.addressbook.interfaces
import z3c.pagelet.browser
import zope.size.interfaces
import zope.traversing.browser.absoluteurl


class FrontPage(z3c.pagelet.browser.BrowserPagelet):
    """Pagelet for the front page."""

    def getAddressBooks(self):
        result = []
        for ab in self.context.values():
            if not icemac.addressbook.interfaces.IAddressBook.providedBy(ab):
                # only show address books
                continue
            url = zope.traversing.browser.absoluteurl.absoluteURL(
                ab, self.request)
            result.append(dict(
                title=ab.title,
                url=url,
                delete_url=url + '/@@delete_address_book.html',
                count=zope.size.interfaces.ISized(ab).sizeForDisplay()))
        return result
