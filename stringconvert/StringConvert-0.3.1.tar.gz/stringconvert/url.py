from urlconvert import _to_parts, makeUnicode, matchScheme, matchHost, \
   matchPort, matchScript, matchPath, matchQuery, plainDecode, decodeScript, \
   decodePath, decodeQuery, build_url
from conversionkit import chainConverters, toDictionary

_make_unicode = makeUnicode()

def _build_url(conversion, state):
    try: 
        conversion.result = build_url(**conversion.value)
    except Exception, e:
        conversion.error = 'Not a valid URL: %r'%e

def unicodeToURL():
    return chainConverters(
        _to_parts, 
        toDictionary(
            converters = dict(
                scheme   = chainConverters(_make_unicode, matchScheme(), plainDecode('utf8')),
                host     = chainConverters(_make_unicode, matchHost(), plainDecode('utf8')),
                port     = chainConverters(_make_unicode, matchPort(), plainDecode('utf8')),
                script   = chainConverters(_make_unicode, matchScript(), decodeScript('utf8')),
                path     = chainConverters(_make_unicode, matchPath(), decodePath('utf8')),
                query    = chainConverters(_make_unicode, matchQuery(), decodeQuery('utf8')),
            )
        ),
        _build_url,
    )

