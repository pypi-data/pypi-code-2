try:
    import hashlib
except ImportError:
    import md5
from Acquisition import aq_inner, aq_parent
#from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode
from Products.statusmessages.interfaces import IStatusMessage

class Miscellaneous(BrowserView):

    def verkkomaksut_canceled(self):
        context = aq_inner(self.context)
        message = safe_unicode(context.getCancel_message())
        IStatusMessage(self.request).addStatusMessage(message, type='info')
        url = aq_parent(context).absolute_url()
        self.request.response.redirect(url)

    def verkkomaksut_on_success(self, fields, REQUEST):
        context = aq_inner(self.context) 
        order_number = context.getNext_order_number()
        ORDER_NUMBER = str(order_number)
        # Increase next_order_number by one.
        context.setNext_order_number(order_number + 1)
        REQUEST.set('ORDER_NUMBER', ORDER_NUMBER)
        if context.getMsg_necessary():
            context.send_form(fields, REQUEST)
        field = context.selected_price_field()
        form = context.REQUEST.form
        price = form.get(field)
        MERCHANT_ID = str(context.getMerchant_id())
        AMOUNT = price
        ORDER_DESCRIPTION = context.order_description(fields, REQUEST)
        CURRENCY = 'EUR'
#        portal = getToolByName(context, 'portal_url').getPortalObject()
#        portal_url = portal.absolute_url()
        parent = aq_parent(aq_inner(context))
#        ids = parent.objectIds()
#        ids = [id for id in ids if id in form.keys()]
#        queries = ['&'+id+'='+form.get(id) for id in ids if form.get(id) is not None][1:]
#        query = '?'+ids[0]+'='+form.get(ids[0])+''.join(queries)
        parent_url = parent.absolute_url()
        return_url = '%s/@@verkkomaksut-success' % (parent_url)
#        message = 'AAA'
#        IStatusMessage(REQUEST).addStatusMessage(message, type='info')
#        parent.plone_utils.addPortalMessage(_(u'AAA'))
#        cancel_url = '%s?portal_status_message=%s'%(parent_url, context.getCancel_message())
        cancel_url = '%s/@@verkkomaksut-canceled' %(context.absolute_url())
        notify_url = '%s/@@verkkomaksut-notify' % (context.absolute_url())
#        notify_url = '%s/verkkomaksutnotify%s' % (context.absolute_url(), query)
        RETURN_ADDRESS = return_url
        CANCEL_ADDRESS = cancel_url
        NOTIFY_ADDRESS = notify_url
        TYPE = 'S1'
        CULTURE = 'fi_FI'
        MODE = '1'

        ADAPTER_UID = context.UID()

        sdm = getToolByName(context, 'session_data_manager')
        session = sdm.getSessionData(create=True)

#        m = md5.new()
        try:
            m = hashlib.md5()
        except:
            m = md5.new()
        m.update(context.getMerchant_authentication_code())
        ## For TYPE S1
        m.update('|' + MERCHANT_ID)
        m.update('|' + AMOUNT)
        m.update('|' + ORDER_NUMBER)
        m.update('||' + ORDER_DESCRIPTION)
        m.update('|' + CURRENCY)
        m.update('|' + RETURN_ADDRESS)
        m.update('|' + CANCEL_ADDRESS)
        m.update('||' + NOTIFY_ADDRESS)
        m.update('|' + TYPE)
        m.update('|' + CULTURE)
        m.update('||' + MODE + '||')
        auth_code = m.hexdigest()
        AUTHCODE = auth_code.upper()

        value = dict(
            MERCHANT_ID = MERCHANT_ID,
            AMOUNT = AMOUNT,
            ORDER_NUMBER = ORDER_NUMBER,
            ORDER_DESCRIPTION = ORDER_DESCRIPTION,
            CURRENCY = CURRENCY,
            RETURN_ADDRESS = RETURN_ADDRESS,
            CANCEL_ADDRESS = CANCEL_ADDRESS,
            NOTIFY_ADDRESS = NOTIFY_ADDRESS,
            TYPE = TYPE,
            CULTURE = CULTURE,
            MODE = MODE,
            AUTHCODE = AUTHCODE,
            ADAPTER_UID = ADAPTER_UID,
        )

        session.set('pfg.verkkomaksut', value)
        session.set('pfg.verkkomaksut.fields', context.displayInputs(REQUEST))


#        url = '%s/verkkomaksut' % parent_url
        url = '%s/@@verkkomaksut' % parent_url
#        url = '%s/@@verkkomaksut' % getToolByName(context, 'portal_url').getPortalObject().absolute_url()
        return context.REQUEST.RESPONSE.redirect(url)


    def verkkomaksut_notify(self):
        pass
