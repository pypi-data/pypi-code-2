# Copyright (c) 2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id: mockers.py 43247 2010-07-02 16:15:13Z sylvain $

from zope.publisher.interfaces.browser import IBrowserRequest
from zope.interface import implements
from ZODB.POSException import ConflictError
import ExtensionClass


class MockWSGIStartResponse(object):
    """This mock object is used instead of the start_response callable
    of WSGI. It records any call to it.
    """

    __slots__ = ['status', '__headers', 'data']

    def __init__(self):
        self.status = None
        self.__headers = None
        self.data = []

    @apply
    def headers():
        def set(self, value):
            self.__headers = value
        def get(self):
            if self.__headers is None:
                return None
            headers = list(self.__headers)
            headers.sort(key=lambda t: t[0])
            return headers
        return property(get, set)

    def __call__(self, status, headers):
        assert self.status is None, "Status already set in mock response"
        assert self.headers is None, "Headers already set in mock response"
        self.status = status
        self.headers = headers
        return self.write

    def write(self, data):
        self.data.append(data)


class Mocker(object):

    def __init__(self):
        self.__called = []

    def __getattr__(self, method_name):
        if method_name.startswith('_'):
            raise AttributeError(method_name)
        def method(*args, **kwargs):
            self.mocker_call(method_name, args, kwargs)
        return method

    def mocker_call(self, method_name, args, kwargs):
        if not method_name.startswith('mocker_'):
            self.__called.append((method_name, args, kwargs))

    def mocker_called(self):
        called = list(self.__called)
        del self.__called[:]
        return called


class MockTransactionManager(Mocker):
    """Mock a Zope transaction manager.
    """

    def __init__(self):
        super(MockTransactionManager, self).__init__()
        self.__conflict = False

    def mocker_set_conflict(self, state):
        self.__conflict = state

    def commit(self):
        self.mocker_call('commit', (), {})
        if self.__conflict:
            raise ConflictError()


class MockApplication(ExtensionClass.Base):
    """Mockup Application.
    """

    def getPhysicalPath(self):
        return ('',)


class MockRequest(Mocker):
    implements(IBrowserRequest)

    def __init__(self, args=(), data=(), view=None, response=None, retry=0):
        super(MockRequest, self).__init__()
        self.response = response
        self.args = args
        self.environ = {}
        self.other = {}
        self.__data = data
        self.__view = view
        self.__tries = retry

    def __getitem__(self, key):
        return self.__data[key]

    def __setitem__(self, key, value):
        self.__data[key] = value

    def get(self, key, default=None):
        return self.__data.get(key, default)

    def traverse(self, path, **options):
        return self.__view

    def supports_retry(self):
        return self.__tries != 0

    def retry(self):
        self.mocker_call('retry', (), {})
        assert self.__tries > 0, "Number of retries exceeded"
        self.__tries -= 1
        return self
