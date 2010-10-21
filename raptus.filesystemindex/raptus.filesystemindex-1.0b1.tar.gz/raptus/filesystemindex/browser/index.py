import os

from zope.component import getMultiAdapter

from plone.memoize.instance import memoize

from Products.CMFPlone.utils import safe_unicode
from Products.CMFCore.utils import getToolByName
from plone.app.layout.viewlets.common import ViewletBase
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from raptus.filesystemindex import _

def cmp_items(x, y):
    return cmp(x['name'], y['name'])

class FileSystemIndex(ViewletBase):
    """Viewlet showing the file system index
    """
    index = ViewPageTemplateFile('index.pt')
    recurse = ViewPageTemplateFile('list.pt')
    
    @property
    @memoize
    def root(self):
        return self.context.getFileSystemPath()
    
    @property
    @memoize
    def mtypes(self):
        return getToolByName(self.context, 'mimetypes_registry')
    
    @property
    @memoize
    def linkroot(self):
        return 'file:///'+('windows' in self.request.get('HTTP_USER_AGENT').lower() and self.context.getWinMount() or self.context.getUnixMount())
    
    @property
    @memoize
    def open(self):
        return self.request.form.get('open', '')
    
    def _get_icon(self, filename):
        return self.mtypes.classify(None, filename=filename).icon_path
    
    def _recursive_get_items(self, base, folders=0):
        if not os.path.isdir(base):
            return []
        items = []
        list = os.listdir(base)
        for name in list:
            path = os.path.join(base, name)
            relpath = path[len(self.root)+1:]
            if (folders and not os.path.isdir(path)) or \
               (not folders and not os.path.isfile(path)):
                continue
            item = {'name': safe_unicode(name),
                    'link': '/'.join((base.replace(self.root, self.linkroot), name)).replace(os.path.sep, '/'),
                    'icon': self._get_icon(name),
                    'target': '_blank'}
            if os.path.isdir(path):
                item['target'] = '_self'
                item['icon'] = 'folder_icon.gif'
                if self.open.startswith(relpath):
                    item['childs'] = self._recursive_get_items(path, folders)
                item['link'] = '%s/%s' % (self.context.absolute_url(), relpath)
            items.append(item)
        items.sort(cmp=cmp_items)
        return items
    
    @memoize
    def folders(self):
        return [{'name': _(u'Home'),
                 'target': '_self',
                 'icon': 'folder_icon.gif',
                 'link': self.context.absolute_url(),
                 'childs': self._recursive_get_items(self.root, 1)}]
    
    @memoize
    def files(self):
        files = []
        if self.open:
            files.append({'name': '..',
                          'target': '_self',
                          'icon': 'folder_icon.gif',
                          'link': '%s/%s' % (self.context.absolute_url(), os.path.dirname(self.open))})
        files.extend(self._recursive_get_items(os.path.join(self.root, self.open), 1))
        files.extend(self._recursive_get_items(os.path.join(self.root, self.open)))
        return files
