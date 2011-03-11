"""Wille Server default views

"""
import os

from utils import fileshare_make_response, metadata_to_http_headers

class Frontpage:
    def GET(self, request_handler):
        wille_client = request_handler.wille_client()
        
        # Send response headers
        request_handler.send_response(200)
        request_handler.send_header('Content-type', 'text/html')
        request_handler.end_headers()
        
        # TODO: Move HTML to a template file and use render_template (low priority)
        str = ''
        str += '<h1>Wille Node at %s</h1>' % (request_handler.datastore('hostname'))
        app_count = len(request_handler.datastore('apps'))
        str += '<h2><a href="apps/">Apps (%s)</a></h2>' % (app_count)
        service_count = len(wille_client.services())
        str += '<h2><a href="services/">Services (%s)</a></h2>' % (service_count)
        neighbour_count = len(wille_client.servicepool.pools(pooltype='http'))
        str += '<h2>Neighbours (%s)</h2>' % (neighbour_count)
        str += '<h2><a href="management/">Management</a></h2>'
        return str

class Management:
    def GET(self, request_handler):
        self.wille_client = request_handler.wille_client()
        self.hostname = request_handler.datastore('hostname') # Get hostname
        self.apps = request_handler.datastore('apps')
        self.url_prefix = 'http://%s:%s/' % (self.hostname, request_handler.server.server_port)
        self.service_url_prefix = '%sservices/' % (self.url_prefix)
        self.server_visibility = request_handler.datastore('server_visibility')
        
        # Send response headers
        request_handler.send_response(200)
        request_handler.send_header('content-type', 'text/html')
        request_handler.end_headers()
        
        str = '<h1><a href="/">%s</a> &gt; Management</h1>' % (request_handler.datastore('hostname'))

        str += '<p><b>Enabled profiles: %s</b></p>' % (request_handler.datastore('profiles'))
        
        str += '<h2>Services</h2>'
        self.services = self.wille_client.services()
        str += '<table>'
        str += '<tr>'
        str += '<td><b>Service</b></td>'
        str += '<td><b>Profiles</b></td>'
        str += '<td><b>Pool</b></td>'
        str += '<td><b>Type</b></td>'
        str += '<td><b>Status</b></td>'
        str += '<td><b>Times executed</b></td>'
        str += '<td><b>Visibility</b></td>'
        str += '<td><b>Published</b></td>'
        str += '</tr>'
        for service in self.services:
            service.reload() # Reload service to get latest description
            str += '<tr>'
            str += '<td><a href="%s%s/">%s</a></td>\n' % (self.service_url_prefix, service.name, service.name)
            str += '<td>%s</td>\n' % (service.profiles)
            str += '<td>%s</td>\n' % (service.pooltype)
            str += '<td>%s</td>\n' % (service.type)
            str += '<td><abbr title="%s">%s</abbr></td>\n' % (service.error_log, service.status)
            #str += '<td>%s</td>\n' % (service.description)
            str += '<td>%s</td>\n' % (service.exec_count)
            str += '<td>%s</td>\n' % self.server_visibility
            str += '<td>%s</td>\n' % service.published
            str += '</tr>\n'
        str += '</table>'

        str += '<h2>Apps</h2>'
        str += '<table>'
        str += '<tr>'
        str += '<td><b>App</b></td>'
        str += '<td><b>Profiles</b></td>'
        str += '<td><b>Description</b></td>'
        str += '</tr>'
        for app in self.apps:
            str += '<tr>'
            str += '<td><a href="%s">%s</a></td>\n' % (self.apps[app].make_url(self.url_prefix), app)
            str += '<td>%s</td>\n' % (self.apps[app].profiles)
            str += '<td>%s</td>\n' % (self.apps[app].properties['description'])
            str += '<td>%s</td>\n' % (self.apps[app].full_path)
            str += '</tr>\n'
        str += '</table>'
        
        return str

class AppList:
    def GET(self, request_handler):
        self.apps = request_handler.datastore('apps')
        
        # Send response headers
        request_handler.send_response(200)
        request_handler.send_header('content-type', 'text/html')
        request_handler.end_headers()
        
        str = '<h1><a href="/">%s</a> &gt; Apps</h1>' % (request_handler.datastore('hostname'))
        
        for app in self.apps:
            str += '<p><a href="%s/">%s</a></p>' % (self.apps[app].name, self.apps[app].name)
        return str

class ServiceList:
    def GET(self, request_handler):
        wille_client = request_handler.wille_client()
        hostname = request_handler.datastore('hostname') # Get hostname
        
        # Send response headers
        request_handler.send_response(200)
        request_handler.send_header('Content-type', 'application/rdf+xml; charset=utf-8')
        request_handler.end_headers()
        
        url_prefix = 'http://%s:%s/' % (hostname, request_handler.server.server_port)
        service_url_prefix = '%sservices/' % (url_prefix)
        
        str = '<?xml version="1.0" encoding="utf-8"?>\n'+\
              '<rdf:RDF xmlns="http://purl.org/rss/1.0/"\n'+\
              'xmlns:dc="http://purl.org/dc/elements/1.1/"\n'+\
              'xmlns:wille="http://tut.fi/hypermedia/wille/"\n'+\
              'xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">\n'+\
              '<channel rdf:about="'+url_prefix+'">\n'+\
              '<title>'+url_prefix+'services</title>\n'+\
              '<description>Services RSS</description>\n'+\
              '<link>'+url_prefix+'</link>\n'+\
              '<items>'
        str += '<rdf:Seq>\n'
        services_list = wille_client.services()
        for service in services_list:
            if service.status_ok():
                str += '  <rdf:li rdf:resource="%s%s/"/>\n' % (service_url_prefix, service.name)
        str += '</rdf:Seq></items></channel>\n'
        for service in services_list:
            if service.status_ok():
                str += '<item rdf:about="%s%s/">\n' % (service_url_prefix, service.name)
                str += '  <title><![CDATA['+service.name+']]></title>\n'
                str += '  <link>%s%s/</link>\n' % (service_url_prefix, service.name)
                str += '  <dc:date>%s</dc:date>\n' % service.published
                str += '  <dc:description><![CDATA[%s]]></dc:description>\n' % (service.description)
                str += '  <dc:identifier>%s%s/</dc:identifier>\n' % (service_url_prefix, service.name)
                str += '  <dc:type>%s</dc:type>\n' % (service.type)
                if service.profiles:
                    for profile in service.profiles:
                        str += '  <wille:profile>%s</wille:profile>\n' % (profile)
                str += '</item>\n'
        str += '</rdf:RDF>'
        return str

class ServeFiles:
    """ Customisable View for sharing a folder """
    def GET(self, request, filename):
        """Simple fileserver-like handler for sharing all files in given directory
           Parameters:
            request - Wille Request Handler
            filename - Filename as retrieved from request 
        """
        
        # Reflection: get model for this app
        app = request.app
        #match = request.match_path()
        shared_dir = request.rule[3]
        #def match_path(self, path, urls):
        shared_path = os.path.realpath( os.path.join( app.full_path, shared_dir ) )
        
        print shared_path
        
        # Select correct file to return
        if len(filename)<1:
            return fileshare_make_response(shared_path, 'index.html')
        try:
            return fileshare_make_response(shared_path, filename)
        except:
            # File was not found -- try parsing query string
            # For example: "index.html?param=1" -> discard "?param=1"
            parts = filename.split('?',1)
            try:
                return fileshare_make_response(shared_path, parts[0])
            except:
                pass

        # File not found response
        response = 'File Not Found: %s' % filename
        return (response, {'Content-type': 'text/html'}, 404)

class ServiceExecute:
    def GET(self, request_handler, service_name):
        wille_client = request_handler.wille_client()
        
        # Try to locate requested service
        try:
            service = wille_client.services(name=service_name)[0]
        except:
            # Service not found
            request_handler.send_response(404)
            return "Service not found"

        # Execute service
        try:
            # Extract input data
            data = request_handler.input()
            
            # Set debug status to service
            service.debug = request_handler.datastore('debug')
            
            # Execute service
            result = service.execute(params=data, servicepool=wille_client.servicepool, keyring=wille_client.keyring)
        except Exception, e:
            # Some scaffolding
            str = '<h1><a href="/">%s</a> &gt; ' % (request_handler.datastore('hostname'))
            str += '<a href="../">Services</a> &gt; %s</h1><p>%s</p>' % (service_name, service.description)
            str += '<form action="" method="post" enctype="multipart/form-data">\n'
            str += '<h2>Execute service</h2>'
            for param in service.all_params:
                param_type = service.properties.get('parameters.%s.type' % param, 'text')
                param_size = service.properties.get('parameters.%s.size' % param, '80')
                optional_str = ''
                try:
                    service.required_params.index(param)
                except ValueError:
                    optional_str = '(optional)'
                    
                # Type-specific tailoring
                extra_html=''
                if param_type=='date':
                    param_size=10
                    extra_html = '<em>(Input a date in format YYYY-MM-DD)</em>'
                if param_type=='datetime':
                    param_size=19 
                    extra_html = '<em>(Input a date and time in format YYYY-MM-DD HH:MM:SS)</em>'
                if param_type=='time':
                    param_size=8
                    extra_html = '<em>(Input time in format HH:MM:SS)</em>'
                    
                str += ('<p><label for="%s" style="float: left; width: 120px;">%s</label>'+ \
                        '<input type="%s" id="%s" name="%s" value="%s" size="%s"/><label for="%s"> %s %s</label></p>\n') % \
                        (param, param, param_type, param, param, '', param_size, param, optional_str, extra_html)
            str += '<p><input type="submit" value="Execute"/></p>\n'
            str += '</form>'
            return str
        
        # HTTP Response + headers
        response_code = 200
        if result.metadata.has_key('code'):
            response_code = result.metadata['code']
        request_handler.send_response( response_code )
        headers = metadata_to_http_headers( result.metadata )
        for header in headers:
            request_handler.send_header(header, headers[header])
        request_handler.end_headers()
                    
        return result.data

    def POST(self, request_handler, service_name):
        return self.GET(request_handler, service_name)        

class SharedFilesView:
    def GET(self, context, filename):
        shared_path = os.path.realpath( os.path.join( context.datastore('wille_root_dir'), './shared' ) )
    
        # Select correct file to return
        if len(filename)<1:
            return fileshare_make_response(shared_path, 'index.html')
        try:
            return fileshare_make_response(shared_path, filename)
        except:
            # File was not found -- try parsing query string
            # For example: "index.html?param=1" -> discard "?param=1"
            parts = filename.split('?',1)
            try:
                return fileshare_make_response(shared_path, parts[0])
            except:
                pass

        # File not found response
        response = 'File Not Found: %s' % filename
        return (response, {'Content-type': 'text/html'}, 404)

# Run tests
if __name__ == "__main__":
    import doctest
    doctest.testmod()
