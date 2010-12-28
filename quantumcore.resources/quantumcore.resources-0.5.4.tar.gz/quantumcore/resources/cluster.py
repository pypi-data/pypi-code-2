from UserList import UserList
from urlparse import urljoin, urlparse
import md5

class Cluster(UserList):
    """a base class for all clusters"""
    
    default_name = u'' # the default name such as "style" or "script"
    resource_suffix = u'' # the suffix for resources, e.g. "css" or "js"
    
    def __init__(self, 
                 name = u'',
                 prefix_url = '/static', 
                 minimize_method=None, 
                 no=None):
        """initialize a new cluster with ``prefix_url`` being the URL to where
        the resources are served which can also be just an absolute path. An example
        would be ``/static/css``. ``minimize_method`` defines which method should
        be used for packing the data, ``None`` meaning no packing which is also the default.
        Subclasses of this class need to define appropriate actions for packing. Also note
        that resources contained in this cluster should all require the same minimize method.
        ``no`` is the number to be used as suffix for the filename if multiple clusters
        with the same name exist. ``None`` means that no suffix should be used. 
        
        Internally this cluster will also compute a ``hash`` over the contents of the
        cluster for uniquely identifying it. ``None`` means that no has has been
        computed yet."""
        if prefix_url[-1]!='/':
            prefix_url=prefix_url+"/" # make sure the prefix ends with a "/"
        self.prefix_url = prefix_url
        self.name = name
        self.hash = None
        self.no = no
        self.minimize_method = minimize_method
        UserList.__init__(self)
                
        self.resource_string = unicode()
        self._dirty = True # flag that this cluster hasn't been merged yet

    @property
    def basename(self):
        """returns the filename without the hash. This should be used to identify
        a resource on ingress."""
        if self._dirty:
            self.merge()

        name = self.name

        # if the name of this cluster is empty, then use the default name for it
        if name == u'':
            name = self.default_filename

        prefix_url = urlparse(self.prefix_url).path
        if self.no is None:
            return "%s%s.%s" %(prefix_url, name, self.resource_suffix)
        else:
            return "%s%s-%s.%s" %(prefix_url, name, self.no, self.resource_suffix)
        
    
    @property
    def filename(self):
        """compute the filename based on the name of the cluster and the numerical
        suffix"""
        basename = self.basename
        assert self.hash is not None, "Hash should not be None after merging resources"
        
        return "%s?h=%s" %(basename, self.hash)

    @property
    def href(self):
        """compute the link to this cluster"""
        return urljoin(self.prefix_url, self.filename)

    def append(self, resource):
        """append a resource"""
        self.data.append(resource)
        self._dirty = True
        
    def merge(self):
        """merge resources according to their sortkey"""
        self.data.sort() # sort by sortkey 
        self.resource_string = reduce(lambda s,r: s+u"\n"+r.data, self.data, unicode())
        self.hash = md5.new(self.resource_string).hexdigest()
        self._dirty = False

    def render(self, encoding="utf-8"):
        """render this cluster. You can optionally give an ``encoding`` to which to convert
        the unicode strings. Default is ``utf-8``"""
        if self._dirty:
            self.merge()
        return self.resource_string.encode(encoding)
        
    @property
    def modified(self):
        """return ``True`` or ``False`` depending on whether a resource in this cluster
        has been modified or not"""
        for resource in self.data:
            if resource.modified:
                return True # one modified resource is enough to reload everything
        return False
        
    def reload(self):
        """reload this cluster by reloading all resources belonging to it"""
        for resource in self.data:
            resource.reload()
        

class CSSCluster(Cluster):
    """a simple list of CSS resources. It additionally knows how to render, link and merge
    CSS based resources."""
    
    default_filename = u"style"
    resource_suffix = u"css"
        
    def __call__(self, fqdn=None):
        """render the resources as links. If a fqdn is given, prepend this before the path"""
        media = ", ".join(self.data[0].media)
        type_ = self.data[0].type_
        url = self.href
        if fqdn is not None:
            url = urljoin(fqdn,url)
        d = (url, media, type_)
        return """<link href="%s" media="%s" rel="stylesheet" type="%s" />""" %d
        
        

class JSCluster(Cluster):
    """a cluster for javascript resources"""
    
    default_filename = u"script"
    resource_suffix = u"js"
            
    def __call__(self, fqdn=None):
        """render the resources as links. If a fqdn is given, prepend this before the path"""
        type_ = self.data[0].type_
        url = self.href
        if fqdn is not None:
            url = urljoin(fqdn,url)
        d = (url, type_)
        return """<script src="%s" type="%s"></script>""" %d
    
    
