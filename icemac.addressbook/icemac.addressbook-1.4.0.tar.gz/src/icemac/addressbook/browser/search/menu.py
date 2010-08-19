# -*- coding: latin-1 -*-
# Copyright (c) 2008-2010 Michael Howitz
# See also LICENSE.txt
# $Id: menu.py 783 2010-01-09 14:28:06Z icemac $

import zope.viewlet.manager
import z3c.menu.ready2go
import z3c.menu.ready2go.manager


SearchMenu = zope.viewlet.manager.ViewletManager(
    'left', z3c.menu.ready2go.IContextMenu, 
    bases=(z3c.menu.ready2go.manager.MenuManager,))
