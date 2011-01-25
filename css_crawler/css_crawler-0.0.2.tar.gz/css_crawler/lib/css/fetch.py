import urllib2
import urllib
import urlparse
import posixpath
import encutils  # part of cssutils

from css_crawler.lib import log


def join_url(base, url):
    join = urlparse.urljoin(base, url)
    url = urlparse.urlsplit(join)
    path = posixpath.normpath(url.path or '/')
    return urlparse.urlunsplit(
        (url.scheme, url.netloc, path, url.query, url.fragment)
    )


def fetch_url(url, ua='CSS Crawler', log=log):
    log.info('FETCHING: %s', url)

    #fix imported from python 2.7
    url = urllib.quote(url, safe="%/:=&?~#+!$,;'@()*[]")
    url = join_url(url, '')

    opener = urllib2.build_opener()
    opener.addheaders = [('user-agent', ua)]

    request = urllib2.Request(url)
    res = None

    try:
        res = opener.open(request)
    except OSError:
        # e.g if file URL and not found
        log.exception(u'OSError')
    except ValueError as e:
        # invalid url, e.g. "1"
        log.exception(u'ValueError, %s', e.args[0])
    except urllib2.HTTPError as e:
        # http error, e.g. 404, e can be raised
        log.exception(u'HTTPError opening url=%r: %s %s', url, e.code, e.msg)
    except urllib2.URLError as e:
        # URLError like mailto: or other IO errors, e can be raised
        log.exception(u'URLError, %s', e.reason)
    else:
        if res:
            return res
    return None


def css_fetcher_factory(ua='CSS Crawler', log=log, url_fetcher=fetch_url):

    def fetcher(url):

        res = url_fetcher(url, ua, log)

        if res is None:
            return None, None

        mimeType, encoding = encutils.getHTTPInfo(res)
        if mimeType != u'text/css':
            log.warning(
                u'Expected "text/css" mime type for url=%r but found: %r', url,
                mimeType)

        return 'utf-8', unicode(res.read(),
                            encoding or 'utf-8', 'ignore').encode('utf-8')

    return fetcher
