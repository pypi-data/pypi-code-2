# Copyright (c) 2010 Tauno Williams <awilliam@whitemice.org>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
import urllib
from coils.protocol.dav.foundation     import DAVFolder
from documentobject                    import DocumentObject

class DocumentsFolder(DAVFolder):
    def __init__(self, parent, name, **params):
        DAVFolder.__init__(self, parent, name, **params)

    def _load_contents(self):
        contents = self.context.run_command('folder::ls', id=self.entity.object_id)
        for entity in contents:
            if (entity.__entityName__ == 'Folder'):
                self.insert_child(entity.name, entity)
            elif (entity.__entityName__ == 'File'):
                self.insert_child('{0}.{1}'.format(entity.name, entity.extension), entity)
        return True

    def object_for_key(self, name, auto_load_enabled=True, is_webdav=False):
        if  (self.load_contents()):
            if (self.has_child(name)):
                entity = self.get_child(name)
                if (entity.__entityName__ == 'File'):
                    return DocumentObject(self, name, entity=entity,
                                                       request=self.request,
                                                       context=self.context)
                elif (entity.__entityName__ == 'Folder'):
                    return DocumentsFolder(self, name, entity=entity,
                                                        request=self.request,
                                                        context=self.context)
        self.no_such_path()

    def do_PUT(self, name):
        ''' Process a PUT request '''
        # TODO: Support If-Match header!
        # TODO: Check for locks!
        self.log.debug('Request to create {0} in folder {1}'.format(name, self.name))
        if (self.load_contents()):
            if (self.has_child(name)):
                # New Version
                entity = self.get_child(name)
                version = self.context.run_command('document::new-version', document=entity,
                                                                            handle=self.request.rfile)
            else:
                # Creation
                document = self.context.run_command('document::new', name=name,
                                                                     folder=self.entity)
                if (document is not None):
                    version = self.context.run_command('document::new-version', document=document,
                                                                                handle=self.request.rfile)
            if (version is not None):
                pass
