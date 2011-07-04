from aspen import json
from aspen.simplates.simplate import Simplate


class JSONSimplate(Simplate):

    def __init__(self, *a, **kw):
        """Extend to check for json. By now we know we're not static.
        """
        if json is None:
            raise LoadError("Neither json nor simplejson was found. Try "
                            "installing simplejson to use dynamic JSON "
                            "simplates. See "
                            "http://aspen.io/simplates/json/#libraries for "
                            "more information.")
        super(JSONSimplate, self).__init__(self, *a, **kw)

    def parse(self, pages, npages):
        """Override to look for two pages instead of three.
        """

        three  = None
        if npages == 1:
            one = None
            two = pages[0]
        elif npages == 2:
            one, two = pages
        else:
            raise SyntaxError( "JSON simplate %s may have at " % request.fs
                             + "most two pages; it has %d." % npages
                              )

        return (one, two, three) 
