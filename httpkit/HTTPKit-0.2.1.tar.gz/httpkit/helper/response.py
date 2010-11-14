import logging
log = logging.getLogger(__name__)

def not_found(bag, emit_log=True, errordocument='errordocument'):
    if emit_log:
        log.error('Not found: %s'%bag.environ['PATH_INFO'])
    bag.http_response.status = '404 Not Found'
    if not bag.has_key(errordocument):
        try:
            bag.enter(errordocument)
        except Exception, e:
            log.error(str(e))
            bag.http_response.header_list = [dict(name='Content-Type', value='text/plain')]
            bag.http_response.body = [u'Not found']
            return
    bag[errordocument].render()

def forbidden(bag, emit_log=True, errordocument='errordocument'):
    if emit_log:
        log.error('Forbidden: %s'%bag.environ['PATH_INFO'])
    if not bag.has_key(errordocument):
        bag.enter(errordocument)
    bag.http_response.status = '403 Forbidden'
    if not bag.has_key(errordocument):
        try:
            bag.enter(errordocument)
        except Exception, e:
            log.error(str(e))
            bag.http_response.header_list = [dict(name='Content-Type', value='text/plain')]
            bag.http_response.body = [u'Not found']
            return
    bag[errordocument].render()
