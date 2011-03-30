from datetime import datetime
from StringIO import StringIO
from time import strftime
from davobject import DAVObject
from bufferedwriter import BufferedWriter

class StaticObject(DAVObject):

    def __init__(self, parent, name, **params):
        DAVObject.__init__(self, parent, name, **params)

    def get_property_webdav_displayname(self):
        return DAVObject.get_property_webdav_displayname(self)

    def get_property_webdav_getcontentlength(self):
        return unicode(len(self.payload))

    def get_property_webdav_getcontenttype(self):
        return self.mimetype

    def _load_self(self):
        return True

    def do_GET(self):
       self.request.simple_response(200,
                                    data=self.payload,
                                    mimetype=self.get_property_webdav_getcontenttype())