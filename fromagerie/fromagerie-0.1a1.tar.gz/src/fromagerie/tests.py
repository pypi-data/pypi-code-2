import unittest
import os
import urllib
import base64
try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO
try:
    from hashlib import md5 as md5constructor
except ImportError:
    from md5 import new as md5constructor
from urlparse import urlparse

from django.test import TestCase
from django.core import mail
from django.utils.http import urlencode
from django.http import SimpleCookie
from django.core.handlers.wsgi import WSGIRequest
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.core.files.uploadhandler import MemoryFileUploadHandler


from fromagerie.parser import DistutilsMultiPartParser
from fromagerie.views import SimplePackageIndex
from fromagerie.models import Classifier, Release


class FakePayload(object):
    """
    Fake a raw request file-object.
    """
    def __init__(self, content=None):
        if content is not None:
            pos = content.tell()
            content.seek(0, 2)
            self._len = content.tell()
            content.seek(pos)
        else:
            content = StringIO('')
            self._len = 0
        self._content = content

    def read(self, num_bytes=None):
        if num_bytes is None:
            num_bytes = self.__len or 1
        assert self._len >= num_bytes, "Cannot read more than the available bytes from the HTTP incoming data."
        content = self._content.read(num_bytes)
        self._len -= num_bytes
        return content


class DistutilsRequestFactory(object):
    """
    Builds Django request objects with a distutils flavor.
    """
    boundary = '--------------GHSKFJDLGDS7543FJKLFHRE75642756743254'

    def __init__(self, **defaults):
        self.cookies = SimpleCookie()
        self.defaults = defaults

    def request(self, request_body=None, headers=None):
        """
        Build a request object.
        """
        environ = {
            'HTTP_COOKIE':       SimpleCookie(),
            'PATH_INFO':         '/',
            'QUERY_STRING':      '',
            'REMOTE_ADDR':       '127.0.0.1',
            'REQUEST_METHOD':    'GET',
            'SCRIPT_NAME':       '',
            'SERVER_NAME':       'testserver',
            'SERVER_PORT':       '80',
            'SERVER_PROTOCOL':   'HTTP/1.1',
            'wsgi.version':      (1,0),
            'wsgi.url_scheme':   'http',
            'wsgi.errors':       StringIO(),
            'wsgi.multiprocess': True,
            'wsgi.multithread':  False,
            'wsgi.run_once':     False,
            }

        if headers is not None:
            environ.update(headers)

        environ['wsgi.input'] = FakePayload(request_body)

        return WSGIRequest(environ)

    def get(self, data=None, headers=None):
        """
        Build a GET request.
        """
        h = {
            'CONTENT_TYPE':    'text/html; charset=utf-8',
            'PATH_INFO':       '/',
            'QUERY_STRING':    urlencode(data, doseq=True),
            'REQUEST_METHOD': 'GET',
        }
        if headers is not None:
            h.update(headers)
        return self.request(headers=h)

    def post(self, data=None, headers=None):
        """
        Build a POST request.
        """
        post_data = self.encode_multipart(data)
        content_type = 'multipart/form-data; boundary=%s; charset=utf-8' % self.boundary
        pos = post_data.tell()
        post_data.seek(0, 2)
        content_length = post_data.tell()
        post_data.seek(pos)
        h = {
            'CONTENT_TYPE': content_type,
            'CONTENT_LENGTH': content_length,
            'PATH_INFO': '/',
            'REQUEST_METHOD': 'POST',
        }
        if headers is not None:
            h.update(headers)
        return self.request(post_data, h)

    def encode_multipart(self, data):
        """
        Build a POST request body in the style of distutils.
        """
        boundary = self.boundary
        sep_boundary = '\n--' + boundary
        end_boundary = sep_boundary + '--'
        body = StringIO()
        for key, value in data.items():
            if type(value) is not type([]):
                value = [value]
            for value in value:
                if type(value) is tuple and len(value) == 2:
                    fn = ';filename="%s"' % value[0]
                    value = value[1]
                else:
                    fn = ''
                    value = unicode(value).encode("utf-8")
                body.write(sep_boundary)
                body.write('\nContent-Disposition: form-data; name="%s"'%key)
                body.write(fn)
                body.write("\n\n")
                body.write(value)
                if value and value[-1] == '\r':
                    body.write('\n')  # write an extra newline (lurve Macs)
        body.write(end_boundary)
        body.write("\n")
        body.seek(0)
        return body




class ParserTestCase(unittest.TestCase):
    """
    Test the multipartparser.
    """
    def setUp(self):
        self.request_factory = DistutilsRequestFactory()

    def testBasicPost(self):
        """
        Ensure the parser can handle a basic distutils multipart/form-data
        encoded request.
        """
        data = {
            'name': 'test-app',
            'version': '0.1',
            'author': 'John Doe',
            'author_email': 'john.doe@example.com',
            'classifiers': ['Development Status :: 3 - Alpha',
                            'Intended Audience :: Developers'],
        }
        request = self.request_factory.post(data)
        # Django 1.0 chokes without an actual upload handler in the list,
        # so we give it one even though we've got no uploads to handle
        parser = DistutilsMultiPartParser(request.META,
                                          StringIO(request.raw_post_data),
                                          [MemoryFileUploadHandler()]) 
        parsed_data, files = parser.parse()
        self.assertTrue('name' in parsed_data and 'version' in parsed_data\
                        and 'author' in parsed_data and 'author_email' in parsed_data,
                        'Failed to parse request')
        for key in ('name', 'version', 'author', 'author_email'):
            self.assertEquals(parsed_data[key], data[key],
                              'Failed to correctly parse request')
        self.assertEquals(parsed_data.getlist('classifiers'), data['classifiers'],
                         'Failed to correctly parse request')


    def testBasicFilePost(self):
        """
        Ensure the parser can handle a distutils multipart/form-data encoded
        request with a file.
        """
        data = {
            'name': 'another-test-app',
            'version': '0.2',
            'author': 'Jane Doe',
            'author_email': 'jane.doe@example.com',
            'classifiers': ['Development Status :: 3 - Alpha',
                            'Intended Audience :: Developers'],
        }
        filename = 'views.py'
        fh = open(os.path.join(os.path.dirname(__file__), filename))
        data['content'] = (filename, fh.read())
        fh.seek(0)
        request = self.request_factory.post(data)
        parser = DistutilsMultiPartParser(request.META,
                                          StringIO(request.raw_post_data),
                                          [MemoryFileUploadHandler()])
        parsed_data, files = parser.parse()
        self.assertTrue('name' in parsed_data and 'version' in parsed_data\
                        and 'author' in parsed_data and 'author_email' in parsed_data,
                        'Failed to parse request')

        for key in ('name', 'version', 'author', 'author_email'):
            self.assertEquals(parsed_data[key], data[key],
                              'Failed to correctly parse request')
        self.assertEquals(parsed_data.getlist('classifiers'), data['classifiers'],
                         'Failed to correctly parse request')
        self.assertEquals(files['content'].read(), fh.read(),
                          'Failed to correctly parse file upload')
        self.assertTrue(isinstance(files['content'], InMemoryUploadedFile),
                        'Parser failed to use upload handlers')
        

class PackageIndexTestCase(TestCase):
    """
    Test the distutils interface.
    """
    fixtures = ['test_data.json']

    def setUp(self):
        self.request_factory = DistutilsRequestFactory()
        self.package_index = SimplePackageIndex()

    def buildAuthHeader(self, username, password):
        auth_credentials = username + ':' + password
        return 'Basic ' + base64.b64encode(auth_credentials)

    def testAuth(self):
        """
        Ensure the HTTP basic authentication backend challenges an
        unauthenticated submit request.
        """
        request = self.request_factory.post({':action': 'submit'})
        response = self.package_index(request)
        self.assertEquals(response.status_code, 401, 'Authentication not checked')
        self.assertEquals(response['WWW-Authenticate'], 'Basic realm="pypi"',
                          'Authentication challenge not sent')

    def testPasswordReset(self):
        """
        Ensure the index sends an error for non-existent user requests, and
        sends an email for existing users.
        """
        data = {
            ':action': 'password_reset',
            'email': 'nonexistent@example.com',
        }
        request = self.request_factory.post(data)
        response = self.package_index(request)
        self.assertEquals(response.status_code, 400, 'Password reset for non-existent user')
        data['email'] = 'test@example.com'
        request = self.request_factory.post(data)
        response = self.package_index(request)
        self.assertEquals(response.status_code, 200, '')
        self.assertEquals(len(mail.outbox), 1, 'Password reset email not sent')

    def testUserRegistration(self):
        """
        If we don't have registration, make sure we send a Not Implemented
        response.
        If password confirmation does not match password, make sure we send a 400.
        If the account is already registered, make sure we send a 400.
        If registration is installed, make sure the account activation email is
        sent.
        """
        try:
            import registration
            has_registration = True
        except ImportError:
            has_registration = False

        data = {
            ':action': 'user',
            'email': 'new_user@example.com',
            'password': 'password',
            'confirm': 'passwords',
            'name': 'new_user',
        }

        request = self.request_factory.post(data)
        response = self.package_index(request)
        if has_registration:
            self.assertEquals(response.status_code, 400,
                              'Index did not return Bad Request response for bad registration data')
            data['confirm'] = data['password']
            data['email'] = 'test@example.com'
            request = self.request_factory.post(data)
            response = self.package_index(request)
            self.assertEquals(response.status_code, 400,
                              'Index did not return Bad Request response for already registered email')
            data['email'] = 'new_user@example.com'
            request = self.request_factory.post(data)
            response = self.package_index(request)
            self.assertEquals(response.status_code, 200,
                              'Index did not return OK response for valid registration')
            self.assertEquals(len(mail.outbox), 1, 'Registration activation email not sent')
        else:
            self.assertEquals(response.status_code, 501,
                              'Index did not return a Not Implemented response')

    def testListClassifiers(self):
        """
        Make sure we send a plain text list of known classifiers.
        """
        classifiers = Classifier.objects.values_list('name', flat=True)
        classifier_text = '\n'.join(classifiers) + '\n'
        request = self.request_factory.get({':action': 'list_classifiers'})
        response = self.package_index(request)
        self.assertEquals(response.status_code, 200,
                          'Index did not return OK response for list_classifiers request')
        self.assertTrue(response['Content-Type'].startswith('text/plain'),
                        'Index did not return text/plain Content-Type in response')
        self.assertEquals(response.content, classifier_text,
                          'Index did not return correct list of classifiers')

    def testVerify(self):
        """
        Make sure we verify that name and version are present, and that known
        classifiers have been sent.
        """
        classifiers = ['Development Status :: 3 - Alpha', 'Intended Audience :: Developers']
        invalid_classifiers = ['Development Status :: 3 - Alpha', 'Intended Audience :: Developers', 'Cheese :: Limburger']
        data = {
            ':action': 'verify',
            'name': 'test-app',
            'author': 'John Doe',
            'author_email': 'john.doe@example.com',
            'classifiers': classifiers,
        }
        request = self.request_factory.post(data)
        response = self.package_index(request)
        self.assertEquals(response.status_code, 400,
                          'Index did not return Bad Request response for metadata validation request')
        self.assertTrue(response['Content-Type'].startswith('text/plain'),
                        'Index did not return text/plain Content-Type in response')
        self.assertContains(response, 'required', status_code=400, count=1)
        del data['classifiers']
        data['classifiers'] = invalid_classifiers
        request = self.request_factory.post(data)
        response = self.package_index(request)
        self.assertContains(response, 'not one of the available choices', status_code=400, count=1)
        data['version'] = '0.1'
        del data['classifiers']
        data['classifers'] = classifiers
        request = self.request_factory.post(data)
        response = self.package_index(request)
        self.assertContains(response, 'valid', status_code=200, count=1)

    def testRegister(self):
        """
        Ensure valid submissions from authenticated users are registered, and 400s
        returned for invalid release metadata.
        Ensure we send a 400 in response to a request to register and already
        registered release.
        TODO: test against user that doesn't have release add permission
        """
        classifiers = ['Development Status :: 3 - Alpha', 'Intended Audience :: Developers']
        data = {
            ':action': 'submit',
            'name': 'test-app',
            'version': '0.1',
            'author': 'John Doe',
            'author_email': 'john.doe@example.com',
            'classifiers': classifiers,
        }

        auth_string = self.buildAuthHeader('test', 'test')
        h = {'HTTP_AUTHORIZATION': auth_string}

        request = self.request_factory.get(data, h)
        response = self.package_index(request)
        self.assertEquals(response.status_code, 405,
                          'Index did not return a Not Allowed response for an invalid submit method')

        request = self.request_factory.post(data, h)
        response = self.package_index(request)
        self.assertContains(response, 'registered', status_code=200, count=1)
        self.assertTrue(bool(Release.objects.filter(package__name=data['name'], version=data['version'])),
                        'Index did not record an accepted release')
        
        request = self.request_factory.post(data, {'HTTP_AUTHORIZATION': auth_string})
        response = self.package_index(request)
        self.assertContains(response, 'already exists', status_code=400, count=1)

    def testFileUpload(self):
        """
        Test distribution file registration.
        """
        classifiers = [
            'Development Status :: 3 - Alpha',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: BSD License',
            'Operating System :: OS Independent',
            'Programming Language :: Python',
        ]
        data = {
            ':action': 'file_upload',
            'name': 'test-app',
            'version': '0.1',
            'author': 'John Doe',
            'author_email': 'john.doe@example.com',
            'filetype': 'sdist',
            'classifiers': classifiers,
        }
        request = self.request_factory.post(data)
        response = self.package_index(request)
        self.assertEquals(response.status_code, 401,
                          'Authorization not enforced for file_upload')

        auth_string = self.buildAuthHeader('test', 'test')
        h = {'HTTP_AUTHORIZATION': auth_string}

        request = self.request_factory.post(data, h)
        response = self.package_index(request)
        self.assertContains(response, 'not been registered', status_code=400, count=1)

        f = StringIO()
        f.write('some text')
        f.seek(0)
        data['name'] = 'test-module'
        data['content'] = ('foo.zip', f.getvalue())
        request = self.request_factory.post(data, h)
        response = self.package_index(request)
        self.assertContains(response, 'filename must start with', status_code=400, count=1)

        data['content'] = ('test-module-0.1.zip', f.getvalue())
        request = self.request_factory.post(data, h)
        response = self.package_index(request)
        self.assertContains(response, 'Invalid distribution file', status_code=400, count=1)

        dist_path = os.path.join(os.path.dirname(__file__), 'fixtures/test-module-0.1.zip')
        filename = os.path.basename(dist_path)
        fh = open(dist_path, 'r+b')
        data['content'] = (filename, fh.read())
        fh.close()
        real_md5 = md5constructor()
        real_md5.update(data['content'][1])
        data['md5_digest'] = 'acbd18db4cc2f85cedef654fccc4a4d8'
        request = self.request_factory.post(data, h)
        response = self.package_index(request)
        self.assertContains(response, 'digest does not match', status_code=400, count=1)

        del data['md5_digest']
        request = self.request_factory.post(data, h)
        response = self.package_index(request)
        self.assertContains(response, 'successfully registered', status_code=200, count=1)

        release = Release.objects.get(package__name=data['name'], version=data['version'])
        upload = release.files.get(filetype=data['filetype'])
        self.assertEquals(upload.md5_digest, real_md5.hexdigest(),
                          'MD5 digest for upload not calculated properly')
        # and clean up our mess
        upload.content.delete()
