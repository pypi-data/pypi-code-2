from __future__ import with_statement
import cmdln
import fnmatch
import os
import HTMLParser
import httplib2
import logging
import urlparse, urllib

logging.basicConfig(level=logging.WARNING, 
                    format="%(levelname)s: %(message)s")
log = logging.getLogger('mcs')

class RepositoryException(Exception):
    pass

class McRepository(object):
    def __init__(self, *args, **kwargs):
        raise NotImplementedError
    
    def list_items(self):
        raise NotImplementedError
    
    def load_item(self, name):
        raise NotImplementedError
    
    def store_item(self, name, data):
        raise NotImplementedError
    
    def _filter_items(self, item_list):
        return [name for name in item_list if name.endswith(".mcz") or name.endswith(".mcd")]

class McLocalRepository(McRepository):
    def __init__(self, path):
        self.path = os.path.abspath(path)
        assert os.path.exists(self.path) and os.path.isdir(self.path)
    
    def list_items(self):
        return self._filter_items(os.listdir(self.path))
    
    def load_item(self, name):
        with file(os.path.join(self.path, name), "rb") as f:
            return f.read()
    
    def store_item(self, name, data):
        with file(os.path.join(self.path, name), "wb") as f:
            f.write(data)

class McHttpRepository(McRepository):
    def __init__(self, url):
        self.http = httplib2.Http()
        
        urlsplit = urlparse.urlsplit(url)
        if urlsplit.username or urlsplit.password:
            self.url = urlparse.urlunsplit([
                urlsplit[0], 
                urlsplit.hostname if not urlsplit.port 
                                  else "%s:%i" % (urlsplit.hostname, urlsplit.port),
                urlsplit[2],
                urlsplit[3],
                urlsplit[4]
            ])
            self.http.add_credentials(urlsplit.username, urlsplit.password)
        else:
            self.url = urlparse.urlunsplit(urlsplit)
    
    def list_items(self):
        resp, data = self.http.request(self.url)
        if not 200 <= resp.status <= 299:
            raise RepositoryException("%i: %s" % (resp.status, resp.reason))
        link_extractor = LinkExtractor()
        link_extractor.feed(data)
        return self._filter_items(link_extractor.links)
    
    def load_item(self, name):
        resp, data = self.http.request(self._url_from_name(name))
        if not 200 <= resp.status <= 299:
            raise RepositoryException("%i: %s" % (resp.status, resp.reason))
        return data
    
    def store_item(self, name, data):
        resp, data = self.http.request(self._url_from_name(name), method="PUT", body=data)
        if not 200 <= resp.status <= 299:
            raise RepositoryException("%i: %s" % (resp.status, resp.reason))
    
    def _url_from_name(self, name):
        return urlparse.urljoin(self.url, urllib.quote(name))

def repository_for_url(url):
    if url.lower().startswith("http:") or url.lower().startswith("https:"):
        return McHttpRepository(url)
    return McLocalRepository(url)

class LinkExtractor(HTMLParser.HTMLParser):
    def reset(self):
        HTMLParser.HTMLParser.reset(self)
        self.links = []
        
    def handle_starttag(self, tag, attrs):
        if tag == "a":
            self.links.extend(value for name, value in attrs if name=="href")

class Mcs(cmdln.Cmdln):
    name = "mcs"
    
    @cmdln.alias("ls")
    @cmdln.option("-p", "--pattern", action='store', help="only show items that match a pattern")
    @cmdln.option("-v", "--verbose", action='store_true', help="print extra information")
    def do_list(self, subcmd, opts, url="."):
        """${cmd_name}: list all items in a repository
        
        ${cmd_usage}
        ${cmd_option_list}
        """
        if opts.verbose: log.setLevel(logging.INFO)
        
        items = repository_for_url(url).list_items()
        for name in self.filter_list(items, opts.pattern):
            print name
    
    @cmdln.alias("cp")
    @cmdln.option("-a", "--all", action='store_true', help="copy all items even if they already exist in the target")
    @cmdln.option("-p", "--pattern", action='store', help="only copy items that match a pattern")
    @cmdln.option("-v", "--verbose", action='store_true', help="print extra information")
    def do_copy(self, subcmd, opts, from_url, to_url="."):
        """${cmd_name}: copy all items from one repository to another
        
        ${cmd_usage}
        ${cmd_option_list}
        """
        if opts.verbose: log.setLevel(logging.INFO)
        
        from_repo = repository_for_url(from_url)
        to_repo = repository_for_url(to_url)
        done = set(to_repo.list_items())
        todo = set(from_repo.list_items())
        if not opts.all:
            todo -= done
        for name in self.filter_list(todo, opts.pattern):
            print name
            to_repo.store_item(name, from_repo.load_item(name))
    
    def filter_list(self, items, pattern):
        if not pattern:
            return items
        return [item for item in items if fnmatch.fnmatchcase(item, pattern)]
