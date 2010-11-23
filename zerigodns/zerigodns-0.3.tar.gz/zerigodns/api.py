''' Copyright 2009 Peter Sanchez <petersanchez@gmail.com>.  
    See BSD-LICENSE for license information.
    
    Classes used to interact with Zerigo DNS API
'''
import base64
import httplib
import urlparse
from parser import Parser
from urllib import urlencode


class ZerigoError(Exception):
    pass


class ZerigoNotFound(Exception):
    pass
    

class ZerigoDNS(object):
    ''' Base class to interact with ZerigoDNS API.
    '''
    vals = {}
    def __init__(self, user, key, data=None, is_secure=True, is_debug=False):
        self.api_host = 'ns.zerigo.com'
        self.api_path = '/api/1.1/'
        self.is_secure = is_secure
        self.is_debug = is_debug
        self.set_credentials(user, key)
        self.count = 0
        self.parser = Parser()
        self.errors = []
        self.xml_skip = []
        self.element = ''
        self.response_headers = {}
        
        if isinstance(data, dict):
            self.load(data)
    
    def _is_protected(self, name):
        protected = [
            'api_host', 'api_path', 'is_secure', 'parser', 'count',
            'vals', 'errors', 'xml_skip', 'user', 'key', 'element',
            'response_headers', 'is_debug',
        ]
        return (name in protected)
    
    def __setattr__(self, name, val):
        if self._is_protected(name):
            super(ZerigoDNS, self).__setattr__(name, val)
        else:
            name = name.replace('_', '-')
            self.vals[name] = val
    
    def __delattr__(self, name):
        if not self._is_protected(name):
            del self.vals[name]
    
    def __getattribute__(self, name):
        if name == 'vals':
            return super(ZerigoDNS, self).__getattribute__(name)
        else:
            try:
                _name = name.replace('_', '-')
                return self.vals[_name]
            except KeyError:
                return super(ZerigoDNS, self).__getattribute__(name)
    
    def load(self, data, reset=True):
        if reset:
            self.vals = {}  # Reset vals

        for k, v in data.iteritems():
            setattr(self, k, v)
    
    def set_credentials(self, user, key):
        ''' Set access credentials. '''
        self.user = user
        self.key = key
    
    def get_auth_header(self):
        base64str = base64.b64encode('%s:%s' % (self.user, self.key))
        return {
            'Authorization': 'Basic %s' % base64str,
            'Accept': 'application/xml',
        }
    
    def send_request(self, method='GET', id=None, path=None, 
                                request=None, headers={}, opts={}):
        ''' Construct and send request to Zerigo servers.
        '''
        self.errors = []
        if path is not None:
            # Path over-rides element & id
            call_path = urlparse.urljoin(self.api_path, path)
        else:
            if id is not None:
                call_path = urlparse.urljoin(
                    self.api_path,
                    '%s/%s.xml' % (self.element, str(id)),
                )
            else:
                call_path = urlparse.urljoin(
                    self.api_path,
                    '%s.xml' % self.element,
                )
            
        if opts:
            call_path += '?%s' % urlencode(opts)
        
        if self.is_secure:
            conn = httplib.HTTPSConnection(self.api_host)
        else:
            conn = httplib.HTTPConnection(self.api_host)

        req_headers = self.get_auth_header()
        req_headers.update(headers)
        if method in ('POST', 'PUT'):
            req_headers['Content-Type'] = 'application/xml'
            # XXX This is a hack. For some reason letting the Python 
            # HTTPConnection.request() method set the Content-Length 
            # header (default) was setting the length 2 bytes short.
            # Manually set the length for now until we can look into it
            #req_headers['Content-Length'] = (len(request) + 2)
        
        if self.is_debug:
            print 'DEBUG (method): ', method
            print 'DEBUG (path): ', call_path
            print 'DEBUG (headers): ', req_headers
            print 'DEBUG (request): ', request

        conn.request(method, call_path, request, req_headers)
        res = conn.getresponse()
        data = res.read()
        conn.close()
        
        # Handle header data
        self.response_headers.update(res.getheaders())
        self.count = int(res.getheader('X-Query-Count', 0))
        
        if self.is_debug:
            print 'DEBUG (response data): ', data
            print 'DEBUG (response headers): ', self.response_headers
            print 'DEBUG (response code): %i - %s' % (res.status, res.reason)

        if res.status >= 200 and res.status <= 299:
            return data

        if res.status == 422:
            self.errors = self.parse_errors(data)
            return None
        elif res.status == 404:
            raise ZerigoNotFound('Not found')
        else:
            raise ZerigoError('Error: [%i] %s' % (res.status, res.reason))
    
    def parse(self, data):
        return self.parser.parse(data)
    
    def parse_errors(self, data):
        return self.parser.parse_errors(data)
    
    def get_xml_data(self):
        ''' Clean out items that should be skipped.
        '''
        vals = self.vals.copy()
        for name in self.xml_skip:
            try:
                vals.pop(name)
            except KeyError:
                pass
        return vals
    
    def _to_xml(self, data):
        return self.parser.build_request_string(data)
    
    def to_xml(self):
        raise ZerigoError('Not Implemented')
    
    def get_public_ip(self):
        api_path = 'tools/public_ipv4.xml'
        ip_hash = self.parse(
            self.send_request(path=api_path)
        )
        return ip_hash.get('ipv4')
    
    def update_count(self, opts={}):
        if isinstance(self, NSHost):
            if not opts.has_key('zone_id'):
                try:
                    opts['zone_id'] = self.zone_id
                except AttributeError:
                    raise ZerigoError(
                        'Cannot update host count without valid zone id'
                    )

        api_path = '%s/count.xml' % self.element
        data = self.parse(self.send_request(path=api_path, opts=opts))
        self.count = int(data['count'])
        return self.count
    
    def get_blank(self):
        api_path = '%s/new.xml' % self.element
        return self.parse(self.send_request(path=api_path))
    
    def has_errors(self):
        return (len(self.errors) > 0)
    
    def get_errors(self):
        return self.errors
    
    def destroy(self):
        if not hasattr(self, 'id'):
            raise ZerigoError('Cannot destroy without a valid id')
        self.send_request(method='DELETE', id=self.id)
        return (not self.has_errors())
    
    def save(self):
        data = self.to_xml()
        if not hasattr(self, 'id'):
            # Create new instance
            result = self.send_request(method='POST', request=data)
            if not self.has_errors():
                self.load(
                    self.parse(result)[
                        self.element[:-1].replace('_', '-')
                    ]
                )
                loc = self.response_headers.get('Location', None)
                if loc is not None:
                    p = urlparse.urlparse(loc)
                    new_id = int(p.path.split('/')[-2])
                    self.id = new_id
                        
                if not hasattr(self, 'id'):
                    # Second check, sanity purposes
                    raise ZerigoError(
                        'Create was successful but unable to determine the id'
                    )
        else:
            # Update current instance
            result = self.send_request(
                method='PUT',
                id=self.id,
                request=data,
            )

        return (not self.has_errors())


class NSZone(ZerigoDNS):
    ''' Class to manage zone entries 
    '''
    def __init__(self, *args, **kwargs):
        super(NSZone, self).__init__(*args, **kwargs)
        self.xml_skip = (
            'id', 'customer-id', 'created-at', 'updated-at', 'hosts',
        )
        self.element = 'zones'
    
    def __setattr__(self, name, val):
        if name == 'hosts' and isinstance(val, (list, tuple)):
            # Add hosts as NSHost objects
            self.vals[name] = [
                NSHost(
                    self.user,
                    self.key,
                    data=zdata['host'],
                    is_secure=self.is_secure,
                    is_debug=self.is_debug,
                ) for zdata in val
            ]
        else:
            super(NSZone, self).__setattr__(name, val)
    
    def to_xml(self):
        return self._to_xml({'zone': self.get_xml_data()})
    
    def build_blank_zone(self):
        self.load(self.get_blank()['zone'])
    
    def create(self, data, load_blank=False):
        if data.has_key('zone'):
            data = data.get('zone')
        zone = NSZone(
            self.user,
            self.key,
            data=data,
            is_secure=self.is_secure,
            is_debug=self.is_debug,
        )
        if load_blank:
            zone.build_blank_zone()
            zone.load(data, reset=False)
        zone.save()
        return zone
    
    def create_host(self, data, load_blank=False):
        if not hasattr(self, 'id'):
            raise ZerigoError('Cannot add host without a valid zone id')
        
        if data.has_key('host'):
            data = data.get('host')
        host = NSHost(
            self.user,
            self.key,
            data=data,
            is_secure=self.is_secure,
            is_debug=self.is_debug,
        )
        return host.create(data, self.id, load_blank)
    
    def find_all(self, opts={}):
        return self.zones(opts=opts)
    
    def zones(self, opts={}):
        xml = self.send_request(opts=opts)
        data = self.parse(xml)
        return [
            NSZone(
                self.user,
                self.key,
                data=zdata['zone'],
                is_secure=self.is_secure,
                is_debug=self.is_debug,
            ) for zdata in data.get('zones', [])
        ]
    
    def reload(self):
        if not hasattr(self, 'id'):
            raise ZerigoError('Cannot retrieve zone without a valid id')
        xml = self.send_request(method='GET', id=self.id)
        data = self.parse(xml)
        self.load(data['zone'])
        return self
    
    def find(self, id):
        zone = NSZone(
            self.user,
            self.key,
            data={'id': id,},
            is_secure=self.is_secure,
            is_debug=self.is_debug
        )
        zone.reload()
        return zone
    
    def find_by_domain(self, domain):
        zone = NSZone(
            self.user,
            self.key,
            is_secure=self.is_secure,
            is_debug=self.is_debug
        )
        xml = zone.send_request(method='GET', id=domain)
        data = self.parse(xml)
        zone.load(data['zone'])
        return zone
    
    def find_by_hostname(self, hostname):
        host = NSHost(
            self.user,
            self.key,
            is_secure=self.is_secure,
            is_debug=self.is_debug,
        )
        fqdn = '%s.%s' % (hostname, self.domain)
        return host.find_by_hostname(fqdn, self)


class NSHost(ZerigoDNS):
    ''' Class to manage host entries 
    '''
    def __init__(self, *args, **kwargs):
        super(NSHost, self).__init__(*args, **kwargs)
        self.xml_skip = ('id', 'created-at', 'updated-at',)
        self.element = 'hosts'
    
    def _get_zone_id(self, zone_id):
        return zone_id.id if isinstance(zone_id, NSZone) else zone_id
    
    def to_xml(self):
        return self._to_xml({'host': self.get_xml_data()})
    
    def build_blank_host(self):
        self.load(self.get_blank()['host'])
    
    def create(self, data, zone_id=None, load_blank=False):
        if data.has_key('host'):
            data = data.get('host')
        if zone_id is not None:
            data['zone_id'] = self._get_zone_id(zone_id)
        host = NSHost(
            self.user,
            self.key,
            data=data,
            is_secure=self.is_secure,
            is_debug=self.is_debug,
        )
        if load_blank:
            host.build_blank_host()
            host.load(data, reset=False)
        host.save()
        return host
    
    def find_all(self, zone_id, opts={}):
        opts['zone_id'] = self._get_zone_id(zone_id)
        return self.hosts(opts=opts)

    def hosts(self, opts={}):
        if not opts.has_key('zone_id'):
            opts['zone_id'] = self.zone_id
        else:
            opts['zone_id'] = self._get_zone_id(opts['zone_id'])
        xml = self.send_request(method='GET', opts=opts)
        data = self.parse(xml)
        return [
            NSHost(
                self.user,
                self.key,
                data=zdata['host'],
                is_secure=self.is_secure,
                is_debug=self.is_debug,
            ) for zdata in data.get('hosts', [])
        ]
    
    def find(self, id, zone_id):
        zone_id = self._get_zone_id(zone_id)
        host = NSHost(
            self.user,
            self.key,
            data={'id': id, 'zone_id': zone_id,},
            is_secure=self.is_secure,
            is_debug=self.is_debug,
        )
        host.reload()
        return host
    
    def reload(self):
        if not hasattr(self, 'id'):
            raise ZerigoError('Cannot retrieve host without a valid id')
        xml = self.send_request(method='GET', id=self.id)
        data = self.parse(xml)
        self.load(data['host'])
        return self
    
    def find_by_hostname(self, hostname, zone_id):
        zone_id = self._get_zone_id(zone_id)
        host = NSHost(
            self.user,
            self.key,
            data={'zone_id': zone_id,},
            is_secure=self.is_secure,
            is_debug=self.is_debug
        )
        xml = host.send_request(method='GET', opts={'fqdn': hostname})
        data = self.parse(xml)
        return [
            NSHost(
                self.user,
                self.key,
                data=zdata['host'],
                is_secure=self.is_secure,
                is_debug=self.is_debug,
            ) for zdata in data.get('hosts', [])
        ]


class NSZoneTemplate(ZerigoDNS):
    ''' Class to manage zone templates 
    '''
    def __init__(self, *args, **kwargs):
        super(NSZoneTemplate, self).__init__(*args, **kwargs)
        self.xml_skip = ('id', 'created-at', 'updated-at', 'host-templates',)
        self.element = 'zone_templates'
    
    def __setattr__(self, name, val):
        if name == 'host-templates' and isinstance(val, (list, tuple)):
            # Add host-templates as NSHostTemplate objects
            self.vals[name] = [
                NSHostTemplate(
                    self.user,
                    self.key,
                    data=zdata['host-template'],
                    is_secure=self.is_secure,
                    is_debug=self.is_debug,
                ) for zdata in val
            ]
        else:
            super(NSZoneTemplate, self).__setattr__(name, val)
    
    def to_xml(self):
        return self._to_xml({'zone-template': self.get_xml_data()})

    def build_blank_template(self):
        self.load(self.get_blank()['zone-template'])
    
    def create(self, data, load_blank=False):
        if data.has_key('zone-template'):
            data = data.get('zone-template')
        template = NSZoneTemplate(
            self.user,
            self.key,
            data=data,
            is_secure=self.is_secure,
            is_debug=self.is_debug,
        )
        if load_blank:
            template.build_blank_template()
            template.load(data, reset=False)
        template.save()
        return template
    
    def create_host_template(self, data, load_blank=False):
        if not hasattr(self, 'id'):
            raise ZerigoError(
                'Cannot add host template without a valid zone template id'
            )

        if data.has_key('host-template'):
            data = data.get('host-template')
        host = NSHostTemplate(
            self.user,
            self.key,
            data=data,
            is_secure=self.is_secure,
            is_debug=self.is_debug,
        )
        return host.create(data, self.id, load_blank)
    
    def find_all(self, opts={}):
        return self.templates(opts=opts)

    def templates(self, opts={}):
        xml = self.send_request(opts=opts)
        data = self.parse(xml)
        return [
            NSZoneTemplate(
                self.user,
                self.key,
                data=zdata['zone-template'],
                is_secure=self.is_secure,
                is_debug=self.is_debug,
            ) for zdata in data.get('zone-templates', [])
        ]

    def reload(self):
        if not hasattr(self, 'id'):
            raise ZerigoError(
                'Cannot retrieve zone template without a valid id'
            )
        xml = self.send_request(method='GET', id=self.id)
        data = self.parse(xml)
        self.load(data['zone-template'])
        return self

    def find(self, id):
        zone = NSZoneTemplate(
            self.user,
            self.key,
            data={'id': id,},
            is_secure=self.is_secure,
            is_debug=self.is_debug
        )
        zone.reload()
        return zone


class NSHostTemplate(ZerigoDNS):
    ''' Class to manage host templates 
    '''
    def __init__(self, *args, **kwargs):
        super(NSHostTemplate, self).__init__(*args, **kwargs)
        self.xml_skip = ('id', 'created-at', 'updated-at',)
        self.element = 'host_templates'

    def _get_zone_template_id(self, zone_id):
        return zone_id.id if isinstance(zone_id, NSZoneTemplate) else zone_id

    def to_xml(self):
        return self._to_xml({'host-template': self.get_xml_data()})

    def build_blank_template(self):
        self.load(self.get_blank()['host-template'])
    
    def create(self, data, zone_id=None, load_blank=False):
        if data.has_key('host-template'):
            data = data.get('host-template')
        if zone_id is not None:
            data['zone_template_id'] = self._get_zone_template_id(zone_id)
        host = NSHostTemplate(
            self.user,
            self.key,
            data=data,
            is_secure=self.is_secure,
            is_debug=self.is_debug,
        )
        if load_blank:
            host.build_blank_host()
            host.load(data, reset=False)
        host.save()
        return host
    
    def find_all(self, zone_id, opts={}):
        opts['zone_template_id'] = self._get_zone_template_id(zone_id)
        return self.templates(opts=opts)

    def templates(self, opts={}):
        if not opts.has_key('zone_template_id'):
            opts['zone_template_id'] = self.zone_template_id
        else:
            opts['zone_template_id'] = \
                    self._get_zone_template_id(opts['zone_template_id'])
        xml = self.send_request(method='GET', opts=opts)
        data = self.parse(xml)
        return [
            NSHostTemplate(
                self.user,
                self.key,
                data=zdata['host-template'],
                is_secure=self.is_secure,
                is_debug=self.is_debug,
            ) for zdata in data.get('host-templates', [])
        ]

    def find(self, id, zone_id):
        zone_id = self._get_zone_template_id(zone_id)
        host = NSHostTemplate(
            self.user,
            self.key,
            data={'id': id, 'zone_template_id': zone_id,},
            is_secure=self.is_secure,
            is_debug=self.is_debug,
        )
        host.reload()
        return host

    def reload(self):
        if not hasattr(self, 'id'):
            raise ZerigoError('Cannot retrieve host without a valid id')
        xml = self.send_request(method='GET', id=self.id)
        data = self.parse(xml)
        self.load(data['host-template'])
        return self
