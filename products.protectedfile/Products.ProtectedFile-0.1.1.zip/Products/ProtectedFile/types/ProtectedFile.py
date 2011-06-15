from DateTime import DateTime
from urllib import quote_plus
from AccessControl import ClassSecurityInfo
from ComputedAttribute import ComputedAttribute
try:
    from persistent.mapping import PersistentMapping
except ImportException:
    from PersistentMapping import PersistentMapping
try:
    from Products.CMFCore.permissions import View
except ImportError:
    from Products.CMFCore.CMFCorePermissions import View
from Products.Archetypes.public import *
from Products.ATContentTypes.content.file import ATFile, ATFileSchema
from Products.ProtectedFile.config import PROJECTNAME
from Products.ProtectedFile.utils import KeyManager
from Products.CMFCore.utils import getToolByName


class ProtectedFile(ATFile):
    """Protected File.
    """

    schema = ATFileSchema.copy()
    meta_type = portal_type = archetype_name = 'Protected File'
    default_view = immediate_view = 'protectedfile_view'
    security = ClassSecurityInfo()

    actions = (
        {
            'id' : 'email_list',
            'name' : 'E-Mail Listing',
            'action' : 'string:${object_url}/protectedfile_email_list',
            'condition' : 'member',
            'permissions' : (View, ),
        },
    )

    def __init__(self, *args, **kw):
        """Initializes the keys mapping.
        """
        ProtectedFile.inheritedAttribute('__init__')(self, *args, **kw)
        self._keys = PersistentMapping()

    security.declarePrivate('getKeys')
    def getKeys(self):
        """Returns the keys mapping.
        """
        return self._keys

    security.declarePrivate('getKey')
    def getKey(self, key):
        """Returns the requested key token.
        """
        return self.getKeys().get(key)

    security.declarePrivate('purgeOldPendingList')
    def purgeOldPendingList(self):
        """Romoves all not downloaded keys older than a week.
        """
        oneWeekAgo = DateTime() - 7
        keys = self.getKeys()
        for key in keys.keys():
           if not self.isConfirmedKey(key):
                token = self.getKey(key)
                if token.get('timestamp') < oneWeekAgo:
                    del keys[key]

    security.declarePrivate('isConfirmedKey')
    def isConfirmedKey(self, key):
        """Checks if a key is confirmed (used to download).
        """
        if key in self.getKeys().keys():
            token = self.getKey(key)
            return token.get('downloads') > 0
        return False

    security.declareProtected(View, 'confirmKey')
    def confirmKey(self, key):
        """Confirms that the key was used for download.
        """
        if not self.getKeys().has_key(key):
            return False
        token = self.getKey(key)
        downloads = token.get('downloads')
        token.update({'downloads' : downloads + 1})
        self.purgeOldPendingList()
        return True

    security.declareProtected(View, 'addToken')
    def addToken(self, email):
        """Adds an email address with current timestamp to the pending list.
        Returns the related key.
        """
        key = KeyManager().generate()
        # Assure unique keys
        while key in self.getKeys().keys():
            key = KeyManager().generate()
        token = PersistentMapping({
            'email' : email,
            'timestamp' : DateTime(),
            'downloads' : 0,
        })
        self.getKeys().setdefault(key, token)
        return key

    security.declareProtected(View, 'sendFileAddressMail')
    def sendFileAddressMail(self, email, key):
        """Send a mail informing the URI to download the file.
        """
        # Rather than have the template try to use the mailhost, we will
        # render the message ourselves and send it from here (where we
        # don't need to worry about 'UseMailHost' permissions).
        mail_text = self.mail_file_address_template(self, email=email, key=key)
        host = self.MailHost
        mto = email
        mfrom = host.aq_inner.aq_parent.getProperty('email_from_address')
        subject = "Download address for %s" % quote_plus(self.title_or_id())
        try:
            host.secureSend(mail_text, mto=mto, mfrom=mfrom, subject=subject)
        except:
            host.simple_send(email, mfrom,subject, mail_text)

    security.declareProtected(View, 'listTokens')
    def listTokens(self):
        """Returns the confirmed tokens list.
        """
        list = []
        for key in self.getKeys().keys():
            if self.isConfirmedKey(key):
                # Remove Access Restrictions from PersistentMapping
                token = dict(self.getKey(key))
                token.setdefault('key', key)
                list.append(token)
        return list

    security.declareProtected(View, 'listEmails')
    def listEmails(self):
        """Returns the confirmed unique emails list.
        """
        list = []
        for token in self.listTokens():
            list.append(token.get('email'))
        uniqueList = dict.fromkeys(list).keys()
        return uniqueList

    security.declareProtected(View, 'listEmails')
    def countEmails(self):
        """Returns the number of confirmed unique emails.
        """
        return len(self.listEmails())

    security.declareProtected(View, 'index_html')
    def index_html(self, REQUEST, RESPONSE, key=None):
        """Returns the file contents if you have a good key.
        """
        mtool = getToolByName(self, 'portal_membership')
        if mtool.isAnonymousUser() and not self.isConfirmedKey(key):
            return self.view()
        return ProtectedFile.inheritedAttribute('index_html')(self, REQUEST, RESPONSE)

    security.declareProtected(View, 'download')
    def download(self, REQUEST, RESPONSE, key=None):
        """Downloads the file if you have a good key.
        """
        mtool = getToolByName(self, 'portal_membership')
        if mtool.isAnonymousUser() and not self.confirmKey(key):
            return self.view()
        return ProtectedFile.inheritedAttribute('download')(self, REQUEST, RESPONSE)

    security.declareProtected(View, 'get_data')
    def get_data(self, key=None):
        """Restricts the get_data method.
        """
        if key is None:
            key = self.REQUEST.get('key')
        mtool = getToolByName(self, 'portal_membership')
        if mtool.isAnonymousUser() and not self.isConfirmedKey(key):
            return None
        return ProtectedFile.inheritedAttribute('get_data')(self)

    security.declareProtected(View, 'data')
    data = ComputedAttribute(get_data, 1)


registerType(ProtectedFile, PROJECTNAME)
