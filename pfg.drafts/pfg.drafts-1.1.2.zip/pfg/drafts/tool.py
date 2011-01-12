"""Tool to store copies of in-progress PloneFormGen form request data, keyed by user id.
"""

import rfc822
from AccessControl import getSecurityManager
from cStringIO import StringIO
from ZODB.blob import Blob
from zope.interface import implements
from zope.publisher.interfaces import IPublishTraverse
from AccessControl import ClassSecurityInfo
from ZPublisher.HTTPRequest import FileUpload
from BTrees.OOBTree import OOBTree
from OFS.SimpleItem import SimpleItem
from App.class_init import InitializeClass
from plone.app.blob.utils import openBlob
from Products.CMFCore.permissions import ManagePortal
from Products.CMFCore.utils import getToolByName
from Products.statusmessages.interfaces import IStatusMessage


class FakeFieldStorage(object):
    """FileUpload instances are constructed by passing in an "aFieldStorage".
    This class provides a picklable imitation of that.
    """
    def __init__(self, fupload):
        self.blob = Blob()
        blobfile = self.blob.open('w')
        blobfile.writelines(fupload)
        blobfile.close()
        
        self.raw_headers = fupload.headers.headers[0]
        self.filename = fupload.filename
    
    @property
    def file(self):
        return openBlob(self.blob)

    def headers(self):
        return rfc822.Message(StringIO(self.raw_headers))


class PFGDraftStorage(SimpleItem):
    implements(IPublishTraverse)
    
    id = 'portal_fg_drafts'
    title = 'Drafts of PloneFormGen forms in progress'
    meta_type = 'PloneFormGen Drafts'
    
    security = ClassSecurityInfo()
    
    def __init__(self, id='portal_fg_drafts'):
        self.id = id
        self.reset()
    
    def _getCurrentMember(self):
        mtool = getToolByName(self, 'portal_membership')
        if mtool.isAnonymousUser():
            return
        return mtool.getAuthenticatedMember()
    
    def _getDraftKey(self, uid, request=None):
        # let managers load another user's draft for debugging
        if request and 'debug_user' in request.form:
            if getSecurityManager().checkPermission('Manage portal', self):
                return (request.form['debug_user'], uid)
        
        mtool = getToolByName(self, 'portal_membership')
        if mtool.isAnonymousUser():
            return
        member = mtool.getAuthenticatedMember()
        return (member.getId(), uid)
    
    def saveDraft(self, uid, request):
        """Saves values from a Zope request to the draft storage.
        
        If there is already a draft in the storage for the current user,
        it is updated with the new values.
        """
        key = self._getDraftKey(uid, request)
        if key is None:
            return

        stored = {}
        if key in self.drafts:
            stored = self.drafts[key]
        stored = self._marshall(request.form, stored)
        self.drafts[key] = stored

    def retrieveDraft(self, uid, request):
        """Updates a Zope request with data stored in the draft storage.
        
        Values in the request form take precedence over values with
        matching keys in the draft storage.
        """
        if 'fg_from_draft' in request.form:
            # avoid retrieving twice
            return request
        
        # store original 'submitted' flag so we know whether to show a message
        submitted = 'form.submitted' in request.form
        
        key = self._getDraftKey(uid, request)
        if key is None:
            return request
        
        if key in self.drafts:
            draft = self._unmarshall(self.drafts[key])
            for k,v in request.form.items():
                if k in draft and isinstance(v, FileUpload) and not v.filename:
                    # don't clobber an existing file with an empty one
                    continue
                draft[k] = v
            draft['fg_from_draft'] = True
            request.form = draft
            
            # if this is the first form load, show a message
            # that old data was loaded
            if not submitted:
                IStatusMessage(request).addStatusMessage('We reloaded the data you saved earlier. '
                    'If you uploaded any files, they will be retained when you submit the form, '
                    'but will not show up below.')
        return request

    def _marshall(self, form, stored):
        d = {}
        for k,v in stored.items():
            d[k] = v
        for k,v in form.items():
            if isinstance(v, FileUpload):
                if k in stored and not v.filename:
                    # don't clobber an existing file with an empty one
                    continue
                # convert to something that can be pickled
                v = FakeFieldStorage(v)
            d[k] = v
        return d
    
    def _unmarshall(self, form):
        d = {}
        for k,v in form.items():
            if isinstance(v, FakeFieldStorage):
                v = FileUpload(v)
            d[k] = v
        return d
    
    def removeDraft(self, uid):
        key = self._getDraftKey(uid)
        if key and key in self.drafts:
            del self.drafts[key]

    security.declareProtected(ManagePortal, 'reset')
    def reset(self):
        """ Delete all drafts. """
        self.drafts = OOBTree()
    
InitializeClass(PFGDraftStorage)
