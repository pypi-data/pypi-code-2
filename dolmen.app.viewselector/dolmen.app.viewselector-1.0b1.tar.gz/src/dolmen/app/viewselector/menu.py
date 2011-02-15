# -*- coding: utf-8 -*-

import grokcore.component as grok
from dolmen import menu
from dolmen.app.viewselector import MF as _, IViewSelector


class SelectableViewsMenu(menu.Menu):
    grok.name('selectable-views')
    grok.title(_(u'Content display'))
    grok.context(IViewSelector)
    menu_class = u"menu additional-actions"
