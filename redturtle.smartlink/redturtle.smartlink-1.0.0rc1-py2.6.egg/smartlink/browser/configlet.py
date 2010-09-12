# -*- coding: utf-8 -*-

from zope.formlib import form
from plone.app.controlpanel.form import ControlPanelForm
from redturtle.smartlink.interfaces.utility import ISmartlinkConfig
from redturtle.smartlink import smartlinkMessageFactory as _
from plone.protect import CheckAuthenticator
from plone.app.form.validators import null_validator
from Products.statusmessages.interfaces import IStatusMessage
from zope.component import getMultiAdapter
from redturtle.smartlink.interfaces import ISmartLink


class SmartlinkConfigForm(ControlPanelForm):
    """Smartlink Control Panel Form"""

    form_fields = form.Fields(ISmartlinkConfig)

    label = _(u"Smart Link configuration")
    description = _((u"Enter a list of front-end links and a list of their appropriate back-end links. "
                     u"Each front-end link matches to the link that occupies the same position in the list of back-end. "
                     u"The number of elements of the lists must be the same."))
    form_name = _(u"Settings")

    def saveFields(self, action, data):
        CheckAuthenticator(self.request)
        if form.applyChanges(self.context, self.form_fields, data,
                             self.adapters):
            self.status = _(u"Changes saved.")
            self._on_save(data)
        else:
            self.status = _(u"No changes made.")

    @form.action(_(u'label_save_links', default=u'Save'), name=u'save')
    def handle_edit_action(self, action, data):
        self.saveFields(action, data)

    @form.action(_(u'label_cancel_links', default=u'Cancel'),
                 validator=null_validator,
                 name=u'cancel')
    def handle_cancel_action(self, action, data):
        IStatusMessage(self.request).addStatusMessage(_("Changes canceled."),
                                                      type="info")
        url = getMultiAdapter((self.context, self.request),
                              name='absolute_url')()
        self.request.response.redirect(url + '/@@smartlink-config')
        return ''

    @form.action(_(u'label_update_links', default=u'Update existing links'), name=u'update_links')
    def action_update(self, action, data):
        results = self.context.portal_catalog(object_provides=ISmartLink.__identifier__)
        for res in results:
            object = res.getObject()
            object.setRemoteUrl(object.getRemoteUrl())
            object.reindexObject()
        return
