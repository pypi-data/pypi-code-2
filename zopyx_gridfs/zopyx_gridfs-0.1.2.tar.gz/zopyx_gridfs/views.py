import gridfs
import pymongo
import logging
from webob import Response
from pyramid import registry

LOG = logging.getLogger('zopyx.gridfs')

def gridfs_view(request):

    settings = request.registry.settings
    host = settings.get('mongodb_host', 'localhost')
    port = settings.get('mongodb_port', '27017')
    database = settings.get('mongodb_database', 'test')

    try:
        conn = pymongo.Connection(host, int(port))
        LOG.debug('Connected to mongodb://%s:%s/%s'  % (host, port, database))
        filename = request.params.get('filename')
        collection = request.params.get('collection', 'files')

        db = getattr(conn, database)
        fs = gridfs.GridFS(db, collection)

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
    finally:
        conn.disconnect()
