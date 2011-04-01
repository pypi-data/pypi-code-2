#!/usr/bin/env python
################ Test Server #################################
import BaseHTTPServer, cgi
from openid2rp import *

# supported providers
providers = (
    ('Google', 'http://www.google.com/favicon.ico', 'https://www.google.com/accounts/o8/id'),
    ('Yahoo', 'http://www.yahoo.com/favicon.ico', 'http://yahoo.com/'),
    ('Verisign', 'http://pip.verisignlabs.com/favicon.ico', 'http://pip.verisignlabs.com'),
    ('myOpenID', 'https://www.myopenid.com/favicon.ico', 'https://www.myopenid.com/'),
    ('Launchpad', 'https://login.launchpad.net/favicon.ico', 'https://login.launchpad.net/')
    )
             
sessions = []
class Handler(BaseHTTPServer.BaseHTTPRequestHandler):

    def write(self, payload, type):
        self.send_response(200)
        self.send_header("Content-type", type)
        self.send_header("Content-length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def do_GET(self):
        if self.path == '/':
            return self.root()
        path = self.path
        i = path.rfind('?')
        if i >= 0:
            querystring = path[i+1:]
            query = cgi.parse_qs(querystring)
            path = path[:i]
        else:
            query = {}
        if path == '/':
            if 'provider' in query:
                prov = [p for p in providers if p[0]  == query['provider'][0]]
                if len(prov) != 1:
                    return self.not_found()
                prov = prov[0]
                services, url, op_local = discover(prov[2])
                try:
                    session = associate(services, url)
                except ValueError, e:
                    return self.error(str(e))
                sessions.append(session)
                self.send_response(307) # temporary redirect - do not cache
                self.send_header("Location", request_authentication
                                 (services, url, session['assoc_handle'],
                                  self.base_url+"?returned=1"))
                self.end_headers()
                return
            if 'claimed' in query:
                kind, claimed = normalize_uri(query['claimed'][0])
                if kind == 'xri':
                    return self.error('XRI resolution not supported')
                res = discover(claimed)
                if res is None:
                    return self.error('Discovery failed')
                services, url, op_local = res
                try:
                    session = associate(services, url)
                except ValueError, e:
                    return self.error(str(e))
                sessions.append(session)
                self.send_response(307)
                self.send_header("Location", request_authentication
                                 (services, url, session['assoc_handle'],
                                  self.base_url+"?returned=1",
                                  claimed, op_local))
                self.end_headers()
                return                
            if 'returned' in query:
                if 'openid.identity' not in query:
                    return self.rp_discovery()
                handle = query['openid.assoc_handle'][0]
                for session in sessions:
                    if session['assoc_handle'] == handle:
                        break
                else:
                    session = None
                if not session:
                    return self.error('Not authenticated (no session)')
                try:
                    signed = authenticate(session, querystring)
                except Exception, e:
                    self.error("Authentication failed: "+repr(e))
                    return
                if 'openid.claimed_id' in query:
                    if 'claimed_id' not in signed:
                        return self.error('Incomplete signature')
                    claimed = query['openid.claimed_id'][0]
                else:
                    # OpenID 1, claimed ID not reported - should set cookie
                    if 'identity' not in signed:
                        return self.error('Incomplete signature')
                    claimed = query['openid.identity'][0]
                payload = "Hello "+claimed+"\n"
                ax = get_ax(querystring, get_namespaces(querystring), signed)
                sreg = get_sreg(querystring, signed)
                email = get_email(querystring)
                if email:
                    payload += 'Your email is '+email+"\n"
                else:
                    payload += 'No email address is known\n'
                if 'nickname' in sreg:
                    username = sreg['nickname']
                elif "http://axschema.org/namePerson/first" in ax:
                    username = ax["http://axschema.org/namePerson/first"]
                    if "http://axschema.org/namePerson/last" in ax:
                        username += "." + ax["http://axschema.org/namePerson/last"]
                else:
                    username = None
                if username:
                    payload += 'Your nickname is '+username+'\n'
                else:
                    payload += 'No nickname is known\n'
                if isinstance(payload, unicode):
                    payload = payload.encode('utf-8')
                return self.write(payload, "text/plain")
                
        return self.not_found()

    

    def debug(self, value):
        payload = repr(value)
        if isinstance(payload, unicode):
            payload = payload.encode('utf-8')
        self.write(payload, "text/plain")

    def error(self, text):
        if isinstance(text, unicode):
            text = text.encode('utf-8')
        self.write(text, "text/plain")

    def root(self):
        payload = u"<html><head><title>OpenID login</title></head><body>\n"
        
        for name, icon, provider in providers:
            payload += u"<p><a href='%s?provider=%s'><img src='%s' alt='%s'></a></p>\n" % (
                self.base_url, name, icon, name)
        payload += u"<form>Type your OpenID:<input name='claimed'/><input type='submit'/></form>\n"
        payload += u"</body></html>"
        self.write(payload.encode('utf-8'), "text/html")

    def rp_discovery(self):
        payload = '''<xrds:XRDS  
                xmlns:xrds="xri://$xrds"  
                xmlns="xri://$xrd*($v*2.0)">  
                <XRD>  
                     <Service priority="1">  
                              <Type>http://specs.openid.net/auth/2.0/return_to</Type>  
                              <URI>%s</URI>  
                     </Service>  
                </XRD>  
                </xrds:XRDS>
        ''' % (self.base_url+"/?returned=1")
        self.write(payload, 'application/xrds+xml')

    def not_found(self):
        self.send_response(404)
        self.end_headers()
        
# OpenID providers often attempt relying-party discovery
# This requires the test server to use a globally valid URL
# If Python cannot correctly determine the base URL, you
# can pass it as command line argument
def test_server():
    import socket, sys
    if len(sys.argv) > 1:
        base_url = sys.argv[1]
    else:
        base_url = "http://" + socket.getfqdn() + ":8000/"
    print "Listening on", base_url
    Handler.base_url = base_url
    #BaseHTTPServer.HTTPServer.address_family = socket.AF_INET6
    httpd = BaseHTTPServer.HTTPServer(('', 8000), Handler)
    httpd.serve_forever()

if __name__ == '__main__':
    test_server()
