
from Acquisition import aq_parent, aq_inner
from plone.app.content.browser.foldercontents import FolderContentsView \
                                as BaseFolderContentsView
from plone.app.content.browser.foldercontents import FolderContentsTable
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

class FolderContentsView(BaseFolderContentsView):
    """
    """
    # template = ViewPageTemplateFile('folder_contents.pt')
    # TODO: 

    def is_listing_reverse(self):
        field = self.context.getField('is_listing_reverse', None)
        if field is None:
            return False
        return field.get(self.context)

    def contents_table(self):
        contentFilter={}
        if self.is_listing_reverse():
            contentFilter['sort_order'] = 'reverse'
        table = FolderContentsTable(aq_inner(self.context), self.request,
                                contentFilter=contentFilter)
        return table.render()

