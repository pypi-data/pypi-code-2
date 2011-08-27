"""
Cache module for Abrek
"""
import contextlib
import hashlib
import os
import urllib2


class AbrekCache(object):
    """
    Cache class for Abrek
    """

    _instance = None

    def __init__(self):
        home = os.environ.get('HOME', '/')
        basecache = os.environ.get('XDG_CACHE_HOME',
                     os.path.join(home, '.cache'))
        self.cache_dir = os.path.join(basecache, 'abrek')

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def open_cached(self, key, mode="r"):
        """
        Acts like open() but the pathname is relative to the
        abrek-specific cache directory.
        """
        if "w" in mode and not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)
        if os.path.isabs(key):
            raise ValueError("key cannot be an absolute path")
        try:
            stream = open(os.path.join(self.cache_dir, key), mode)
            yield stream
        finally:
            stream.close()

    def _key_for_url(self, url):
        return hashlib.sha1(url).hexdigest()

    def _refresh_url_cache(self, key, url):
        with contextlib.nested(
            contextlib.closing(urllib2.urlopen(url)),
            self.open_cached(key, "wb")) as (in_stream, out_stream):
            out_stream.write(in_stream.read())

    @contextlib.contextmanager
    def open_cached_url(self, url):
        """
        Like urlopen.open() but the content may be cached.
        """
        # Do not cache local files, this is not what users would expect

        # workaround - not using cache at all.
        # TODO: fix this and use the cache
        # if url.startswith("file://"):
        if True:
            stream = urllib2.urlopen(url)
        else:
            key = self._key_for_url(url)
            try:
                stream = self.open_cached(key, "rb")
            except IOError as exc:
                self._refresh_url_cache(key, url)
                stream = self.open_cached(key, "rb")
        yield stream
        stream.close()
