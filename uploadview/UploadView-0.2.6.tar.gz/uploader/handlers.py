import os
import sys
from urlparse import urlparse
from webob import Response, exc

class Handler(object):
    def __init__(self, app, request):
        self.app = app
        self.request = request
        self.application_path = urlparse(request.application_url)[2]

    def link(self, path=(), permanant=False):
        if isinstance(path, basestring):
            path = [ path ]
        path = [ i.strip('/') for i in path ]
        if permanant:
            application_url = [ self.request.application_url ]
        else:
            application_url = [ self.application_path ]
        path = application_url + path
        return '/'.join(path)

    def redirect(self, location):
        return exc.HTTPSeeOther(location=location)

class Get(Handler):

    form = """<form name="upload_form" method="post" enctype="multipart/form-data">
<input type="file" name="file"/><input type="submit" value="upload"/></form></body></html>"""

    @classmethod
    def match(cls, app, request):
        if app.query_string and (app.query_string not in request.GET):
            return False
        return request.method == 'GET'

    def __call__(self):
        form = "<html><body>"
        if 'uploaded' in self.request.GET:
            form += '<div>%s uploaded successfully</div>' % self.request.GET['uploaded']
        form += self.form
        if self.app.display_contents:
            contents = os.listdir(self.app.directory)
            if contents:
                contents.sort()
                form += '<div><i>Currently uploaded:<ul><li>' + '</li><li>'.join(contents) + '</li></ul></i></div>'
            else:
                form += '<div><i>No files in upload directory</i></div>'
            log_file = self.app.log_file
            if log_file and os.path.exists(log_file):
                log_contents = file(log_file).read()
                form += '<div>Upload log:<pre>%s</pre></div>' % log_contents
        form += '</body></html>'
        return Response(content_type='text/html', body=form)

class Post(Handler):

    @classmethod
    def match(cls, app, request):
        return request.method == 'POST'

    def write(self, fin, path):
        fout = file(path, 'w')
        fout.write(fin.file.read())
        fout.close()

    def __call__(self):

        # get the file
        fin = self.request.POST['file']
        try:
            _path = fin.filename
        except AttributeError: # no file uploaded
            return self.redirect(self.link('/'))

        # don't allow bad filenames
        illegal = ['..', '<', '&', '>']
        illegal.append(os.path.sep)
        for i in illegal:
            _path = _path.replace(i, '_')

        # write the file + redirect
        _path = os.path.join(self.app.directory, _path)
        self.write(fin, _path)
        if self.app.log_file:
            try:
                f = file(self.app.log_file, 'a')
                print >> f, fin.filename
                f.close()
            except Exception, e:
                print >> sys.stderr, e
        return self.redirect(self.link('/?uploaded=' + fin.filename))

def path(directory, request):
    if os.sep == '/':
        return os.path.join(directory, request.path_info.strip('/'))
    return os.path.join(directory, *request.path_info.strip('/').split('/'))

class SubpathGet(Get):
    
    @classmethod
    def match(cls, app, request):
        if not Get.match(app, request):
            return False
        _path = path(app.directory, request)
        if os.path.exists(_path) and os.path.isdir(_path):
            return True
        
class SubpathPost(Post):
    
    @classmethod
    def match(cls, app, request):
        if request.method != 'POST':
            return False
        _path = path(app.directory, request)
        if os.path.exists(_path) and os.path.isdir(_path):
            return True

    def __call__(self):
        fin = self.request.POST['file']
        _path = path(self.app.directory, self.request)
        _path = os.path.join(_path, fin.filename)
        self.write(fin, _path)
        return self.redirect(self.link(self.request.path_info))
        
