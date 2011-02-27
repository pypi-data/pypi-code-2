import urlparse
import bucho


default_message = """\
bucho provide below urls:
 * /show
 * /latest_status
 * /all_status
 * /torumemo
"""

def wsgi_app(environ, start_response):
    split_result = urlparse.urlsplit(environ['PATH_INFO'])
    paths = filter(None, split_result[2].split('/'))
    headers = [('Content-Type', 'text/plain')]

    if not paths:
        start_response('200 OK', headers)
        return [default_message]

    api_name = paths[0]

    try:
        method = getattr(bucho, api_name)
    except:
        status = '404 Not Found'
        start_response(status, headers)
        return [status]

    try:
        result = method().encode('utf-8')
    except:
        status = '500 Internal Server Error'
        start_response(status, headers)
        return [status]

    start_response('200 OK', headers)
    return [result]


def app_factory(global_config, **local_conf):
    """ wsgi app factory for Paste """
    return wsgi_app

