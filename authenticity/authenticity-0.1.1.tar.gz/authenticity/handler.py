# Copyright (C) 2011 Luci Stanescu <luci@cnix.ro>. See debian/copyright for details.
#

"""
HTTP request handler. This is where the main magic happens.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

__all__ = ['RequestHandler']

import errno
import mimetypes
import os
import sqlite3
import traceback
import urllib
import urlparse
from string import Template

from mod_python import apache
from openid.extensions.sreg import SRegRequest, SRegResponse
from openid.server.server import EncodingError, ProtocolError, Server
from openid.store.filestore import FileOpenIDStore
from openid.store.sqlstore import SQLiteStore

import authenticity
from authenticity.configuration import AuthenticityConfiguration
from authenticity.http import Request, Response, decode_uri
from authenticity.identity import AuthenticationError, IdentityLookupError, IdentityServiceError, LDAPIdentityService
from authenticity.logging import ApacheLogger
from authenticity.openid import OpenIDResponse
from authenticity.template import TemplateManager, TemplateResponse


class NegativeReplyError(Exception):
    """
    Base class for exceptions which result in negative HTTP errors.
    """

    status = None


class InternalServerError(NegativeReplyError):
    """
    This exception is raised by the request handlers when an internal error is
    encountered. The exception is caught by the RequestHandler and a status
    code 500 is returned (Internal Server Error) to the client.
    """

    status = apache.HTTP_INTERNAL_SERVER_ERROR


class InvalidRequestError(NegativeReplyError):
    """
    This exception is raised by the request handlers when there is something
    wrong with the request. The exception is caught by the RequestHandler and a
    status code 400 is returned (Bad Request) to the client.
    """

    status = apache.HTTP_BAD_REQUEST


class NotFoundError(NegativeReplyError):
    """
    This exception is raised by the request handlers when they want to signal
    that the resource does not exist. The exception is caught by the
    RequestHandler and a status 404 is returned (Not Found) to the client.
    """

    status = apache.HTTP_NOT_FOUND


class RequestContext(object):
    """
    An object containing information about the context in which a request is
    being processed.
    """
    def __init__(self, apache_request, configuration):
        self._apache_request = apache_request
        self.configuration = configuration
        self.logger = None
        self.openid_server = None
        self.template_manager = None

    @property
    def authenticity_homepage(self):
        """
        The homepage of the Authenticity OpenID Server.
        """
        return authenticity.__homepage__

    @property
    def authenticity_version(self):
        """
        The version of the Authenticity OpenID Server.
        """
        return authenticity.__version__

    @property
    def page_title(self):
        """
        The title that should be displayed on the pages.
        """
        return self.configuration.general.page_title.safe_substitute(realm_name=self.realm_name)

    @property
    def realm_name(self):
        """
        The name that should be displayed on the pages as the realm the users
        login to.
        """
        return self.configuration.general.realm_name.safe_substitute(server_host=self._apache_request.hostname,
                                                                     server_name=self._apache_request.server.server_hostname)

    @property
    def server_admin(self):
        """
        The e-mail address of the administrator as defined in the apache
        configuration.
        """
        return self._apache_request.server.server_admin

    @property
    def server_base(self):
        """
        The base URL where the server receives requests.
        """
        return decode_uri(self._apache_request.construct_url(self.server_path.encode('utf-8')))

    @property
    def server_path(self):
        """
        The base path where the server receives requests.
        """
        return self.configuration.general.server_path.rstrip('/')

    def data_path(self, path):
        """
        Returns an absolute path from the argument relative to the data path.
        """
        return os.path.join(self.configuration.general.data_path, path)

    def construct_url(self, path, path_only=True):
        """
        Returns a URL for the resource identified by path. An absolute path (one
        which starts with /) is taken relative to the server path, while a
        relative path is taken relative to the parent directory of the resource
        in the current request.
        """
        if path.startswith('/'):
            full_path = '/'.join([self.server_path, path.lstrip('/')])
        else:
            full_path = '/'.join([self._apache_request.uri.rpartition(b'/')[0].decode('utf-8'), path])
        if path_only:
            return full_path
        else:
            return decode_uri(self._apache_request.construct_url(full_path.encode('utf-8')))

    def login_url(self, path_only=True):
        """
        The URL where the login request should be POSTed.
        """
        return self.construct_url('/login', path_only=path_only)

    def openid_server_url(self, path_only=True):
        """
        The URL where the server handles OpenID requests.
        """
        return self.construct_url('/server', path_only=path_only)

    def server_xrds_url(self, path_only=True):
        """
        The URL where the server's XRDS document is served.
        """
        return self.construct_url('/serverxrds', path_only=path_only)

    def user_id_url(self, username, path_only=True):
        """
        The URL where the information about a user is served.
        """
        return self.construct_url('/id/%s' % urllib.quote(username.encode('utf-8'), b'').decode('utf-8'), path_only=path_only)

    def user_xrds_url(self, username, path_only=True):
        """
        The URL where the XRDS document for a user is served.
        """
        return self.construct_url('/idxrds/%s' % urllib.quote(username.encode('utf-8'), b'').decode('utf-8'), path_only=path_only)


class RequestHandler(object):
    """
    Main object for processing requests.
    """

    def handle_request(self, apache_request):
        """
        Initializes the request processing and dispatches the request to an
        appropriate handler.
        """
        # initial request validation
        if apache_request.method not in (b'GET', b'POST'):
            apache_request.allow_methods([b'GET', b'POST'], reset=True)
            apache_request.status = apache_reques.HTTP_METHOD_NOT_ALLOWED
            return apache.OK

        # initialize logging
        logger = ApacheLogger(apache_request)

        # read configuration
        try:
            config_file = open('/etc/authenticity/config.ini')
        except (IOError, OSError), e:
            if e.errno != errno.ENOENT:
                logger.warn('Failed to open configuration file /etc/authentcity/config.ini: %s.' % os.strerror(e.errno))
            config_file = None
        config = AuthenticityConfiguration.read(config_file, apache_request.get_options(), logger)

        # initialize context and request information
        context = RequestContext(apache_request, config)
        context.logger = logger
        context.template_manager = TemplateManager(config, logger)
        if config.identity.backend == 'ldap':
            context.identity_service = LDAPIdentityService(config, logger)
        else:
            raise RuntimeError('Unexpected identity backend: %s' % config.general.backend)
        request = Request.from_apache_request(apache_request, context.server_path)

        context.logger.debug('Received %s request for %s:', request.method, request.uri)
        for key, values in request.query.iteritems():
            for value in values:
                context.logger.debug('    %s = %s', key, value)
        try:
            # initialize server
            if context.configuration.general.openid_store.scheme == 'file':
                store = FileOpenIDStore(context.configuration.general.openid_store.path)
            elif context.configuration.general.openid_store.scheme == 'sqlite':
                conn = sqlite3.connect(context.configuration.general.openid_store.path)
                store = SQLiteStore(conn)
                cursor = conn.cursor()
                try:
                    cursor.execute("""SELECT name FROM sqlite_master WHERE type='table'""")
                    if not cursor.fetchall():
                        store.createTables()
                finally:
                    cursor.close()
            else:
                raise RuntimeError('Unexpected store type: %s' % context.configuration.general.openid_store.scheme)
            context.openid_server = Server(store, context.construct_url('/server', path_only=False))

            # dispatch the request
            template_public_directories = ['/%s/' % d for d in context.template_manager.configuration.general.public_directories or []]
            if request.uri in ('', '/'):
                context.logger.debug('Processed request for main server page.')
                head_elements = """<meta http-equiv="X-XRDS-Location" content="%(server_xrds_url)s"/>""" % \
                                dict(server_xrds_url=context.server_xrds_url(path_only=False))
                response = TemplateResponse('about.xml',
                                            apache.HTTP_OK,
                                            request,
                                            context,
                                            headers={'X-XRDS-Location': context.server_xrds_url(path_only=False)},
                                            head_elements=head_elements)
            elif request.uri.startswith('/id/'):
                response = self.identity_handler(request, context)
            elif request.uri.startswith('/idxrds/'):
                response = self.identity_xrds_handler(request, context)
            elif request.uri == '/login':
                response = self.login_handler(request, context)
            elif request.uri == '/server':
                response = self.server_handler(request, context)
            elif request.uri == '/serverxrds':
                response = self.serverxrds_handler(request, context)
            elif any(request.uri.startswith(dir) for dir in template_public_directories):
                filename = os.path.join(context.template_manager.directory, request.uri.lstrip('/'))
                try:
                    file = open(filename)
                except (IOError, OSError):
                    raise NotFoundError
                else:
                    context.logger.debug('Processed request for template file: %s.', request.uri.lstrip('/'))
                    content_type = mimetypes.guess_type(filename)[0] or 'text/plain'
                    response = Response(apache.HTTP_OK, content_type=content_type, body=file.read())
            else:
                raise NotFoundError
        except InternalServerError, e:
            error = unicode(e) or 'An internal server error has occurred.'
            context.logger.debug('Failed to process request for %s due to an internal error.', request.uri)
            response = TemplateResponse('error.xml', e.status, request, context, data=dict(error=error))
        except (EncodingError, InvalidRequestError), e:
            error = unicode(e) or ('Received invalid request for %s.' % request.uri)
            context.logger.debug('Replying with %d status due to invalid request for %s.', apache.HTTP_BAD_REQUEST, request.uri)
            response = TemplateResponse('error.xml', e.status, request, context, data=dict(error=error))
        except NotFoundError, e:
            error = unicode(e) or ('The resource %s was not found on this server.' % request.uri)
            context.logger.debug('Received request for unknown resource: %s', error)
            response = TemplateResponse('error.xml', e.status, request, context, data=dict(error=error))
        except Exception, e:
            context.logger.debug('Failed to process request for %s due to an internal error.', request.uri)
            response = TemplateResponse('error.xml',
                                        apache.HTTP_INTERNAL_SERVER_ERROR,
                                        request,
                                        context,
                                        data=dict(error='An internal server error has occurred.'))
            for line in traceback.format_exc().splitlines():
                context.logger.error(line)

        context.logger.debug('Sending %d HTTP response.', response.status)
        if isinstance(response, OpenIDResponse):
            context.logger.debug('Replying with OpenID response:')
            for key, value in response.openid_response.fields.toPostArgs().iteritems():
                context.logger.debug('  %s = %s', key, value.decode('utf-8'))
        elif isinstance(response, TemplateResponse):
            context.logger.debug('Replying with template generated response of type %s (%d bytes).',
                                 response.content_type,
                                 response.content_length)
        else:
            context.logger.debug('Replying with %s request of %d bytes.', response.content_type, response.content_length)
        response.to_apache_response(apache_request)

        return apache.OK

    def identity_handler(self, request, context):
        """
        Handler for the /id/$username requests.
        """
        username = urllib.unquote(request.uri[len('/id/'):])
        if not username:
            raise NotFoundError
        try:
            identity = context.identity_service.lookup(username)
        except IdentityLookupError:
            raise NotFoundError('An identity associated with the username %s was not found.' % username)
        except IdentityServiceError, e:
            context.logger.error('Identity lookup failed: %s.', e)
            raise InternalServerError
        else:
            context.logger.debug('Processed request for identity page of %s.', username)
            head_elements = """<meta http-equiv="X-XRDS-Location" content="%(user_xrds_url)s"/>
                               <link rel="openid.server" href="%(server_url)s"/>
                               <link rel="openid2.provider" href="%(server_url)s"/>""" % \
                            dict(server_url=context.openid_server_url(path_only=False),
                                 user_xrds_url=context.user_xrds_url(username, path_only=False))
            if context.configuration.identity.forced_local_id:
                forced_local_id = context.configuration.identity.forced_local_id.safe_substitute(server_base=context.server_base,
                                                                                                 username=username)
                head_elements += """<link rel="openid.delegate" href="%(local_id)s"/>
                                    <link rel="openid2.local_id" href="%(local_id)s"/>""" % \
                                 dict(local_id=forced_local_id)
            return TemplateResponse('identity.xml',
                                    apache.HTTP_OK,
                                    request,
                                    context,
                                    headers={'X-XRDS-Location': context.user_xrds_url(username, path_only=False)},
                                    head_elements=head_elements,
                                    data=dict(identity=identity))

    def identity_xrds_handler(self, request, context):
        """
        Handler for /idxrds/$username requests.
        """
        username = urllib.unquote(request.uri[len('/idxrds/'):])
        try:
            identity = context.identity_service.lookup(username)
        except IdentityLookupError:
            raise NotFoundError('An identity associated with the username %s was not found.' % username)
        except IdentityServiceError, e:
            context.logger.error('Identity lookup failed: %s', e)
            raise InternalServerError
        else:
            context.logger.debug('Processed request for identity XRDS document of %s.', username)
            if context.configuration.identity.forced_local_id:
                forced_local_id = context.configuration.identity.forced_local_id.safe_substitute(server_base=context.server_base,
                                                                                                 username=username)
            else:
                forced_local_id = None
            return TemplateResponse(context.data_path('xrds/identity.xml'),
                                    apache.HTTP_OK,
                                    request,
                                    context,
                                    data=dict(identity=identity, forced_local_id=forced_local_id))

    def login_handler(self, request, context):
        """
        Handler for the /login requests.
        """
        try:
            action = request.query['action'][0]
            openid_args = dict(urlparse.parse_qsl(request.query['original_request'][0].encode('utf-8'), True))
            openid_request = context.openid_server.decodeRequest(openid_args)
            username = request.query['username'][0]
            password = request.query['password'][0]
            send_sreg_data = 'send_sreg_data' in request.query
            if openid_request.idSelect():
                identifier = Template(request.query['identifier'][0]).safe_substitute(username=username)
            else:
                identifier = openid_request.identity.decode('utf-8')
        except (IndexError, KeyError):
            raise InvalidRequestError('The request does not contain expected data.')
        if action == 'cancel':
            context.logger.debug('Sending negative OpenID response due to cancel action.')
            return OpenIDResponse(context.openid_server, openid_request.answer(False))
        elif action != 'login':
            raise InvalidRequestError('The request action %s is invalid.' % action)
        valid_identifiers = (f.safe_substitute(server_base=context.server_base, username=username) \
                             for f in context.configuration.identity.identifier_formats)
        if identifier not in valid_identifiers:
            context.logger.info('Attempt to use invalid identifier %s by %s.', identifier, username)
            return self._login_response(request,
                                        context,
                                        openid_request,
                                        username=username,
                                        send_sreg_data=send_sreg_data,
                                        error='The identifier %s is invalid.' % identifier)
        try:
            identity = context.identity_service.authenticate(username, password)
        except AuthenticationError:
            context.logger.info('Failed authentication from %s.', username)
            return self._login_response(request,
                                        context,
                                        openid_request,
                                        username=username,
                                        send_sreg_data=send_sreg_data,
                                        error='Your credentials are incorrect.')
        except IdentityServiceError, e:
            context.logger.error('Authentication failed: %s.' % e)
            raise InternalServerError
        else:
            context.logger.info('Successful authentication to use identifier %s by %s for %s.',
                                identifier, username, openid_request.trust_root)
            openid_response = openid_request.answer(True, identity=identifier)
            sreg_request = SRegRequest.fromOpenIDRequest(openid_request)
            sreg_data = dict(nickname   = identity.nickname,
                             email      = identity.email,
                             fullname   = identity.fullname,
                             dob        = identity.birthday.strftime('%Y-%m-%d') if identity.birthday else None,
                             gender     = identity.gender,
                             postcode   = identity.postcode,
                             country    = identity.country,
                             language   = identity.language,
                             timezone   = identity.timezone)
            if send_sreg_data:
                sreg_data = dict((key, value.encode('utf-8')) for key, value in sreg_data.iteritems() if value)
            else:
                sreg_data = dict()
            sreg_response = SRegResponse.extractResponse(sreg_request, sreg_data)
            openid_response.addExtension(sreg_response)
            return OpenIDResponse(context.openid_server, openid_response)

    def server_handler(self, request, context):
        """
        Handler for the /server requests.
        """
        try:
            openid_args = dict((key.encode('utf-8'), values[0].encode('utf-8')) for key, values in request.query.iteritems())
            openid_request = context.openid_server.decodeRequest(openid_args)
            if openid_request is not None:
                context.logger.debug('Received OpenID request at server location:')
                for key, value in openid_request.message.toPostArgs().iteritems():
                    context.logger.debug('  %s = %s', key, value.decode('utf-8'))
            if openid_request is None:
                context.logger.debug('Processed empty request at OpenID server location.')
                head_elements = """<meta http-equiv="X-XRDS-Location" content="%(server_xrds_url)s"/>""" % \
                                dict(server_xrds_url=context.server_xrds_url(path_only=False))
                return TemplateResponse('about.xml',
                                        apache.HTTP_OK,
                                        request,
                                        context,
                                        headers={'X-XRDS-Location': context.server_xrds_url(path_only=False)},
                                        head_elements=head_elements)
            elif openid_request.mode == b'checkid_immediate':
                context.logger.debug('Sending negative OpenID response to checkid_immediate request.')
                return OpenIDResponse(context.openid_server, openid_request.answer(False))
            elif openid_request.mode == b'checkid_setup':
                context.logger.debug('Challenging user as a result of checkid_setup request.')
                return self._login_response(request, context, openid_request)
            else:
                context.logger.debug('Handling OpenID request automatically.')
                return OpenIDResponse(context.openid_server, context.openid_server.handleRequest(openid_request))
        except ProtocolError, e:
            context.logger.error('Replying with negative response due to protocol error: %s.', e)
            return OpenIDResponse(context.openid_server, e)

    def serverxrds_handler(self, request, context):
        """
        Handler for the /serverxrds requests.
        """
        context.logger.debug('Sending server XRDS document.')
        return TemplateResponse(context.data_path('xrds/server.xml'), apache.HTTP_OK, request, context)

    def _login_response(self, request, context, openid_request, username=None, send_sreg_data=True, error=None):
        sreg_request = SRegRequest.fromOpenIDRequest(openid_request)
        identifier = openid_request.identity.decode('utf-8')
        claimed_identifier = openid_request.claimed_id.decode('utf-8') if openid_request.claimed_id else identifier
        identifier_formats = [f.safe_substitute(server_base=context.server_base) \
                              for f in context.configuration.identity.identifier_formats]
        data = dict(error               = error,
                    claimed_identifier  = claimed_identifier,
                    id_select           = openid_request.idSelect(),
                    identifier          = identifier,
                    identifier_formats  = identifier_formats,
                    original_request    = openid_request.message.toURLEncoded().decode('utf-8'),
                    sreg_requested      = sreg_request.wereFieldsRequested(),
                    policy_url          = sreg_request.policy_url,
                    send_sreg_data      = send_sreg_data,
                    trust_root          = decode_uri(openid_request.trust_root),
                    username            = username or '')
        return TemplateResponse('login.xml', apache.HTTP_OK, request, context, data=data)


