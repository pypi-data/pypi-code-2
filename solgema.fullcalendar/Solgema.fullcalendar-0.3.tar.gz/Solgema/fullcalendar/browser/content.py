from Acquisition import aq_parent, aq_inner

from Products.CMFCore.utils import getToolByName

from plone.z3cform.layout import wrap_form

from zope.i18nmessageid import MessageFactory
from z3c.form.interfaces import INPUT_MODE, DISPLAY_MODE
from z3c.form import form as z3cform, field as z3cfield
from z3c.form import button
from z3c.formwidget.query.widget import QuerySourceFieldRadioWidget

from Solgema.fullcalendar.interfaces import ISolgemaFullcalendarProperties
PLMF = MessageFactory('plone')


class SolgemaFullcalendarFormBase( z3cform.EditForm ):


    @property
    def fields(self):
        fields = z3cfield.Fields( ISolgemaFullcalendarProperties )
        fields['target_folder'].widgetFactory[INPUT_MODE] = QuerySourceFieldRadioWidget
        return fields

    @button.buttonAndHandler(PLMF('label_save'), name='apply')
    def handleApply(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return
        changes = self.applyChanges(data)
        if changes:
            jstool = getToolByName(self.context, 'portal_javascripts')
            jstool.cookResources()
            self.status = self.successMessage
        else:
            self.status = self.noChangesMessage
        self.request.RESPONSE.redirect( self.context.absolute_url() )

    @button.buttonAndHandler(PLMF('label_cancel'), name='cancel')
    def handleCancel( self, action):
        self.request.RESPONSE.redirect( self.context.absolute_url() )

SolgemaFullcalendarForm = wrap_form(SolgemaFullcalendarFormBase)
