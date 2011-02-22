from __future__ import with_statement
import os
import logging
import urllib
try:
    import json
except ImportError:
    import simplejson as json

from flask import Module, request, Response, abort

from nowsync.core import app
from nowsync.models.file import is_under_dir, cal_signature, get_files, \
    match_patterns
from nowsync import signals
from nowsync.utils import relpath

api = Module(__name__)

def json_response(data, *args, **kwargs):
    kwargs.setdefault('content_type', 'application/json')
    content = json.dumps(data)
    return Response(content, *args, **kwargs)

def validated_path(path):
    """Make sure a path is valid one and return
    
    """
    logger = logging.getLogger(__name__)
    sync_path = app.nowsync_cfg['sync_path']
    local_path = os.path.realpath(urllib.url2pathname(path))
    rel = relpath(local_path, sync_path)
    # make sure the path is still under sync path
    if not is_under_dir(local_path, sync_path):
        logger.warn('Path %s is not under dir %s', local_path, sync_path)
        abort(400)
    if match_patterns(rel, app.nowsync_cfg['ignore_files']):
        logger.warn('Path %s is in ignore files', local_path)
        abort(400)
    if not match_patterns(rel, app.nowsync_cfg['sync_files']):
        logger.warn('Path %s is in sync files', local_path)
        abort(400)
    return local_path

@api.route('/signature/<path:path>', methods=['GET'])
def signature(path):
    """Get signature of a remote file
    
    """
    logger = logging.getLogger(__name__)
    local_path = validated_path(path)
    if not os.path.exists(local_path):
        abort(404)
    sig = cal_signature(local_path)
    logger.info('Calculate signature %s of %s', sig, local_path)
    return json_response(dict(code='ok', data=sig))
    
@api.route('/put/<path:path>', methods=['POST'])
def put(path):
    """put from client
    
    """
    logger = logging.getLogger(__name__)
    local_path = validated_path(path)
    dir_path = os.path.realpath(os.path.dirname(local_path))
    
    # create directories
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
        logger.info('Create directories for path %s', dir_path)

    logger.debug('Writing file to %s ...', local_path)
    with open(local_path, 'wb') as file:
        file.write(request.data)
    logger.info('Wrote file to %s', local_path)
    return json_response(dict(code='ok', msg='put %s' % path))

@api.route('/delete/<path:path>', methods=['POST'])
def delete(path):
    """Delete a file
    
    """
    logger = logging.getLogger(__name__)
    local_path = validated_path(path)
    if not os.path.exists(local_path):
        abort(404)
    try:
        if os.path.isdir(local_path):
            os.rmdir(local_path)
        else:
            os.remove(local_path)
    except:
        logger.error('Failed to remove file %s', local_path, exc_info=True)
        return json_response(dict(code='error', msg='failed to delete'), 
                             status='500 Interval error')
    
    logger.info('Deleted file %s', local_path)
    return json.dumps(dict(code='ok', msg='deleted %s' % path))

@api.route('/files', methods=['GET'])
def files():
    """Get file map from path to signature
    
    """
    sync_path = app.nowsync_cfg['sync_path']
    sync_files =  app.nowsync_cfg['sync_files']
    ignore_files =  app.nowsync_cfg['ignore_files']
    files = get_files(sync_path, sync_files, ignore_files)
    return json.dumps(dict(code='ok', data=files))

@api.route('/restart', methods=['POST'])
def restart():
    """Restart application
    
    """
    signals.need_restart_app.send()
    return json.dumps(dict(code='ok'))
