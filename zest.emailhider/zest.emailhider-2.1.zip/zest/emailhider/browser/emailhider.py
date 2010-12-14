from zope.component import getMultiAdapter
from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName
from zest.emailhider.interfaces import IMailable

from jquery.pyproxy.plone import jquery, JQueryProxy
from jquery.pyproxy.base import clean_string


class EmailHider(BrowserView):

    def UID(self):
        mailable = IMailable(self.context, None)
        if mailable is None:
            return
        return mailable.UID()

    def email(self):
        mailable = IMailable(self.context, None)
        if mailable is None:
            return
        return mailable.email


class JqEmailHider(BrowserView):
    """jQuery view for revealing the email address of an object.

    The object is given by a uid.

    Objects should have a simple adapter to the IMailable interface,
    so we can ask this adapter for an 'email' attribute.

    Special case: when the uid is 'email_from_address', we do nothing
    with the IMailable interface but just get the email_from_address
    from the portal property.
    """

    @jquery
    def reveal_email(self):
        uid = self.request.form.get('uid', None)
        if not uid:
            return

        if uid == 'email_from_address':
            portal_state = getMultiAdapter((self.context, self.request),
                                            name=u'plone_portal_state')
            portal = portal_state.portal()
            email = portal.getProperty('email_from_address')
        else:
            # Find object by uid
            catalog = getToolByName(self.context, 'uid_catalog')
            brains = catalog(UID=uid)
            if len(brains) != 1:
                return
            target = brains[0].getObject()
            mailable = IMailable(target, None)
            if mailable is None:
                return
            email = mailable.email

        email_link = u'<a href="mailto:%s">%s</a>' % (email, email)
        jq = JQueryProxy()
        jq('.email-uid-%s' % uid).replaceWith(clean_string(email_link))

        return jq
