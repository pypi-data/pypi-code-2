from StringIO import StringIO
from zope.component import getSiteManager
from Products.CMFCore.utils import getToolByName
from Products.MailHost.interfaces import IMailHost
from Products.MailHost.MailHost import MailHost
from plone.app.upgrade.utils import logger

def beforeUninstall(self, reinstall=False, product=None, cascade=[]):
    tool = getToolByName(self, 'MailHost')
    try:
        cascade.remove('utilities')
    except ValueError:
        pass
    return True, cascade

def uninstall(self):
    out = StringIO()
    print >> out, "Removing langMailHost"

    mh = getToolByName(self, 'MailHost', None)
    if mh is None:
        return

    # Migrate secure mail host and broken mail host objects
    meta_type = getattr(mh, 'meta_type', None)
    if meta_type == 'Broken Because Product is Gone':
        new_mh = MailHost(id='MailHost', smtp_host='')
        logger.info('Replaced a broken MailHost object.')
    else:
        new_mh = MailHost(
            id=mh.id,
            title=mh.title,
            smtp_host=mh.smtp_host,
            smtp_port=mh.smtp_port,
            smtp_uid=mh.smtp_uid or '',
            smtp_pwd=mh.smtp_pwd or '',
            force_tls=False,
        )
    self._delObject('MailHost')
    self._setObject('MailHost', new_mh)
    sm = getSiteManager(context=self)
    sm.unregisterUtility(provided=IMailHost)
    sm.registerUtility(new_mh, provided=IMailHost)


    return out.getvalue()
