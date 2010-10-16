import httplib

from mercurial.util import Abort

from nose.tools import assert_equals, assert_raises
from fudge import with_fakes, Fake, patch_object, clear_expectations

from hghudson import build

class TestHook(object):

    def setup(self):
        clear_expectations()
        self.ui = Fake().expects('config').with_args('hudson', 'url').returns('localhost:8080')
        self.ui.next_call().with_args('hudson', 'job').returns('testJob')
        self.ui.next_call().with_args('hudson', 'authentication_token')

        self.fake_connection = Fake().expects('request').with_args('GET', '/job/testJob/build');

        monkeypatched_connection = Fake(callable=True).with_args('localhost:8080').returns(self.fake_connection)
        self.patched_api = patch_object(httplib, 'HTTPConnection', monkeypatched_connection)

    def teardown(self):
        self.patched_api.restore()

    @with_fakes
    def test_successful_call(self):
        self.fake_connection.expects('getresponse').returns_fake().has_attr(status=httplib.FOUND)

        assert_equals(0, build(self.ui, None))

    @with_fakes
    def test_call_to_non_existent_job(self):
        self.fake_connection.expects('getresponse').returns_fake().has_attr(status=httplib.NOT_FOUND)

        assert_raises(Abort, build, self.ui, None)

    @with_fakes
    def test_without_hudson_uri(self):
        clear_expectations()

        self.ui = Fake().expects('config').with_args('hudson', 'url')
        assert_raises(Abort, build, self.ui, None)

    @with_fakes
    def test_with_empty_hudson_uri(self):
        clear_expectations()

        self.ui = Fake().expects('config').with_args('hudson', 'url').returns('')
        assert_raises(Abort, build, self.ui, None)

    @with_fakes
    def test_without_hudson_job(self):
        clear_expectations()

        self.ui = Fake().expects('config').with_args('hudson', 'url').returns('localhost:8080')
        self.ui.next_call().with_args('hudson', 'job')
        assert_raises(Abort, build, self.ui, None)

    @with_fakes
    def test_with_empty_hudson_job(self):
        clear_expectations()

        self.ui = Fake().expects('config').with_args('hudson', 'url').returns('localhost:8080')
        self.ui.next_call().with_args('hudson', 'job').returns('')

        assert_raises(Abort, build, self.ui, None)


    @with_fakes
    def test_call_to_forbidden_job(self):
        self.fake_connection.expects('getresponse').returns_fake().has_attr(status=httplib.FORBIDDEN)

        assert_raises(Abort, build, self.ui, None)


    @with_fakes
    def test_call_with_authentication_token(self):
        clear_expectations()

        self.ui = Fake().expects('config').with_args('hudson', 'url').returns('localhost:8080')
        self.ui.next_call().with_args('hudson', 'job').returns('testJob')
        self.ui.next_call().with_args('hudson', 'authentication_token').returns('secret')

        self.fake_connection = Fake().expects('request').with_args('GET', '/job/testJob/build?token=secret');
        self.fake_connection.expects('getresponse').returns_fake().has_attr(status=httplib.FOUND)

        monkeypatched_connection = Fake(callable=True).with_args('localhost:8080').returns(self.fake_connection)
        self.patched_api = patch_object(httplib, 'HTTPConnection', monkeypatched_connection)

        assert_equals(0, build(self.ui, None))
