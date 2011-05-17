from random import choice

from tools.net.useragent import useragents

ACCEPT_CHOICES = [
    'application/xml,application/xhtml+xml,text/html;q=0.9,text/plain;q=0.8,image/png,*/*;q=0.5',
    'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
]


def useragent():
    return {'User-Agent': choice(useragents)}

def cache_control():
    return {'Cache-Control': 'max-age=0'}

def accept():
    return {'Accept': choice(ACCEPT_CHOICES)}

def accept_language():
    return {'Accept-Language': 'en-us,en;q=0.5'}

def accept_charset():
    return {'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.7'}

def keep_alive():
    return {'Keep-Alive': '300',
            'Connection': 'keep-alive'}

COMMON_HEADERS = [useragent, cache_control, accept, accept_language, accept_charset, keep_alive]

def random_request():
    headers = {}
    for func in COMMON_HEADERS:
        headers.update(func())
    return headers


#Accept-Encoding: gzip,deflate
