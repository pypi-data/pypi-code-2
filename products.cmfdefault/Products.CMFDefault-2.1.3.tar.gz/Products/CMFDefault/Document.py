##############################################################################
#
# Copyright (c) 2001 Zope Foundation and Contributors.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
""" Basic textual content object, supporting HTML, STX and plain text.

$Id: Document.py 110659 2010-04-08 15:54:42Z tseaver $
"""

import transaction
from AccessControl import ClassSecurityInfo
from AccessControl import getSecurityManager
from Acquisition import aq_base
from DocumentTemplate.DT_Util import html_quote
from Globals import DTMLFile
from Globals import InitializeClass
from StructuredText.StructuredText import HTML
from zope.component.factory import Factory
from zope.interface import implements

from Products.CMFCore.PortalContent import PortalContent
from Products.CMFCore.utils import contributorsplitter
from Products.CMFCore.utils import keywordsplitter
from Products.GenericSetup.interfaces import IDAVAware

from DublinCore import DefaultDublinCoreImpl
from exceptions import EditingConflict
from exceptions import ResourceLockedError
from interfaces import IDocument
from interfaces import IMutableDocument
from interfaces.Document import IDocument as z2IDocument
from interfaces.Document import IMutableDocument as z2IMutableDocument
from permissions import ModifyPortalContent
from permissions import View
from utils import _dtmldir
from utils import bodyfinder
from utils import formatRFC822Headers
from utils import html_headcheck
from utils import Message as _
from utils import parseHeadersBody
from utils import SimpleHTMLParser


def addDocument(self, id, title='', description='', text_format='', text=''):
    """Add a Document.
    """
    o = Document(id, title, description, text_format, text)
    self._setObject(id,o)


class Document(PortalContent, DefaultDublinCoreImpl):

    """A Document - Handles both StructuredText and HTML.
    """

    implements(IMutableDocument, IDocument, IDAVAware)
    __implements__ = (z2IMutableDocument, z2IDocument,
                      PortalContent.__implements__,
                      DefaultDublinCoreImpl.__implements__)

    effective_date = expiration_date = None
    cooked_text = text = text_format = ''
    _size = 0

    _stx_level = 1                      # Structured text level

    _last_safety_belt_editor = ''
    _last_safety_belt = ''
    _safety_belt = ''

    security = ClassSecurityInfo()

    def __init__(self, id, title='', description='', text_format='', text=''):
        DefaultDublinCoreImpl.__init__(self)
        self.id = id
        self.title = title
        self.description = description
        self.setFormat(text_format)
        self._edit(text)

    security.declareProtected(ModifyPortalContent, 'manage_edit')
    manage_edit = DTMLFile('zmi_editDocument', _dtmldir)

    security.declareProtected(ModifyPortalContent, 'manage_editDocument')
    def manage_editDocument( self, text, text_format, file='', REQUEST=None ):
        """ A ZMI (Zope Management Interface) level editing method """
        Document.edit( self, text_format=text_format, text=text, file=file )
        if REQUEST is not None:
            REQUEST['RESPONSE'].redirect(
                self.absolute_url()
                + '/manage_edit'
                + '?manage_tabs_message=Document+updated'
                )

    def _edit(self, text):
        """ Edit the Document and cook the body.
        """
        self.text = text
        self._size = len(text)

        text_format = self.text_format
        if text_format == 'html':
            self.cooked_text = text
        elif text_format == 'plain':
            self.cooked_text = html_quote(text).replace('\n', '<br />')
        else:
            self.cooked_text = HTML(text, level=self._stx_level, header=0)

    #
    #   IMutableDocument method
    #

    security.declareProtected(ModifyPortalContent, 'edit')
    def edit(self, text_format, text, file='', safety_belt=''):
        """ Update the document.

        To add webDav support, we need to check if the content is locked, and if
        so return ResourceLockedError if not, call _edit.

        Note that this method expects to be called from a web form, and so
        disables header processing
        """
        self.failIfLocked()
        if not self._safety_belt_update(safety_belt=safety_belt):
            msg = _(u'Intervening changes from elsewhere detected. '
                    u'Please refetch the document and reapply your changes. '
                    u'(You may be able to recover your version using the '
                    u"browser 'back' button, but will have to apply them to "
                    u'a freshly fetched copy.)')
            raise EditingConflict(msg)
        if file and (type(file) is not type('')):
            contents=file.read()
            if contents:
                text = contents
        if html_headcheck(text) and text_format.lower() != 'plain':
            text = bodyfinder(text)
        self.setFormat(text_format)
        self._edit(text)
        self.reindexObject()

    security.declareProtected(ModifyPortalContent, 'setMetadata')
    def setMetadata(self, headers):
        headers['Format'] = self.Format()
        new_subject = keywordsplitter(headers)
        headers['Subject'] = new_subject or self.Subject()
        new_contrib = contributorsplitter(headers)
        headers['Contributors'] = new_contrib or self.Contributors()
        for key, value in self.getMetadataHeaders():
            if not key in headers:
                headers[key] = value
        self._editMetadata(title=headers['Title'],
                          subject=headers['Subject'],
                          description=headers['Description'],
                          contributors=headers['Contributors'],
                          effective_date=headers['Effective_date'],
                          expiration_date=headers['Expiration_date'],
                          format=headers['Format'],
                          language=headers['Language'],
                          rights=headers['Rights'],
                          )

    security.declarePrivate('guessFormat')
    def guessFormat(self, text):
        """ Simple stab at guessing the inner format of the text """
        if html_headcheck(text): return 'html'
        else: return 'structured-text'

    security.declarePrivate('handleText')
    def handleText(self, text, format=None, stx_level=None):
        """ Handles the raw text, returning headers, body, format """
        headers = {}
        if not format:
            format = self.guessFormat(text)
        if format == 'html':
            parser = SimpleHTMLParser()
            parser.feed(text)
            headers.update(parser.metatags)
            if parser.title:
                headers['Title'] = parser.title
            body = bodyfinder(text)
        else:
            headers, body = parseHeadersBody(text, headers)
            if stx_level:
                self._stx_level = stx_level
        return headers, body, format

    security.declarePublic( 'getMetadataHeaders' )
    def getMetadataHeaders(self):
        """Return RFC-822-style header spec."""
        hdrlist = DefaultDublinCoreImpl.getMetadataHeaders(self)
        hdrlist.append( ('SafetyBelt', self._safety_belt) )
        return hdrlist

    security.declarePublic( 'SafetyBelt' )
    def SafetyBelt(self):
        """Return the current safety belt setting.
        For web form hidden button."""
        return self._safety_belt

    security.declarePrivate('isValidSafetyBelt')
    def isValidSafetyBelt(self, safety_belt):
        """Check validity of safety belt.
        """
        if not safety_belt:
            # we have no safety belt value
            return True
        if self._safety_belt is None:
            # the current object has no safety belt (ie - freshly made)
            return True
        if safety_belt == self._safety_belt:
            # the safety belt does match the current one
            return True
        this_user = getSecurityManager().getUser().getId()
        if ((safety_belt == self._last_safety_belt)
                and (this_user == self._last_safety_belt_editor)):
            # safety belt and user match last safety belt and user
            return True
        return False

    security.declarePrivate('updateSafetyBelt')
    def updateSafetyBelt(self, safety_belt):
        """Update safety belt tracking.
        """
        this_user = getSecurityManager().getUser().getId()
        self._last_safety_belt_editor = this_user
        self._last_safety_belt = safety_belt
        self._safety_belt = str(self._p_mtime)

    def _safety_belt_update(self, safety_belt=''):
        """Check validity of safety belt and update tracking if valid.

        Return 0 if safety belt is invalid, 1 otherwise.

        Note that the policy is deliberately lax if no safety belt value is
        present - "you're on your own if you don't use your safety belt".

        When present, either the safety belt token:
         - ... is the same as the current one given out, or
         - ... is the same as the last one given out, and the person doing the
           edit is the same as the last editor."""

        if not self.isValidSafetyBelt(safety_belt):
            return 0
        self.updateSafetyBelt(safety_belt)
        return 1

    ### Content accessor methods

    #
    #   IContentish method
    #

    security.declareProtected(View, 'SearchableText')
    def SearchableText(self):
        """ Used by the catalog for basic full text indexing """
        return "%s %s %s" % ( self.Title()
                            , self.Description()
                            , self.EditableBody()
                            )

    #
    #   IDocument methods
    #

    security.declareProtected(View, 'CookedBody')
    def CookedBody(self, stx_level=None, setlevel=0):
        """ Get the "cooked" (ready for presentation) form of the text.

        The prepared basic rendering of an object.  For Documents, this
        means pre-rendered structured text, or what was between the
        <BODY> tags of HTML.

        If the format is html, and 'stx_level' is not passed in or is the
        same as the object's current settings, return the cached cooked
        text.  Otherwise, recook.  If we recook and 'setlevel' is true,
        then set the recooked text and stx_level on the object.
        """
        if (self.text_format == 'html' or self.text_format == 'plain'
            or (stx_level is None)
            or (stx_level == self._stx_level)):
            return self.cooked_text
        else:
            cooked = HTML(self.text, level=stx_level, header=0)
            if setlevel:
                self._stx_level = stx_level
                self.cooked_text = cooked
            return cooked

    security.declareProtected(View, 'EditableBody')
    def EditableBody(self):
        """ Get the "raw" (as edited) form of the text.

        The editable body of text.  This is the raw structured text, or
        in the case of HTML, what was between the <BODY> tags.
        """
        return self.text

    #
    #   IDublinCore method
    #

    security.declareProtected(View, 'Format')
    def Format(self):
        """ Dublin Core Format element - resource format.
        """
        if self.text_format == 'html':
            return 'text/html'
        else:
            return 'text/plain'

    #
    #   IMutableDublinCore method
    #

    security.declareProtected(ModifyPortalContent, 'setFormat')
    def setFormat(self, format):
        """ Set text format and Dublin Core resource format.
        """
        value = str(format)
        old_value = self.text_format

        if value == 'text/html' or value == 'html':
            self.text_format = 'html'
        elif value == 'text/plain':
            if self.text_format not in ('structured-text', 'plain'):
                self.text_format = 'structured-text'
        elif value == 'plain':
            self.text_format = 'plain'
        else:
            self.text_format = 'structured-text'

        # Did the format change? We might need to re-cook the content.
        if value != old_value:
            if html_headcheck(self.text) and value != 'plain':
                self.text = bodyfinder(self.text)

            self._edit(self.text)

    ## FTP handlers
    security.declareProtected(ModifyPortalContent, 'PUT')
    def PUT(self, REQUEST, RESPONSE):
        """ Handle HTTP (and presumably FTP?) PUT requests """
        self.dav__init(REQUEST, RESPONSE)
        self.dav__simpleifhandler(REQUEST, RESPONSE, refresh=1)

        try:
            self.failIfLocked()
        except ResourceLockedError, msg:
            transaction.abort()
            RESPONSE.setStatus(423)
            return RESPONSE

        body = REQUEST.get('BODY', '')
        if REQUEST.get_header('Content-Type', '') == 'text/html':
            format = 'html'
        else:
            format = None
        headers, body, format = self.handleText(body, format)

        safety_belt = headers.get('SafetyBelt', '')
        if not self._safety_belt_update(safety_belt):
            # XXX Can we get an error msg through?  Should we be raising an
            #     exception, to be handled in the FTP mechanism?  Inquiring
            #     minds...
            transaction.abort()
            RESPONSE.setStatus(450)
            return RESPONSE

        self.setFormat(format)
        self.setMetadata(headers)
        self._edit(body)
        RESPONSE.setStatus(204)
        self.reindexObject()
        return RESPONSE

    _htmlsrc = (
        '<html>\n <head>\n'
        ' <title>%(title)s</title>\n'
       '%(metatags)s\n'
        ' </head>\n'
        ' <body>%(body)s</body>\n'
        '</html>\n'
        )

    security.declareProtected(View, 'manage_FTPget')
    def manage_FTPget(self):
        "Get the document body for FTP download (also used for the WebDAV SRC)"
        if self.Format() == 'text/html':
            ti = self.getTypeInfo()
            method_id = ti and ti.queryMethodID('gethtml', context=self)
            if method_id:
                method = getattr(self, method_id)
                if getattr(aq_base(method), 'isDocTemp', 0):
                    bodytext = method(self, self.REQUEST)
                else:
                    bodytext = method()
            else:
                # Use the old code as fallback. May be removed some day.
                hdrlist = self.getMetadataHeaders()
                hdrtext = ''
                for name, content in hdrlist:
                    if name.lower() == 'title':
                        continue
                    else:
                        hdrtext = '%s\n <meta name="%s" content="%s" />' % (
                            hdrtext, name, content)

                bodytext = self._htmlsrc % {
                    'title': self.Title(),
                    'metatags': hdrtext,
                    'body': self.EditableBody(),
                    }
        else:
            hdrlist = self.getMetadataHeaders()
            hdrtext = formatRFC822Headers( hdrlist )
            bodytext = '%s\r\n\r\n%s' % ( hdrtext, self.text )

        return bodytext

    security.declareProtected(View, 'get_size')
    def get_size( self ):
        """ Used for FTP and apparently the ZMI now too """
        return self._size

InitializeClass(Document)

DocumentFactory = Factory(Document)
