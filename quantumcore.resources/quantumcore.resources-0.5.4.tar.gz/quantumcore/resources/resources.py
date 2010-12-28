from UserList import UserList
from urlparse import urlparse
from calendar import timegm
from datetime import timedelta, datetime
from email.utils import formatdate

from quantumcore.exceptions import NotFound

from cluster import CSSCluster, JSCluster    

class ResourceManager(object):
    """a Resource Manager which is able to organize resources (CSS or JS) into clusters
    of similar resources which eventually can be merged together into single files. Moreover
    it provides caching friendly naming of the resulting resource files and provided 
    appropriate caching headers on serving merged resources.
    
    Internally we have a list of the original resources inside ``orig_resources`` and 
    a list of the resulting clusters inside ``clusters``. ``clusters`` is a dictionary
    with the key being the name of the clusters. The value is a list of ``ResourceCluster``
    lists which contain those resources with the same profile. The profile can be e.g. 
    the media type for CSS resources. The ``Resource`` object is responsible for providing
    the profile string. 
    
    In the end we have for the ``clusters`` variable a key pointing to a list of
    ``ResourceCluster`` objects which in turn are lists of resources.
    
    A Resource Manager also supports auto reloading if you initialize it with 
    ``auto_reload=True``. This will be delegated to the clusters which have to do the
    checking themselves.
    """
    
    cluster_class = None
    mimetype = "application/octet-stream"
    
    def __init__(self, 
                 resources, 
                 prefix_url=u"/static", 
                 no_merge = False,
                 fqdn = "",
                 auto_reload=False):
        """initialize the ``Resources`` object by storing the resources to be handled"""
        
        self.orig_resources = [] # a simple list of all source resources
        self.clusters = {} # a dict containing name -> [cluster] pairs 
        self.filenames = {} # all the filenames we are managing which equal to clusters
        self.basenames = {} # the base filenames without hash => cluster
        self.prefix_url = prefix_url
        self.prefix_path = urlparse(prefix_url)[2]
        self.auto_reload = auto_reload
        self.fqdn = fqdn
        
        # first append the resources to our registry
        for resource in resources:
            self.append(resource)
            
        # then in one go compute the clusters if permitted
        self._dirty = True
        if not no_merge:
            self.merge()
            
    def append(self, resource):
        """append a new resource to this registry and recompute the clusters"""
        self.orig_resources.append(resource)
        self._dirty = True
        
                
    def merge(self):
        """compute clusters from the stored resources. The algorithm is as follows:
        
        1. Sort all resources by their priority
        2. Iterate over all resources
        3. In case the name is different than the one before, create a new cluster
        4. In case the profile is different from the one before, create a new cluster
        5. In case the resource is not mergeable create a new cluster
        6. Append the resource to the active cluster
        """
        
        self.clusters = {} # name => [cluster]
        self.filenames = {}
        self.basenames = {}
        self.orig_resources.sort() # first sort all resources by their prio
        used_names = {} # remember the names we have used (name => counter)
         
        active_profile = None # active profile in loop
        active_cluster = None # active cluster in loop
        active_name = None        

        for resource in self.orig_resources:
            profile = resource.profile
            name = resource.name

            # create a new cluster if something changes
            if name != active_name or profile!=active_profile:
                # merge an eventually active cluster
                if active_cluster is not None:
                    active_cluster.merge()
                if not self.clusters.has_key(name):
                    no = None
                    self.clusters[name] = [] # initialize it
                else:
                    no = len(self.clusters[name])

                # create the new cluster
                active_name = name
                active_profile = profile
                active_cluster = self.cluster_class(name = name, prefix_url = self.prefix_url, no = no)
                self.clusters[name].append(active_cluster)
                self.basenames[active_cluster.basename] = active_cluster
                self.filenames[active_cluster.filename] = active_cluster
            active_cluster.append(resource)
        if active_cluster is not None:
            active_cluster.merge() # merge the last cluster as well

        self._dirty = False
        return self.clusters
    
    def _get_clusters_for_name(self, name):
        """return all clusters with the given name"""
        return self.clusters[name]
        
    def _get_all_clusters(self):
        """return all clusters"""
        all = []
        for name in self.clusters.keys():
            all = all + self.clusters[name]
        return all
        
    def check_if_modified(self, name=None):
        """ask all clusters if they have been modified and mark this manager
        as dirty if so. If name is not None only the named clusters will be checked"""
        if name is None:
            clusters = self._get_all_clusters()
        else:
            clusters = self._get_clusters_for_name()

        dirty = False
        for cluster in clusters:
            if cluster.modified:
                dirty = True
                cluster.reload()
                # we do not break here because all modified clusters need to be reloaded
        self._dirty = dirty
        
    def __call__(self, name=u"", fqdn=True):
        """return a list of HTML link tags"""
        if self.auto_reload:
            self.check_if_modified()
        if self._dirty:
            self.merge()
        res = []
        for cluster in self._get_clusters_for_name(name):
            res.append(cluster(fqdn=self.fqdn))
        return "\n".join(res)
        
    def get_payload(self, url, check_hash = False):
        """render the resource for the named ``url``. If ``check_hash`` is ``True`` then
        also the hash is checked and needs to be correct. Otherwise the resource is even
        rendered if it's not uptodate."""
        if self.auto_reload:
            self.check_if_modified()
        if self._dirty:
            self.merge() 
        foo, foo, path, foo, params, foo = urlparse(url)
        if not path.startswith(self.prefix_path):
            raise NotFound(url, "prefix not know to resource registry. Prefix known '%s' " %self.prefix_path)

        if check_hash:
            # TODO: Better check for hash by deconstructing the params
            cluster = self.filenames[path+params]
        else:
            cluster = self.basenames[path]
        # TODO: If not found raise a more meaningful exception with explanation here
        # might also be a NotFound exception actually
        
        return cluster.render() # render the cluster
    
    def headers(self, timeout=3600):
        """return a list of headers in the format (name, value)"""
        timeout_date = datetime.utcnow() + timedelta(seconds = timeout)
        t = timegm(timeout_date.utctimetuple())
        expires = formatdate(t, localtime=False, usegmt=True)

        headers = [
            ('Cache-Control', 'max-age=%d' %timeout),
            ('Content-Type', self.mimetype),
            ('Expires', expires),
        ]
        return headers
        
         
    def render_wsgi(self, environ, start_response, timeout=3600):
        url = environ['PATH_INFO']

        # TODO: Catch NotFound exception
        
        data = self.get_payload(url)
        
        headers = self.headers(timeout)
        headers.append(('Content-Length', '%d' %len(data)), )
        start_response("200 Ok", headers)
        return data,
        
        
class CSSResourceManager(ResourceManager):
    cluster_class = CSSCluster
    mimetype = "text/css"
        
class JSResourceManager(ResourceManager):

    cluster_class = JSCluster
    mimetype = "text/javascript"
        
                
                
