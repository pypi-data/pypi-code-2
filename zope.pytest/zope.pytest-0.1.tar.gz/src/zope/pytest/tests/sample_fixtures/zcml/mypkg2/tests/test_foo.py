import mypkg2
from zope.component import queryUtility
from mypkg2.interfaces import IFoo
from zope.pytest import configure

def pytest_funcarg__config_mypkg2(request):
    return configure(request, mypkg2, 'ftesting.zcml')

def test_get_utility(config_mypkg2):
    util = queryUtility(IFoo, name='foo utility', default=None)
    assert util is not None

def test_dofoo_utility(config_mypkg2):
    util = queryUtility(IFoo, name='foo utility', default=None)
    assert util().do_foo() == 'Foo!'
