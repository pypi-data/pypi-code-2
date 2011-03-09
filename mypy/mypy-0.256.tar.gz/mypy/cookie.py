from render import get_request

def set(key, value, expires='Expires=Mon, 19-Jan-2080 14:09:52 GMT;', path='/', request=None):
    str_cookie = "%s=%s"%(key, value)
    if path:
        str_cookie += ";Path=%s"%path
    if expires:
        str_cookie += (";%s"%expires)
    if request is None:
        request = get_request()
    request.res.headers.add_header(
        'Set-Cookie', str_cookie
    )

def delete(key, path='/', request=None):
    if request is None:
        request = get_request()
    request.res.headers.add_header(
        'Set-Cookie',
        '%s=EXPIRED;Expires=Mon, 19-Jan-1980 14:09:52 GMT;Path=%s'%(
            key, path
        )
    )
