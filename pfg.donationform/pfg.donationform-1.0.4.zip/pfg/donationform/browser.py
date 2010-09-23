from Acquisition import aq_base
from zope.component.factory import Factory
from zope.formlib import form
from zope.app.form.browser import TextAreaWidget
from Products.Five.formlib import formbase
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.i18nl10n import utranslate
from Products.statusmessages.interfaces import IStatusMessage
from Products.PloneFormGen.content.form import FormFolder
from getpaid.formgen.content.getpaidpfgadapter import getAvailableCreditCards

from pfg.donationform import donationformMessageFactory as _
from pfg.donationform.interfaces import IDonationFormSettings

DonationFormFactory = Factory(
    FormFolder,
    title=_(u'Create a new donation form')
    )

def ShortTextAreaWidget(field, request):
    widget = TextAreaWidget(field, request)
    widget.height = 4
    return widget

class DonationFormAddForm(formbase.AddForm):
    label = _(u'Add Donation Form')
    description = _(u'This form helps you create a PloneFormGen form to collect '
                    u'donations.  When you click the "Add" button, it will create '
                    u'a PloneFormGen form with a donation field, a GetPaid checkout '
                    u'adapter, and optionally contact and billing fields.')
    
    form_fields = form.Fields(IDonationFormSettings)
    form_fields['levels'].custom_widget = ShortTextAreaWidget
    pfg = None

    def update(self):
        mailhost = getToolByName(self.context, 'MailHost', None)
        mailhost = getattr(aq_base(mailhost), 'smtp_host', None)
        if not mailhost:
            IStatusMessage(self.request).add(
                _(u'Please configure your mailhost before adding a donation form.'))
            portal_url = getToolByName(self.context, 'portal_url')()
            return self.request.response.redirect(portal_url + '/@@mail-controlpanel')
        super(DonationFormAddForm, self).update()

    def createAndAdd(self, data):
        folder = self.context.context
        id = folder.generateUniqueId("FormFolder")
        self.pfg = form = folder[folder.invokeFactory('FormFolder', id)]
        form.setTitle(data['title'])
        form._renameAfterCreation()
        
        # delete the default form fields that come w/ PFG
        existing_ids = form.objectIds()
        deleters = ("replyto", "topic", "comments")
        deleters = [d for d in deleters if d in existing_ids]
        form.manage_delObjects(deleters)
        
        # add Donation Field for selecting donation amount and recurrence
        self.addField(form, 'donation', 'DonationFieldSet', title='Donation',
                      fgAllowRecurringPayments = True,
                      fgDonationLevels = data['levels'].splitlines())
        
        # add getpaid adapter
        gp = form[form.invokeFactory('GetpaidPFGAdapter', 'getpaid-checkout')]
        gp.setTitle('GetPaid Checkout Adapter')
        if data['create_fields']:
            gp.success_callback = "_one_page_checkout_success"
            if data['use_ssl'] and not form.absolute_url().startswith('http://nohost'):
                # force SSL unless running tests
                form.setForceSSL(True)
            
            fs = form[form.invokeFactory('FieldsetFolder', 'contact-info')]
            fs.setTitle('Contact Information')
            self.addField(fs, 'name', 'FormStringField', title='Name', required=True)
            self.addField(fs, 'email', 'FormStringField', title='E-mail', fgStringValidator='isEmail', required=True)
            self.addField(fs, 'bill_first_line', 'FormStringField', title='Street Address', required=True)
            self.addField(fs, 'bill_second_line', 'FormStringField', title='Street Address 2', hidden=True)
            self.addField(fs, 'bill_city', 'FormStringField', title='City', required=True)
            self.addField(fs, 'bill_state', 'FormStringField', title='State', fgsize=2, required=True)
            self.addField(fs, 'bill_postal_code', 'FormStringField', title='Postal Code', fgStringValidator='isZipCode', fgsize=5, required=True)
            self.addField(fs, 'bill_country', 'FormStringField', title='Country')
            self.addField(fs, 'phone_number', 'FormStringField', title='Phone', fgStringValidator='isInternationalPhoneNumber', required=True)
            
            fs = form[form.invokeFactory('FieldsetFolder', 'billing-info')]
            fs.setTitle('Billing Details')
            self.addField(fs, 'credit_card_type', 'FormSelectionField', title='Credit Card Type', fgVocabulary=getAvailableCreditCards(form), required=True)
            # XXX numeric validation
            self.addField(fs, 'credit_card', 'FormStringField', title='Credit Card Number', description='Only digits allowed - e.g. 4444555566667777 and not 4444-5555-6666-7777', required=True)
            self.addField(fs, 'name_on_card', 'FormStringField', title='Card Holder Name', description='Enter the full name, as it appears on the card.', required=True)
            self.addField(fs, 'cc_cvc', 'FormStringField', title='Credit Card Verification Number', description='For MC, Visa, and DC, this is a 3-digit number on back of the card.  For AmEx, this is a 4-digit code on front of card.', fgsize=3, fgmaxlength=4, required=True)
            self.addField(fs, 'cc_expiration', 'FormExpirationDateField', title='Credit Card Expiration Date', required=True)
            
            # make sure the mailer and thank you page don't include CC fields
            show_fields = ('name', 'email', 'bill_first_line', 'bill_second_line', 
                           'bill_city', 'bill_state', 'bill_postal_code', 'bill_country',
                           'phone_number')
            form.mailer.setShowAll(False)
            form.mailer.setShowFields(show_fields)
            form['thank-you'].setShowAll(False)
            thanks_description = utranslate(domain='pfg.donationform',
                                            msgid=_(u"Thanks for your generous donation."),
                                            context=self.request)
            form['thank-you'].setDescription(thanks_description)
        else:
            gp.success_callback = "_multi_item_cart_add_success"
            form.setThanksPageOverride('redirect_to:string:${portal_url}/@@getpaid-cart')
        
        form.setSubmitLabel('Donate')
        form.mailer.setMsg_subject('New Donation Received')
        form.reindexObject()
        self._finished_add = True

    def nextURL(self):
        if self.pfg is not None:
            return self.pfg.absolute_url()
        return formbase.AddForm.nextURL(self)

    def addField(self, folder, id, field_type, **kw):
        f = folder[folder.invokeFactory(field_type, id)]
        for k, v in kw.items():
            f.getField(k).getMutator(f)(v)
        return f
