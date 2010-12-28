from resource import Resource, from_pkg_stream
import jsmin

minifier = jsmin.JavaScriptMinifier()

def minify(s):
    """minify the string by using jsmin"""
    return minifier.JSMinify(s)

class JSResource(Resource):
    """a JS resource with support for merging and minimizing"""
    
    def __init__(self, 
                 source = u'',
                 minimize_method = None, 
                 type_ = u"text/javascript",
                 processors=[],
                 **kw):
        """initialize the JS resource. You have to give ``source`` as a string,
        the ``minimize_method`` of ``None`` or ``jsmin`` and the mimetype ``type_`` 
        which is probably the default of ``text/javascript``.
        Additional keyword arguments are passed to the ``Resource`` superclass."""
        if minimize_method=="jsmin":
            processors= processors +[minify]
        super(JSResource, self).__init__(source, processors=processors, **kw)
        self.minimize_method = minimize_method
        self.type_ = type_

    @property
    def profile(self):
        """return the profile string for this resource. This is either a random string
        in case this resource is not mergeable."""
        if not self.merge:
            return self.hash
            
        return unicode(self.type_)

def js_from_pkg_stream(package, filename, **kw):
    return from_pkg_stream(package, filename, cls=JSResource, **kw)
