"""Define a browser view for the FileExchange Container content type. In the FTI
configured in profiles/default/types/*.xml, this is being set as the default
view of that content type.
"""

from Acquisition import aq_inner, aq_parent
from AccessControl import Unauthorized

from DateTime import DateTime

from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from Products.CMFCore.utils import getToolByName

from plone.memoize.instance import memoize

from Products.CMFPlone import PloneMessageFactory as _
from Products.FileExchange.config import ADD_PERMISSIONS, MODIFY_PERMISSION

class FileExchangeContainerView(BrowserView):
    """Default view of a fileexchange container
    """

    template = ViewPageTemplateFile('templates/fileexchangecontainer.pt')

    def __call__(self):
        context = aq_inner(self.context)
        self.errors = {}
        self.errors_edit = {}
        self.doDelete = self.doEdit = self.hasFiles = self.hasPerm =  False
        self.request.set('disable_border', True)
        self.putils = getToolByName(context, 'plone_utils')
        self.mtool = getToolByName(context, 'portal_membership')

        form = self.request.form

        if form.get('form.submitted', None) is not None:
            self.processForm()

        if self.request.get('delete'):
            self.prepareDelete()

        if self.request.get('edit'):
            self.prepareEdit()

        self.ownFiles = self.getFolderContentsByAuthor()
        self.receivedFiles = self.getFolderContentsNotByAuthor()
        self.hasFiles = self.ownFiles or self.receivedFiles
        self.fullname = self.mtool.getMemberInfo(self.getAuthor()).get('fullname', self.getAuthor())
        self.hasPerm = self.mtool.checkPermission(ADD_PERMISSIONS['FileExchange File'], context)

        return self.template()

    @memoize
    def getParent(self):
        return aq_parent(aq_inner(self.context))

    @memoize
    def getAuthor(self):
        return self.getParent().getId()

    def prepareContents(self, objects):
        context = aq_inner(self.context)
        contents = []

        for obj in objects:
            values = {'id'      : obj.getId(),
                      'title'   : obj.Title(),
                      'modified': obj.modified,
                      'icon'    : obj.getIcon(),
                      'url'     : '%s/%s' % (context.absolute_url(), obj.getId()),
                      'delUrl'  : '%s?delete=%s' % (context.absolute_url(), obj.getId()),
                      'editUrl' : '%s?edit=%s' % (context.absolute_url(), obj.getId()),
                      'hasPerm' : self.mtool.checkPermission(MODIFY_PERMISSION, obj),
                      }
            contents.append(values)
        return contents

    @memoize
    def getFolderContentsByAuthor(self):
        context = aq_inner(self.context)
        content = context.getFolderContents( contentFilter={'Creator' : self.getAuthor(),
                                                            'sort_on' : 'modified',
                                                            'sort_order' : 'reverse' }, full_objects=True )
        return self.prepareContents(content)

    @memoize
    def getFolderContentsNotByAuthor(self):
        context = aq_inner(self.context)
        found   = []
        content = context.getFolderContents( contentFilter={'sort_on' : 'modified',
                                                            'sort_order' : 'reverse' }, full_objects=True )
        for item in content:
            if not item.Creator() == self.getAuthor():
                found.append(item)
        return self.prepareContents(found)

    def getFileTitle(self, id):
        context = aq_inner(self.context)
        if context.get(id, None) is not None:
            return context.get(id, None).Title()
        return None

    def prepareEdit(self):
        context = aq_inner(self.context)
        file = context.get(self.request.get('edit'), None)
        if not self.mtool.checkPermission(MODIFY_PERMISSION, file):
            raise Unauthorized
        self.doEdit = self.request.get('edit')
        self.request.set('title_edit', self.getFileTitle(self.request.get('edit')))

    def prepareDelete(self):
        context = aq_inner(self.context)
        file = context.get(self.request.get('delete'), None)
        if not self.mtool.checkPermission(MODIFY_PERMISSION, file):
            raise Unauthorized
        self.doDelete = {'id'    : self.request.get('delete'),
                         'title' : self.getFileTitle(self.request.get('delete')),
                        }

    def validateForm(self):
        form = self.request.form
        errors = self.errors
        if form.get('id', None) is not None:
            errors = self.errors_edit
        if form.get('title', '') == '' and form.get('title_edit', '') == '':
            errors['title'] = _(u'This field is required, please provide some information.')
        if form.get('file', '').filename == '' and form.get('id', None) is None:
            errors['file'] = _(u'This field is required, please provide some information.')
        return (len(errors) == 0)

    def processForm(self):
        context = aq_inner(self.context)
        form = self.request.form
        if form.get('form.button.Save', None) is not None:
            if self.validateForm():
                if form.get('id', None) is not None:
                    self.editFile(form.get('id', None))
                else:
                    self.addFile()
            else:
                if form.get('id', None) is not None:
                    self.request.set('edit', form.get('id', None))
                self.putils.addPortalMessage(_(u'Please correct the indicated errors.'))

        if form.get('form.button.Delete') and form.get('id'):
            self.deleteFile(form.get('id'))

        pass

    def deleteFile(self, id):
        context = aq_inner(self.context)
        try:
            file = context.get(id, None)
            if not self.mtool.checkPermission(MODIFY_PERMISSION, file):
                raise Unauthorized
            title = self.getFileTitle(id)
            context.manage_delObjects(id)
            message = _(u'${title} has been deleted.',
                        mapping={u'title' : title})
            self.putils.addPortalMessage(message)
        except:
            self.putils.addPortalMessage(_(u'Deleting file failed.'))

    def editFile(self, id):
        context = aq_inner(self.context)
        form = self.request.form
        try:
            file = context.get(id, None)
            if not self.mtool.checkPermission(MODIFY_PERMISSION, file):
                raise Unauthorized
            file.edit(title=form.get('title_edit'))
            if not form.get('file', '').filename == '':
                file.edit(file=form.get('file').read())
            file.reindexObject()
            self.putils.addPortalMessage(_(u'Changes saved.'))
        except:
            self.putils.addPortalMessage(_(u'Saving changes failed.'))

    def addFile(self):
        context = aq_inner(self.context)
        form = self.request.form
        try:
            typestool = getToolByName(context, 'portal_types')

            f = form.get('file')
            now = DateTime()
            time = '%s.%s' % (now.strftime('%Y-%m-%d'), str(now.millis())[7:])
            ext = f.filename.rfind('.') > -1 and f.filename[f.filename.rfind('.'):] or ''
            id = 'file%s%s' % (time, ext)

            typestool.constructContent(type_name='FileExchange File', container=context, id=id)
            file = context.get(id, None)
            file.manage_addLocalRoles(self.request.get('AUTHENTICATED_USER').getId(), ('FEFOwner',))
            file.edit(title=form.get('title'), file=f.read())
            file.reindexObject()
            self.putils.addPortalMessage(_(u'File successfully uploaded.'))
        except:
            self.putils.addPortalMessage(_(u'Fileupload failed.'))
