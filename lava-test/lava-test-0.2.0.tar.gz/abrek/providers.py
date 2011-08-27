"""
Test providers.

Allow listing and loading of tests in a generic way.
"""

from pkg_resources import working_set

from abrek.api import ITestProvider
from abrek.cache import AbrekCache
from abrek.config import get_config
from abrek.testdef import AbrekDeclarativeTest


class BuiltInProvider(ITestProvider):
    """
    Test provider that provides tests shipped in the Abrek source tree
    """

    _builtin_tests = [
        'bootchart',
        'firefox',
        'glmemperf',
        'gmpbench',
        'gtkperf',
        'ltp',
        'peacekeeper'
        'posixtestsuite',
        'pwrmgmt',
        'pybench',
        'smem',
        'stream',
        'tiobench',
        'x11perf',
        'xrestop',
    ]

    def __init__(self, config):
        pass

    @property
    def description(self):
        return "Tests built directly into Abrek:"

    def __iter__(self):
        return iter(self._builtin_tests)

    def __getitem__(self, test_name):
        try:
            module = __import__("abrek.test_definitions.%s" % test_name, fromlist=[''])
        except ImportError:
            raise KeyError(test_name)
        else:
            return module.testobj


class PkgResourcesProvider(ITestProvider):
    """
    Test provider that provides tests declared in pkg_resources working_set

    By default it looks at the 'abrek.test_definitions' name space but it can
    be changed with custom 'namespace' configuration entry.
    """

    def __init__(self, config):
        self._config = config

    @property
    def namespace(self):
        return self._config.get("namespace", "abrek.test_definitions")

    @property
    def description(self):
        return "Tests provided by installed python packages:"

    def __iter__(self):
        for entry_point in working_set.iter_entry_points(self.namespace):
            yield entry_point.name

    def __getitem__(self, test_name):
        for entry_point in working_set.iter_entry_points(self.namespace, test_name):
            return entry_point.load().testobj
        raise KeyError(test_name)


class RegistryProvider(ITestProvider):
    """
    Test provider that provides declarative tests listed in the test registry.
    """
    def __init__(self, config):
        self._config = config
        self._cache = None 

    @property
    def entries(self):
        """
        List of URLs to AbrekDeclarativeTest description files
        """
        return self._config.get("entries", [])

    @property
    def description(self):
        return "Tests provided by Abrek registry:"

    @classmethod
    def register_remote_test(self, test_url):
        config = get_config() # This is a different config object from self._config
        provider_config = config.get_provider_config("abrek.providers:RegistryProvider")
        if "entries" not in provider_config:
            provider_config["entries"] = []
        if test_url not in provider_config["entries"]:
            provider_config["entries"].append(test_url)
            config._save_registry()
        else:
            raise ValueError("This test is already registered")

    def _load_remote_test(self, test_url):
        """
        Load AbrekDeclarativeTest from a (possibly cached copy of) test_url
        """
        cache = AbrekCache.get_instance()
        with cache.open_cached_url(test_url) as stream:
            return AbrekDeclarativeTest.load_from_stream(stream)

    def _fill_cache(self):
        """
        Fill the cache of all remote tests
        """
        if self._cache is not None:
            return
        self._cache = {}
        for test_url in self.entries:
            test = self._load_remote_test(test_url)
            if test.testname in self._cache:
                raise ValueError("Duplicate test %s declared" % test.testname)
            self._cache[test.testname] = test

    def __iter__(self):
        self._fill_cache()
        for test_name in self._cache.iterkeys():
            yield test_name

    def __getitem__(self, test_name):
        self._fill_cache()
        return self._cache[test_name]
