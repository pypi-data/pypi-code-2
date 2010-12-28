from types import StringType, UnicodeType

from resource import Resource, from_pkg_stream

class CSSResource(Resource):
    """a CSS resource with support for merging and minimizing"""
    
    def __init__(self, 
                 source = u'',
                 minimize_method = None, 
                 media = ['projection', 'screen'],
                 type_ = u'text/css',
                 **kw):
        super(CSSResource, self).__init__(source, **kw)
        self.minimize_method = minimize_method
        if type(media) in (StringType, UnicodeType):
            self.media = [s.strip() for s in media.split(',')]
        else:
            self.media = media # we assume it's a list
        self.type_ = type_
        self.media.sort() # for profile generation
    
    @property
    def profile(self):
        """return the profile string for this resource. This is either a random string
        in case this resource is not mergeable."""
        if not self.merge:
            return self.hash
            
        return "%s-%s" %(self.media, self.type_)

def css_from_pkg_stream(package, filename, **kw):
    return from_pkg_stream(package, filename, cls=CSSResource, **kw)
    