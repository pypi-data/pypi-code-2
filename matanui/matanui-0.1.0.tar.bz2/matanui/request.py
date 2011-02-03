# -*- coding: utf-8 -*-
'''Provides a structure for container objects of a request.'''

## Created: 2010-12-22 Guy K. Kloss <Guy.Kloss@aut.ac.nz>
##
## Copyright 2010 Guy K. Kloss
## Some rights reserved.
##
## http://www.aut.ac.nz/

__author__ = 'Guy K. Kloss <Guy.Kloss@aut.ac.nz>'

import urllib
import json
from matanui import API_VERSION
from matanui.exceptions import MataNuiServiceException

CONTENT = 'content'
INFO = 'info'
METADATA = 'metadata'
LIST = 'list'


class Request(object):
    '''
    Provides a parser structure for processing the server request.
    '''
    SWITCH_INDICATOR = '$'
    OBJECT_ID_SWITCH = 'id_'
    SWITCHES = [OBJECT_ID_SWITCH]
    ACCEPT_HEADER_BASE = 'application/x.matanui.'
    DEFAULT_ACCEPT_HEADER = ACCEPT_HEADER_BASE + 'content-v' + API_VERSION
    
    def __init__(self, environment):
        '''
        Constructor.
        
        @param environment: The WSGI environment.
        @type environment: C{dict}
        '''
        self.environment = environment 
        
        self.path = None
        """(File) path of resource (C{str})."""
        
        self.object_id = None
        """Object ID of resource (C{str})."""
        
        self.content_request = CONTENT
        """
        Indicates the type of content for the request (default for content).
        Can be one of (C{self.CONTENT}, C{self.METADATA}, C{self.INFO}).
        """
        
        self.query = None 
        """Query suitable for storage backend (C{dict})."""
        
        self.content_type = None
        """Content type requested (C{str})."""
        
        self.encoding = None
        """Encoding requested (C{str}). C{None} for all content and info, "json"
        for meta-data."""
        
        self.version = None
        """API version requested (C{str})."""
        
        self.username = None
        """User name of the requestor/X.509 certificate DN (C{str)"""
        
        # Now _parse the request from the environment.
        if self.environment:
            # This is for testability. Empty env -> no parsing.
            self._parse()

        
    def _parse(self):
        """
        Parses the request, extracts vital information for the service.
        """
        # For ease of implementation and testing, broken up into parts.
        self._parse_accept_headers()
        self._parse_query_parameters()
        self._parse_path()
        self.username = self.environment.get('SSL_CLIENT_I_DN', None)


    def _split_accept_header(self):
        """
        Splits the fields in the accept header, and returns a list of accepted
        types sorted by the given C{q} values.
        
        @return: Accepted types.
        @rtype: C{list}
        """
        accept_header = self.environment.get('HTTP_ACCEPT', '*/*')
        if not accept_header:
            accept_header = '*/*'
        
        parts = [x.strip().split(';') for x in accept_header.split(',')]
        for part in parts:
            # We're only doing a half-arsed evaluation/parsing here, but
            # should be OK for our purpose.
            if len(part) == 1:
                part.append(1.0)
            elif len(part) == 2:
                part[1] = float(part[1][2:])
            else:
                status = (400, '"Funky" declaration in accept header: %s'
                          % accept_header)
                raise MataNuiServiceException("Can't parse accept header: %s"
                                              % status, status)
        parts.sort(reverse=True, key=lambda x: x[1])
        
        return [item[0] for item in parts]
    
    
    def _parse_accept_type(self, accept_type):
        """
        Parse the "Accept" header type, which defines what the client accepts,
        and therefore determines what we need to deliver here.
        
        @param accept_type: The type to parse for acceptability.
        @type accept_type: C{str}
        
        @return: Parse result (kind, encoding, API) and status (code, message).
        @rtype: C{tupel}
        """
        status = (200, '')
        
        if accept_type == '*/*':
            accept_type = self.DEFAULT_ACCEPT_HEADER;
        
        if not accept_type.startswith(self.ACCEPT_HEADER_BASE):
            status = (406, 'Unsupported type in accept header: %s'
                      % accept_type)
            
        accept_type = accept_type[len(self.ACCEPT_HEADER_BASE):]
        
        # Encoding specification is appended after a '+'.
        parts = accept_type.split('+')
        accept_encoding = None
        if len(parts) == 2:
            accept_encoding = parts[1]
        elif len(parts) > 2:
            status = (406, 'Ambiguous specification for encoding: "%s"'
                      % '+'.join(parts[1:]))
        if accept_encoding is not None and accept_encoding.lower() != 'json':
            status = (406, 'Encoding "%s" not supported.' % accept_encoding)
        
        # Optional version is specified after a '-' in the first part.
        parts = parts[0].split('-')
        api_version = 'v' + API_VERSION
        if len(parts) == 2:
            api_version = parts[1]
        elif len(parts) > 2:
            status = (406, 'Ambiguous specification of version: "%s"'
                      % '-'.join(parts[1:]))
        if api_version == 'v' + API_VERSION:
            # Only take part of the version after the 'v'.
            api_version = api_version[1:]
        else:
            status = (406, 'API version "%s" not supported' % api_version)
        
        # The rest (first part) is the content request specification.
        content_switch = parts[0]
        content_request = None
        
        # What kind of content is requested?
        if content_switch == INFO:
            content_request = content_switch
        elif content_switch in ['metadata', 'list']:
            content_request = content_switch
            if accept_encoding is None or accept_encoding.lower() != 'json':
                message = ('Encoding "%s" not supported for meta-data or listing.'
                           % accept_encoding)
                status = (406, message)
        elif content_switch == CONTENT:
            content_request = content_switch
        else:
            status = (406, 'Content request "%s" not supported'
                      % content_switch)
        
        return ((content_request, accept_encoding, api_version), status)


    def _parse_accept_headers(self):
        """
        Determine all the accept types (in order of desirability), and try them
        one by one until we find one that suits our purpose.
        """
        accept_types = self._split_accept_header()
        status = None
        while status != (200, ''):
            if accept_types:
                accept_type = accept_types.pop(0)
            else:
                status = (406, 'No suitable accept header type found.')
            (parse_result, status) = self._parse_accept_type(accept_type)
        
        # Haven't found a suitable accept type?
        if status[0] != 200:
            raise MataNuiServiceException('HTTP error (for last accept header type) %s: %s'
                                          % status, status)
        
        # We're disregarding accept_encoding and api_version for now.
        (content_request, accept_encoding, api_version) = parse_result
        self.content_request = content_request
        self.encoding = accept_encoding
        self.version = api_version
        

    def _parse_query_parameters(self):
        """Parses all query parameters (in the URI after the '?')."""
        query_string = self.environment['QUERY_STRING']
        
        # Break up the query into a key-value dictionary.
        if query_string:
            self.query = dict(x.split('=') for x in query_string.split('&'))
        else:
            return
        try:
            for key, value in self.query.items():
                value_string = urllib.unquote_plus(value)
                self.query[key] = json.loads(value_string)
        except ValueError:
            message = 'Error parsing query'
            status = (400, message)
            raise MataNuiServiceException('Incorrect URL encoded JSON data structure', status)


    def _parse_path(self):
        """Parses the URI's path."""
        http_path = self.environment['PATH_INFO']
        
        # Object IDs are prepended by a switch indicator and 'id_'.
        if self.SWITCH_INDICATOR in http_path:
            switch_indicator_index = http_path.index(self.SWITCH_INDICATOR)
            switches = http_path[switch_indicator_index + 1:]
            http_path = http_path[:switch_indicator_index]
            indicators = switches.split(self.SWITCH_INDICATOR)
            i = 0
            object_ids = []
            while i < len(indicators):
                if indicators[i].startswith(self.OBJECT_ID_SWITCH):
                    object_ids.append(indicators.pop(i)[3:])
            
            # Process object ID.
            if len(object_ids) > 1:
                status = (400, 'Only one object ID allowed.')
                raise MataNuiServiceException('HTTP error %s: %s' % status,
                                              status)
            elif len(object_ids) == 1:
                self.object_id = object_ids[0]
            
            # Reject other switches.
            if indicators:
                status = (400, 'Unknown switches: %s'
                                        % str(indicators))
                raise MataNuiServiceException('HTTP error %s: %s' % status,
                                              status)
        
        # Finally, set the resource path.
        self.path = http_path
    

    def __repr__(self):
        res = []
        for attribute, value in self.__dict__.items():
            if not attribute.startswith('_'):
                res.append('%s=%s' % (attribute, value.__repr__()))
        return '%s(%s)' % (self.__class__.__name__, ', '.join(res))
