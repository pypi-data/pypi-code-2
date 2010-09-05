### -*- coding: utf-8 -*- ####################################################
##############################################################################
#
# Copyright (c) 2008-2009 Thierry Florac <tflorac AT ulthar.net>
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

__docformat__ = "restructuredtext"

# import standard packages

# import Zope3 interfaces

# import local interfaces
from interfaces import IForm, IDialog

# import Zope3 packages
from z3c.form import subform, button
from z3c.formui import form
from zope.event import notify
from zope.interface import implements
from zope.lifecycleevent import ObjectCreatedEvent

# import local packages

from ztfy.skin import _


class AddForm(form.AddForm):
    """Custom AddForm
    
    This form overrides creation process to allow created contents to be
    'parented' before changes to be applied. This is required for ExtFile
    properties to work correctly.
    """

    implements(IForm)

    formErrorsMessage = _('There were some errors.')

    # override button to get translated label
    @button.buttonAndHandler(_('Add'), name='add')
    def handleAdd(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return
        obj = self.createAndAdd(data)
        if obj is not None:
            # mark only as finished if we get the new object
            self._finishedAdd = True

    def update(self):
        self.subforms = self.createSubForms()
        [subform.update() for subform in self.subforms]
        super(AddForm, self).update()

    def createSubForms(self):
        return []

    def createAndAdd(self, data):
        object = self.create(data)
        notify(ObjectCreatedEvent(object))
        self.add(object)
        self.updateContent(object, data)
        return object

    def updateContent(self, object, data):
        form.applyChanges(self, object, data)


class DialogAddForm(AddForm):
    """Custom AJAX add form dialog"""

    implements(IDialog)


class EditForm(form.EditForm):
    """Custom EditForm"""

    implements(IForm)

    formErrorsMessage = _('There were some errors.')
    successMessage = _('Data successfully updated.')
    noChangesMessage = _('No changes were applied.')

    def update(self):
        self.subforms = self.createSubForms()
        [subform.update() for subform in self.subforms]
        super(EditForm, self).update()

    def createSubForms(self):
        return []


class DialogEditForm(EditForm):
    """Custom AJAX edit dialog base class"""

    implements(IDialog)


class EditSubForm(subform.EditSubForm):
    """Custom EditSubForm
    
    Actually no custom code..."""


class DisplayForm(form.DisplayForm):
    """Custom DisplayForm"""

    implements(IForm)

    def update(self):
        self.subforms = self.createSubForms()
        [subform.update() for subform in self.subforms]
        super(DisplayForm, self).update()

    def createSubForms(self):
        return []


class DialogDisplayForm(DisplayForm):
    """Custom AJAX display dialog base class"""
