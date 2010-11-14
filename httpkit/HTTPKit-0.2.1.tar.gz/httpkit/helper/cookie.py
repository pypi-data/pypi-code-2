# -*- coding: utf-8 -*-
"""\

This code was originally based on code in WebOb by Ian Bicking and it seems
silly to start from scratch since it already works so well. Ian's license reads
as follows:

Copyright (c) 2007 Ian Bicking and Contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the “Software”), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

#
# Helpers
#

import Cookie
from datetime import timedelta, datetime, date
import time

def _serialize_cookie_date(dt):
    if dt is None:
        return None
    if isinstance(dt, unicode):
        dt = dt.encode('ascii')
    if isinstance(dt, timedelta):
        dt = datetime.now() + dt
    if isinstance(dt, (datetime, date)):
        dt = dt.timetuple()
    return time.strftime('%a, %d-%b-%Y %H:%M:%S GMT', dt)

def set_cookie(key, value='', max_age=None,
               path='/', domain=None, secure=None, httponly=False,
               version=None, comment=None, expires=None, charset='utf8'):
    """
    Set (add) a cookie for the response
    """
    if isinstance(value, unicode) and charset is not None:
        value = '"%s"' % value.encode(charset)
    cookies = Cookie.BaseCookie()
    cookies[key] = value
    if isinstance(max_age, timedelta):
        max_age = max_age.seconds + max_age.days*24*60*60
    if max_age is not None and expires is None:
        expires = datetime.utcnow() + timedelta(seconds=max_age)
    if isinstance(expires, timedelta):
        expires = datetime.utcnow() + expires
    if isinstance(expires, datetime):
        expires = '"'+_serialize_cookie_date(expires)+'"'
    for var_name, var_value in [
        ('max_age', max_age),
        ('path', path),
        ('domain', domain),
        ('secure', secure),
        ('HttpOnly', httponly),
        ('version', version),
        ('comment', comment),
        ('expires', expires),
        ]:
        if var_value is not None and var_value is not False:
            cookies[key][var_name.replace('_', '-')] = str(var_value)
    header_value = cookies[key].output(header='').lstrip()
    if header_value.endswith(';'):
        # Python 2.4 adds a trailing ; to the end, strip it to be
        # consistent with 2.5
        header_value = header_value[:-1]
    return header_value

def get_cookie(cookie_string, name=None):
    if cookie_string:
        cookie = Cookie.SimpleCookie()
        cookie.load(cookie_string)
        if name:
            if cookie.has_key(name):
                return cookie[name].value
        else:
            return cookie
    else:
        return None

def delete_cookie(key, path='/', domain=None):
    """
    Delete a cookie from the client.  Note that path and domain must match
    how the cookie was originally set.

    This sets the cookie to the empty string, and max_age=0 so
    that it should expire immediately.
    """
    return set_cookie(key, '', path=path, domain=domain,
                    max_age=0, expires=timedelta(days=-5))

def unset_cookie(key, header_list=[], path='/', domain=None):
    """
    Unset a cookie with the given name (remove it from the
    response).  If there are multiple cookies (e.g., two cookies
    with the same name and different paths or domains), all such
    cookies will be deleted.
    """
    new_header_list = []
    existing_cookie_values = []
    for d in header_list:
        name = d['name']
        value = d['value']
        if name.lower() == 'set-cookie':
            existing_cookie_values.append(value)
        else:
            new_header_list.append(dict(name=name, value=value))
    if existing_cookie_values:
        for header in existing_cookie_values:
            cookies = Cookie.BaseCookie()
            cookies.load(header)
            if key in cookies:
                found = True
                del cookies[key]
                value = cookies.output(header='').lstrip()
            if value:
                if value.endswith(';'):
                    # Python 2.4 adds a trailing ; to the end, strip it
                    # to be consistent with 2.5
                    value = value[:-1]
                new_header_list.append(dict(name='Set-Cookie', value=value))
    return new_header_list

