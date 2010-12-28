from pkg_resources import resource_stream, resource_string, resource_filename

import md5
import datetime
import os

class Resource(object):
    """A resource is e.g. some CSS or Javascript file which needs to be included in an HTML
    page. A ``Resource`` can be used by a ``ResourceManager`` to merge similar resources
    together. It can also be derived into specialized classes for CSS and Javascript
    which might have different requirements.
    
    The ``Resource`` takes a ``source`` string and converts it to a unicode string which
    is accessible as ``data``. Moreover it computes a ``hash`` which can be used to 
    uniquely identify a resource. 
    """
    
    def __init__(self,
                 source=u'',
                 name=u"", 
                 merge = False, 
                 encoding="utf-8", 
                 prio=1,
                 filename=None,
                 processors=[],
                 **kwargs):
        """initialize a generic ``Resource`` object with the ``source`` string,
        an optional ``name``, a flag ``merge`` defining whether this resource can be
        merged with similar resources, the ``encoding`` of the ``source`` string, defaulting
        to ``utf-8`` and an optional ``prio`` attribute which defines the ordering of this
        resource in the resource manager. The lower the priority the earlier it appears.
        
        ``filename`` is used for the auto reloader. It is a filename which is
        checked for it's modification date. In production you might not need it.
        
        ``processors`` is a list of processor functions which take the input and e.g.
        minify it.
        
        """
        self.processors = processors
        self.encoding = encoding
        self.data = self.process(source.decode(encoding))
        self.hash = unicode(md5.new(self.data).hexdigest())
        self.name = name
        self.prio = prio
        self.merge = merge
        self.filename = filename
        if filename is not None:
            self.mtime = os.stat(filename).st_mtime
        else:
            self.mtime = None
        
    def __cmp__(self, other):
        """compare two resources with each other. For this we first sort by name
        and then inside those named group by priority (as name changes will create new
        clusters anyway)"""
        r=cmp(self.name, other.name)
        if r==0:
            r=cmp(self.prio, other.prio)
        return r

    def process(self, s):
        """run the source code s through all the processors"""
        for p in self.processors:
            s=p(s)
        return s
        
    @property
    def profile(self):
        """return the profile for this resource. Profiles define whether similar resources
        can be merged together or not as resources with the same profile have the option
        to be merged together. This can be the case e.g. for some CSS resources with the
        same media type. If the ``merge`` flag is ``False`` this resource will never be 
        merged and we use the ``hash`` as the profile in order to make profiles unique
        in any case.
        In this generic case we return an empty profile string as we don't have enough
        information on the context to do an educated guess.
        """
        if not self.merge:
            return self.hash
        else:
            return u''
            
    @property
    def modified(self):
        """return True or False depending whether this resource has been modified or not"""
        if self.filename is None:
            return False # no file, no modification
        return os.stat(self.filename).st_mtime > self.mtime
        
    def reload(self):
        """reload this resource. Only works if filename is set"""
        if self.filename is None:
            return 
        fp = open(self.filename, "r")
        data = fp.read()
        fp.close()
        
        self.mtime = os.stat(self.filename).st_mtime
        self.data = data.decode(self.encoding)
        self.hash = unicode(md5.new(self.data).hexdigest())


def from_pkg_stream(package, filename, cls = Resource, auto_reload=False, **kw):
    """a factory function for creating a new ``Resource`` object from a package
    resource stream. ``package`` is the package, usually passed as ``__name__``, 
    filename is the path to the file relative to the package, ``cls`` is the class
    to instantiate which needs to be derived from ``Resource``. Optionally you
    can give additional keyword arguments which are then passed to the class.
    
    ``auto_reload`` defines whether the resource_filename will also be stored and thus
    resource reloading is possible. The default is ``False``."""
    
    stream = resource_stream(package, filename)
    stream.seek(0)
    data = stream.read()
    if auto_reload:
        kw['filename'] = resource_filename(package, filename)
    return cls(data, **kw)

