
## This library is free software; you can redistribute it and/or
## modify it under the terms of the GNU General Public
## License as published by the Free Software Foundation; either
## version 2 of the License, or any later version.

## This library is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
## General Public License for more details.

## You should have received a copy of the GNU General Public
## License along with this library; if not, write to the Free Software
## Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

from logging import ERROR
from Products.Archetypes.debug import log
from Products.Archetypes.debug import log_exc

from Products.Archetypes.Field import FileField, ObjectField
from Products.Archetypes.Registry import registerField
from Products.CMFCore import permissions
from Products.CMFCore.utils import getToolByName

from Acquisition import aq_base
from OFS.Image import File
from types import ListType, TupleType, ClassType, FileType, DictType, IntType
from types import StringType, UnicodeType, StringTypes

from AccessControl import ClassSecurityInfo

from archetypes.multifile.MultiFileWidget import MultiFileWidget

class MultiFileField(FileField):
    """Stores multiple files."""

    _properties = ObjectField._properties.copy()
    _properties.update({
        'type' : 'file',
        'default' : '',
        'primary' : False,
        'widget' : MultiFileWidget,
        'content_class' : File,
        'default_content_type' : 'application/octet-stream',
        })

    security  = ClassSecurityInfo()
    
    def _process_input(self, value, file=None, default=None, mimetype=None,
                       instance=None, filename='', **kwargs):
        fvalue = []            
        if isinstance(value, ListType):
            for f in value:
                if f.filename =='':
                    continue
                file = self._make_file(self.getName(), title='',
                                       file='', instance=instance)
                filename = f.filename

                filename = filename[max(filename.rfind('/'),
                                    filename.rfind('\\'),
                                    filename.rfind(':'),
                                    )+1:]
                
                file.manage_upload(f)
            
                if mimetype is None or mimetype == 'text/x-unknown-content-type':
                    body = file.data
                    if not isinstance(body, basestring):
                        body = body.data
                        
                    mtr = getToolByName(instance, 'mimetypes_registry', None)
                    if mtr is not None:
                        kw = {'mimetype':None,
                              'filename':filename}
                        d, f, mimetype = mtr(body[:8096], **kw)
                        
                else:
                    mimetype = getattr(file, 'content_type', None)
                    if mimetype is None:
                        mimetype, enc = guess_content_type(filename, body, mimetype)
                        
                mimetype = str(mimetype).split(';')[0].strip()
                setattr(file, 'content_type', mimetype)
                setattr(file, 'filename', filename)
                fvalue.append((file, mimetype, filename))
        return fvalue

    def _make_file(self, id, title='', file='', instance=None):
        return self.content_class(id, title, file)

    security.declarePrivate('get')
    def get(self, instance, **kwargs):
        """Returns field value."""
        value = []
        
        __traceback_info__ = (self.getName(), instance, kwargs)
        try:
            kwargs['field'] = self
            if not hasattr(instance, '_fs'):
                instance._fs = []
            for fname in instance._fs:
                fdict = {}
                f = self.getStorage(instance).get(fname, instance, **kwargs)
                fdict['file'] = f
                fdict['get_size'] = f.get_size()
                fdict['filename'] = f.filename
                fdict['content_type'] = f.content_type
                fdict['icon'] = self.getIcon(f.content_type)
                value.append(fdict)
        except AttributeError:
            # happens if new Atts are added and not yet stored in the instance
            if not kwargs.get('_initializing_', False):
                self.set(instance, self.getDefault(instance), _initializing_=True, **kwargs)
            #return [self.getDefault(instance),]
            return []

        if value:
            return value
        return []
    
    security.declarePrivate('set')
    def set(self, instance, value, **kwargs):
        """
        Assign input value to object. If mimetype is not specified,
        pass to processing method without one and add mimetype returned
        to kwargs. Assign kwargs to instance.
        """
        if type(value) == type([]):
            pass
        
        if not hasattr(instance, '_fs'):
            instance._fs = []
            instance._p_changed = True
        
        if kwargs.has_key('DELETE'):
            kwargs['field'] = self            
            for filename in kwargs['DELETE']:
                if filename in instance._fs:
                    instance._fs.remove(filename)
                    instance._p_changed=True
                self.getStorage(instance).unset(filename, instance, **kwargs)

        value_list = self._process_input(value, file=None,
                                         instance=instance,
                                         **kwargs)

        if value_list is None or value_list ==[]:
            return 
            
        value_list = self._wrapValue(instance, value_list, **kwargs)
        for data, mimetype, filename in value_list:
            #ObjectField.set(self, instance, data, **kwargs)
            if data.size == 0:
                continue
            kwargs['field'] = self
            kwargs['mimetype'] = kwargs.get('mimetype', getattr(self, 'default_content_type', 'application/octet-stream'))
            # Remove acquisition wrappers
            value = aq_base(data)
            __traceback_info__ = (self.getName(), instance, value, kwargs)
            if data.filename not in instance._fs:
                instance._fs.append(data.filename)
            self.getStorage(instance).set(data.filename, instance, value, **kwargs)

    def _wrapValue(self, instance, value, **kwargs):
        """Wraps the value in the content class if it's not wrapped
        """
        value_list = []
        
        for data, mimetype, filename in value:
            if isinstance(data, self.content_class):
                value_list.append((data, mimetype, filename))
                continue
            mimetype = kwargs.get('mimetype', self.default_content_type)
            filename = kwargs.get('filename', '')
            obj = self._make_file(self.getName(), title='',
                                  file=data, instance=instance)
            setattr(obj, 'filename', filename)
            setattr(obj, 'content_type', mimetype)
            try:
                delattr(obj, 'title')
            except (KeyError, AttributeError):
                pass
            value_list.append((obj, mimetype, filename))
            
        return value_list

    security.declarePrivate('validate_required')
    def validate_required(self, instance, value, errors):
        return ObjectField.validate_required(self, instance, value, errors)

    security.declareProtected(permissions.View, 'download')
    def download(self, instance, name, REQUEST=None, RESPONSE=None):
        """Kicks download.

        Writes data including file name and content type to RESPONSE
        """
        files = self.get(instance)
        if not REQUEST:
            REQUEST = instance.REQUEST
        if not RESPONSE:
            RESPONSE = REQUEST.RESPONSE
        for file in files:
            if file['filename'] == name:
                filename = file['filename']
                RESPONSE.setHeader('Content-Type', file['content_type'])
                RESPONSE.setHeader('Content-Disposition', 'attachment;  filename="%s"' % file['filename'])
                return file['file'].data
        raise IndexError

    security.declarePublic('get_size')
    def get_size(self, instance):
        """Get size of the stored data used for get_size in BaseObject
        """
        files = self.get(instance)
        size = 0
        for file_dict in files:
            size = size+file_dict['get_size']
        return size

    def getIcon(self, content_type):
        mtr = getToolByName(self, 'mimetypes_registry', None)
        if mtr is None:
            return None
        lookup = mtr.lookup(content_type)
        if lookup:
            return lookup[0].icon_path
        else:
            return None

    security.declarePrivate('getIndexable')
    def getIndexable(self, instance):
        # XXX Naive implementation that loads all data contents into
        # memory.  To have this not happening set your field to not
        # 'searchable' (the default) or define your own 'index_method'
        # property.

        transforms = getToolByName(instance, 'portal_transforms')
        files = self.get(instance)
        datastreams = ''
        for f_dict in files:
            f = f_dict.get('file', None)
            if f is None:
                continue

            orig_mt = f_dict.get('content_type', None)
            if transforms._findPath(orig_mt, 'text/plain') is None:
                continue

            file_name = f_dict.get('filename', '')

            datastream = ''
            try:
                datastream = transforms.convertTo(
                    "text/plain",
                    str(f),
                    mimetype = orig_mt,
                    filename = file_name,
                    )
            except (ConflictError, KeyboardInterrupt):
                raise
            except Exception, e:
                log("Error while trying to convert file contents to 'text/plain' "
                    "in %r.getIndexable() of %r: %s" % (self, instance, e))

            datastreams += str(datastream) + '\n'

        return datastreams

registerField(MultiFileField,
              title='Multiple File Field',
              description=('Used for storing multiple files. '))

