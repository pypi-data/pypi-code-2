from resource import Resource, from_pkg_stream

class JSTResource(Resource):
    """This is a resource which represents a template for jsontemplate.
    Basically it reads a file containing the template and returns another file
    which contains the template as a javascript string variable, e.g.
    
    var tmpl1 = "<h1>Template!</h1>\nSuper Duper"

    The name of the variable is determined by the ``tmpl`` attribute.

    """
    
    def __init__(self, 
                 source = u'',
                 type_ = u"text/javascript",
                 tmpl = u'',
                 **kw):
        super(JSTResource, self).__init__(source, **kw)
        self.type_ = type_
        self.tmpl = tmpl
        
        # replace the data by the javascript template
        self.data = self._generate_js(self.data)
        
    def _generate_js(self, data):
        """quote all data in the template and make it a one line string"""
        data = data.replace("\n", "\\n")
        data = data.replace('"', '\\"')
        
        js = """var %s = jsontemplate.Template("%s");  """ %(self.tmpl, data)
        return js
    
    @property
    def profile(self):
        """return the profile string for this resource. This is either a random string
        in case this resource is not mergeable."""
        if not self.merge:
            return self.hash
            
        return unicode(self.type_)
        
    def reload(self):
        """reload the template"""
        super(JSTResource, self).reload()
        self.data = self._generate_js(self.data)

def jst_from_pkg_stream(package, filename, **kw):
    return from_pkg_stream(package, filename, cls=JSTResource, **kw)
