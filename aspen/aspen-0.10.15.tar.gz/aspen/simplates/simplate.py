from aspen.simplates import PAGE_BREAK


class Simplate(object):
    """This is a regular simplate. Override the hooks for *.json and *.sock.
    """

    def __init__(self, raw):
        raw = raw.replace("^L", PAGE_BREAK)
        pages = raw.split(PAGE_BREAK)
        npages = len(pages)
        self.one, self.two, self.three = self.parse(pages, npages)

    def parse(self, pages, npages):
        """Given a sequence of raw strings, return three page strings.
        """
        if npages == 1:
            one = two = None
            three = pages[0] 
        elif npages == 2:
            one = "" # Empty string instead of None; only None if two is None
            two, three = pages
        elif npages == 3:
            one, two, three = pages
        else:
            raise SyntaxError( "Simplate %s may have at most " % request.fs
                             + "three pages; it has %d." % npages
                              )

        
        three = self.trim_initial_newline(three)

        return (one, two, three)
   
    def trim_initial_newline(self, template):
        """Trim any initial newline from page three.
        
        This is a convenience. It's nice to put ^L on a line by itself, but
        really you want the template to start on the next line.

        """
        try:
            if template[0] == '\r':
                if template[1] == '\n':
                    template = template[2:]
            elif template[0] == '\n':
                template = template[1:]
        except IndexError:
            pass


    def handle(self, request, response=None):
        """Given a Request, return or raise a Response.
        """
        if response is None:
            response = Response()

        mimetype, namespace, script, template = load(request)

        if namespace is None:
            response.body = template
        else:
           
            # Populate namespace.
            # ===================
        
            namespace.update(request.namespace)
            namespace['request'] = request
            namespace['response'] = response
       

            # Exec the script.
            # ================
        
            if script:
                exec script in namespace
                response = namespace['response']


            # Process the template.
            # =====================
            # If template is None that means that that page was empty.
        
            if template is not None:
                response.body = template.generate(**namespace)

        
        # Set the mimetype.
        # =================
        # We guess based on the filesystem path, not the URL path. Also, we 
        # special case JSON.
       
        if mimetype == 'application/json':
            if template is None:                # dynamic
                if not isinstance(response.body, basestring):
                    # json.dumps is guaranteed to exist here.
                    response.body = json.dumps( response.body
                                              , cls=FriendlyEncoder
                                               )
            else:                               # static
                pass
            response.headers.set('Content-Type', request.json_content_type)
        
        if response.headers.one('Content-Type') is None:
            if mimetype.startswith('text/'):
                mimetype += "; charset=UTF-8" 
            response.headers.set('Content-Type', mimetype)


        # Send it on back up the line.
        # ============================

        return response

