import hashlib
import lxml.html
import mmap
import os
import posixpath
import re
import shutil
import string
import tempfile
import urllib
import urllib2
import urlparse


__all__ = [
    'AbstractCachingPackageIndex',
    'NaiveCachingPackageIndex',
    'DjangoCachingPackageIndex',
]


class DistributionNotFound(Exception):
    pass


class InvalidHash(Exception):
    pass


class AbstractCachingPackageIndex(object):
    """
    Caches responses from a remote package index, stores distributions locally.
    
    This must be subclassed, with get_cache/set_cache implementations provided.
    """
    
    DistributionNotFound = DistributionNotFound
    InvalidHash = InvalidHash
    
    _VALID_BASENAME_CHRS = '-_.() ' + string.ascii_letters + string.digits
    _INVALID_BASENAME_CHRS_RE = re.compile(r'[^%s]+' % re.escape(_VALID_BASENAME_CHRS))
    
    def __init__(self, serve_path=None, cache_path=None,
                        remote_url='http://pypi.python.org/simple/',
                        remote_package_names_lifetime=60 * 60 * 2,
                        remote_dist_names_lifetime=60 * 60 * 24):
        self.cache_path = cache_path
        self.serve_path = serve_path
        self.remote_url = remote_url
        self.remote_package_names_lifetime = remote_package_names_lifetime
        self.remote_dist_names_lifetime = remote_dist_names_lifetime
    
    def get_cache(self, name):
        raise NotImplementedError()
    
    def set_cache(self, name, value, lifetime_seconds):
        raise NotImplementedError()
    
    def get_or_set_cache(self, key, get_value, lifetime):
        """
        Returns a cache value if it exists - if not, sets the cache with the
        value returned by get_value(), and returns that.
        """
        value = self.get_cache(key)
        if value is None:
            value = get_value()
            self.set_cache(key, value, lifetime)
        return value
    
    def package_names(self):
        names = []
        if self.serve_path is not None:
            names.extend(self.serve_package_names())
        if self.remote_url is not None:
            names.extend(self.remote_package_names())
        return list(sorted(set(names)))
    
    def dist_names(self, package_name):
        names = []
        if self.serve_path is not None:
            names.extend(self.serve_dist_names(package_name))
        if self.remote_url is not None:
            names.extend(self.remote_dist_names(package_name))
        return list(sorted(set(names)))
    
    def dist_filename(self, package_name, dist_name):
        if self.serve_path is not None:
            serve_filename = self._local_dist_filename(self.serve_path, package_name, dist_name)
            if os.path.isfile(serve_filename):
                return serve_filename
        
        if self.cache_path is None:
            raise DistributionNotFound((
                '%s/%s can\'t be downloaded, as cache_path hasn\'t been set'
            ) % (
                package_name, dist_name,
            ))
        
        if self.remote_url is None:
            raise DistributionNotFound((
                '%s/%s can\'t be downloaded, as remote_url hasn\'t been set'
            ) % (
                package_name, dist_name,
            ))
        
        cache_filename = self._local_dist_filename(self.cache_path, package_name, dist_name)
        if os.path.isfile(cache_filename):
            return cache_filename
        
        dist_url = self.remote_dist_url(package_name, dist_name)
        
        # Download to a temporary file
        response = urllib2.urlopen(dist_url)
        tmp_handle, tmp_filename = tempfile.mkstemp()
        tmp_file = os.fdopen(tmp_handle, 'wb+')
        shutil.copyfileobj(response, tmp_file)
        tmp_file.close()
        
        # Check the file hash, if one was given in the URL
        self._assert_valid_hash(tmp_filename, dist_url)
        
        # Copy the temp file to the local package directory
        cache_dirname = os.path.dirname(cache_filename)
        try:
            os.makedirs(cache_dirname)
        except (IOError, OSError):
            if not os.path.isdir(cache_dirname):
                raise
        shutil.move(tmp_filename, cache_filename)
        
        return cache_filename
    
    def serve_package_names(self):
        """
        Package names served from the local filesystem. Doesn't include
        anything in the cache.
        """
        return self._local_package_names(self.serve_path)
    
    def serve_dist_names(self, package_name):
        """
        Distribution names for a locally-served package.
        """
        return self._local_dist_names(self.serve_path, package_name)
    
    def remote_package_names(self):
        """
        Cached package names from the remote package index.
        """
        return self.get_or_set_cache(
            key='package_names',
            get_value=lambda: self._fetch_remote_package_names(),
            lifetime=self.remote_package_names_lifetime,
        )
    
    def remote_dist_urls(self, package_name):
        return self.get_or_set_cache(
            key='dist_urls:%s' % package_name,
            get_value=lambda: self._fetch_remote_dist_urls(package_name),
            lifetime=self.remote_dist_names_lifetime,
        )
    
    def remote_dist_names(self, package_name):
        for dist_url in self.remote_dist_urls(package_name):
            yield self._remote_dist_name_from_url(dist_url)
    
    def remote_dist_url(self, package_name, dist_name):
        for dist_url in self.remote_dist_urls(package_name):
            if dist_name == self._remote_dist_name_from_url(dist_url):
                return dist_url
        
        raise DistributionNotFound('Unknown distribution "%s" for package "%s"' % (
            dist_name, package_name,
        ))
    
    def _local_package_names(self, base_path):
        if base_path is not None and os.path.isdir(base_path):
            for filename in os.listdir(base_path):
                if os.path.isdir(os.path.join(base_path, filename)):
                    yield self._decode_basename(filename)
    
    def _local_dist_names(self, base_path, package_name):
        if base_path is not None:
            package_path = self._local_package_path(base_path, package_name)
            if os.path.isdir(package_path):
                for filename in os.listdir(package_path):
                    if os.path.isfile(os.path.join(package_path, filename)):
                        yield self._decode_basename(filename)
    
    def _local_package_path(self, base_path, package_name):
        return os.path.join(base_path, self._encode_basename(package_name))
    
    def _local_dist_filename(self, base_path, package_name, dist_name):
        return os.path.join(
            self._local_package_path(base_path, package_name),
            self._encode_basename(dist_name),
        )
    
    def _fetch_remote_package_names(self):
        package_names = []
        
        for link_url in self._iter_remote_urls(''):
            if not link_url.startswith(self.remote_url):
                continue
            
            package_name = re.search(r'^[^?#]*', link_url).group()
            package_name = package_name[len(self.remote_url):]
            package_name = package_name.rstrip('/')
            package_name = urllib.unquote(package_name)
            
            if not package_name or '/' in package_name:
                continue
            
            package_names.append(package_name)
        
        return package_names
    
    def _remote_dist_name_from_url(self, dist_url):
        return posixpath.basename(urlparse.urlparse(dist_url).path)
    
    def _fetch_remote_dist_urls(self, package_name):
        try:
            return list(self._iter_remote_urls('%s/' % urllib.quote(package_name)))
        except urllib2.HTTPError, exc:
            if exc.code == 404:
                return []
            else:
                raise
    
    def _encode_basename(self, basename):
        def encode_match(match):
            return ''.join('$%02x' % ord(char) for char in match.group())
        basename = basename.encode('ascii')
        basename = self._INVALID_BASENAME_CHRS_RE.sub(encode_match, basename)
        basename = re.sub(r'^\.', encode_match, basename)
        return basename
    
    def _decode_basename(self, basename):
        def decode_match(match):
            return chr(int(match.group()[1:], 16))
        return re.sub(r'\$[0-9a-f]{2}', decode_match, basename)
    
    def _iter_remote_urls(self, relative_url):
        """
        Fetch an HTML page, yielding all linked URLs within the same domain
        as self._remote_url.
        """
        
        root_url = urlparse.urlunparse(
            urlparse.urlparse(self.remote_url)[:2] + ('/', '', '', '')
        )
        
        page_url = urlparse.urljoin(self.remote_url, relative_url)
        
        # urllib2 honours $HTTP_PROXY, lxml.html.parse doesn't.
        tree = lxml.html.parse(urllib2.urlopen(page_url))
        
        for a in tree.getroot().iterdescendants('a'):
            if not 'href' in a.attrib:
                continue
            
            link_url = a.attrib['href']
            link_url = urlparse.urljoin(page_url, link_url)
            parsed_link_url = urlparse.urlparse(link_url)
            
            if link_url.startswith(root_url):
                yield link_url
    
    def _assert_valid_hash(self, filename, dist_url):
        match = re.search(r'#md5=(?P<md5>.*)$', dist_url)
        if match:
            expected_hash = match.group('md5')
            file_hash = self._hash_file(filename, hashlib.md5)
            if file_hash != expected_hash:
                raise InvalidHash('Invalid MD5 (expected %s, got %s)' % (
                    expected_hash, file_hash,
                ))
    
    def _hash_file(self, filename, algorithm):
        hashing_file = open(filename, 'rb+')
        try:
            file_size = os.path.getsize(filename)
            mmapping = mmap.mmap(hashing_file.fileno(), file_size)
            try:
                return algorithm(mmapping).hexdigest()
            finally:
                mmapping.close()
        finally:
            hashing_file.close()


class NaiveCachingPackageIndex(AbstractCachingPackageIndex):
    """
    Simple caching package index, for testing. Stores cache in a dictionary.
    """
    
    def __init__(self, *args, **kwargs):
        super(NaiveCachingPackageIndex, self).__init__(*args, **kwargs)
        self.cache = {}
    
    def get_cache(self, name):
        import datetime
        
        if name not in self.cache:
            return
        
        entry = self.cache[name]
        
        if entry['expires'] < datetime.datetime.now():
            del self.cache[name]
            return
        
        return entry['value']
    
    def set_cache(self, name, value, lifetime_seconds):
        import datetime
        
        self.cache[name] = {
            'value': value,
            'expires': datetime.datetime.now() + datetime.timedelta(seconds=lifetime_seconds),
        }


class DjangoCachingPackageIndex(AbstractCachingPackageIndex):
    """
    Package index using Django's cache framework.
    """
    
    def get_cache(self, name):
        return self.django_cache.get(name)
    
    def set_cache(self, name, value, lifetime_seconds):
        self.django_cache.set(name, value, lifetime_seconds)
    
    @property
    def django_cache(self):
        if not hasattr(self, '_django_cache'):
            from django.core.cache import cache
            self._django_cache = cache
        return self._django_cache
