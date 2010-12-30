import gridfs
import pymongo
import logging
from webob import Response
from pyramid import registry
from pyramid.view import view_config
from pyramid.renderers import render_to_response

LOG = logging.getLogger('zopyx.gridfs')


# The upload form template
@view_config(route_name='gridfs_upload_form', request_method='GET')
def upload(request):
    collection = request.matchdict['collection']
    return render_to_response('templates/upload.pt',
                              {'collection' : collection},
                              request=request)

# The upload action
@view_config(route_name='gridfs_upload_action', request_method='POST')
class GridFSUploader(object):

    def __init__(self, request):
        self.request = request

    @property
    def gridfs(self):
        settings = self.request.registry.settings
        host = settings.get('mongodb_host', 'localhost')
        port = settings.get('mongodb_port', '27017')
        database = settings.get('mongodb_database', 'test')
        conn = pymongo.Connection(host, int(port))
        db = getattr(conn, database)
        fs = gridfs.GridFS(db, self.request.matchdict['collection'])
        return fs

    def __call__(self):

        uploaded_file = self.request.POST['uploaded_file']
        fs = self.gridfs
        if fs.exists(uploaded_file.filename):
            return Response(status=500, 
                            body=u'Resource %s exists' % uploaded_file.filename)

        fp = fs.new_file(_id=uploaded_file.filename)
        fp.write(uploaded_file.value)
        fp.close()
        return Response(status=201, body='created')

@view_config(route_name='gridfs', request_method='GET')
class GridFSDownloader(GridFSUploader):

    def __call__(self):

        fs = self.gridfs
        filename = self.request.matchdict['filename']
        if not fs.exists(filename):
            return Response(status=404)

        grid_file = fs.get(filename)
        ct = grid_file.content_type
        headers = [('content-length', grid_file.length),
                  ]
        if ct:
            headers.append(('content-type', grid_file.content_type))
        return Response(app_iter=grid_file,
                        headers=headers)
