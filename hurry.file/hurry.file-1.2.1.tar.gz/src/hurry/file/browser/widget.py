##############################################################################
#
# Copyright (c) 2006-2008 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################

import random, sys
from StringIO import StringIO

from zope.interface import implements
from zope.publisher.browser import FileUpload

from zope.app.form.browser import DisplayWidget
from zope.app.form.interfaces import IDisplayWidget
from zope.app.form.browser.widget import renderElement
from zope.app.form.interfaces import ConversionError
from zope.app.form.browser.textwidgets import escape
from zope.session.interfaces import ISession
from zope.app.form.browser import TextWidget

from hurry.file.file import HurryFile

class DownloadWidget(DisplayWidget):
    """Display widget for file download.
    """
    implements(IDisplayWidget)

    required = False
    
    def __call__(self):
        if self._renderedValueSet():
            value = self._data
        else:
            value = self.context.default
        if value == self.context.missing_value:
            return renderElement(
                u'div',
                contents=u'Download not available')
        filename = escape(value.filename)
        return renderElement(
            u'a',
            href=filename,
            contents=filename)

class FakeFieldStorage:
    def __init__(self, filename, data):
        self.filename = filename
        self.file = StringIO(data)
        self.headers = {}
        
class FileWidgetBase(TextWidget):
    type = 'file'
    _missing = None
    
    def __call__(self):
        value = self._getFormValue()
        if value:
            file_id = self._setFile(value)
        else:
            file_id = None
            
        displayMaxWidth = self.displayMaxWidth or 0
        if displayMaxWidth > 0:
            result = renderElement(
                self.tag,
                type=self.type,
                name=self.name,
                id=self.name,
                cssClass=self.cssClass,
                size=self.displayWidth,
                maxlength=displayMaxWidth,
                extra=self.extra)
        else:
            result = renderElement(
                self.tag,
                type=self.type,
                name=self.name,
                id=self.name,
                cssClass=self.cssClass,
                size=self.displayWidth,
                extra=self.extra)
            
        # if there was data in the input, pass along the data id
        if file_id is not None:
            # tell tramline to store this file (if tramline is in use)
            self.request.response.addHeader('tramline_ok', 'OK')
            if value:
                result += ' (%s)' % value.filename 
            result += renderElement(
                'input',
                type='hidden',
                name=self.name + '.file_id',
                id=self.name + '.file_id',
                value=file_id,
                )
        return result
    
    def hasInput(self):
        return (self.name in self.request.form or
                self.name + '.file_id' in self.request.form)

    def _getFormInput(self):
        return (self.request.get(self.name),
                self.request.get(self.name + '.file_id'))

    def _toFormValue(self, value):
        if value == self.context.missing_value:
            return self._missing
        return FileUpload(FakeFieldStorage(value.filename.encode('UTF-8'),
                                           value.data))

    def _toFieldValue(self, (input, file_id)):
        # we got no file upload input
        if not input:
            # if we got a file_id, then retrieve file and return it
            if file_id:
                return self._retrieveFile(file_id)
            # no file upload input nor file id, so return missing value
            return self.context.missing_value
        # read in file from input
        try:
            seek = input.seek
            read = input.read
        except AttributeError, e:
            raise ConversionError('Form input is not a file object', e)

        seek(0)
        data = read()

        if data:
            return HurryFile(input.filename, data)
        else:
            return self.context.missing_value

    def _setFile(self, file):
        """Store away uploaded file (FileUpload object).

        Returns file_id identifying file.
        """
        # if there was no file input and there was a file_id already in the
        # input, reuse this for next request
        if not self.request.get(self.name):
            file_id = self.request.get(self.name + '.file_id')
            if file_id is not None:
                return file_id
        # otherwise, stuff filedata away in session, making a new file_id
        if file == self.context.missing_value:
            return None
        return self._storeFile(file)

    def _storeFile(self, file_upload):
        """Store a file_upload away. Return unique file id.
        """
        raise NotImplementedError

    def _retrieveFile(self, file_id):
        """Retrieve a file. This returns a HurryFile, *not* a FileUpload.
        """
        raise NotImplementedError

class EncodingFileWidget(FileWidgetBase):
    """Stuff actual file data away in form, encoded.
    """
    def _storeFile(self, file_upload):
        data = '%s\n%s' % (file_upload.filename, file_upload.read())
        return data.encode('base64')[:-1]

    def _retrieveFile(self, file_id):
        data = file_id.decode('base64')
        filename, filedata = data.split('\n', 1)
        return HurryFile(filename, filedata)
    
class SessionFileWidget(FileWidgetBase):
    """Stuff file in session.
    """
    def _storeFile(self, file_upload):
        """Store a file away. Return unique file id.
        """
        session = ISession(self.request)
        while True:
            file_id = random.randrange(sys.maxint)
            session_id = 'session_file_widget.%s' % file_id
            session_data = session[session_id]
            if not session_data.has_key('data'):
                break
        session_data['data'] = {'filename': file_upload.filename,
                                'data': file_upload.read()}
        return file_id
    
    def _retrieveFile(self, file_id):
        session = ISession(self.request)
        session_data = session['session_file_widget.%s' % file_id]['data']
        return HurryFile(session_data['filename'], session_data['data'])
    
class EncodingFileUploadDownloadWidget(EncodingFileWidget, DownloadWidget):
    def __call__(self):
        # first render the normal upload information
        result = EncodingFileWidget.__call__(self)
        # now show the download link
        result += renderElement('br')
        result += DownloadWidget.__call__(self)
        return result

class SessionFileUploadDownloadWidget(SessionFileWidget, DownloadWidget):
    def __call__(self):
        # first render the normal upload information
        result = SessionFileWidget.__call__(self)
        # now show the download link
        result += renderElement('br')
        result += DownloadWidget.__call__(self)
        return result
