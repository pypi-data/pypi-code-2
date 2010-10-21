import os

from zope.component import getMultiAdapter

from ZPublisher.BaseRequest import DefaultPublishTraverse

class FileSystemTraverse(DefaultPublishTraverse):
    
    def __init__(self, context, request):
        self.context = context
        self.request = request
        
    def publishTraverse(self, request, name):
        path = name
        if self.request.form.get('open', False):
            path = '%s/%s' % (self.request.form.get('open'), path)
        if os.path.exists(os.path.join(self.context.getFileSystemPath(), path)):
            self.request.form['open'] = path
            return self.context
        return super(FileSystemTraverse, self).publishTraverse(request, name)
