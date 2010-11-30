
from plone.app.content.browser.foldercontents import FolderContentsView as BaseFolderContentsView
from plone.app.content.browser.foldercontents import FolderContentsKSSView as BaseFolderContentsKSSView
from plone.app.content.browser.foldercontents import FolderContentsTable




class FolderContentsView(BaseFolderContentsView):
    """
    """

    def contents_table(self):
        table = FolderContentsTable(self.context, self.request,
                                    contentFilter={'getPhysicalTree': True})
        return table.render()


class FolderContentsKSSView(BaseFolderContentsKSSView):
    def update_table(self, pagenumber='1', sort_on='getObjPositionInParent', sort_order='', show_all=False):
        self.request.set('sort_on', sort_on)
        if sort_order :
            self.request.set('sort_order', sort_order)
        self.request.set('pagenumber', pagenumber)
        table = self.table(self.context, self.request,
                                    contentFilter={'sort_on':sort_on,
                                                   'sort_order':sort_order,
                                                   'getPhysicalTree': True})
        core = self.getCommandSet('core')
        core.replaceHTML('#folderlisting-main-table', table.render())
        return self.render()

