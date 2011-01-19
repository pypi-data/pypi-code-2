# To change this template, choose Tools | Templates
# and open the template in the editor.

import unittest

from pydenji.appcontext.wiring import ArgNameContextWirer
from pydenji.appcontext.wiring import PropertyAndContextMergingProxy
from pydenji.appcontext.wiring import NameClashError

class Peer(object):
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

    def __repr__(self):
        return "<Peer %s %s>" % (str(self.args), str(self.kwargs))

    def __eq__(self, other):
        return True if (
                (other.args == self.args) and
                (other.kwargs == self.kwargs)
                ) else False
                

class DummyContext(object):
    def get_object(self, name, *args, **kwargs):
        if name != "peer":
            raise KeyError, "Can't handle anything different from peer"
        return Peer(*args, **kwargs)

    def __contains__(self, key):
        return True if (key == "peer") else False

    def __iter__(self):
        return iter(["peer"])
    
def factory(a, b, peer):
    return (a, b, peer)

class TestContextWiring(unittest.TestCase):
    def test_contextwiring_fetches_data_from_mapping_and_context(self):
        context = DummyContext()
        mapping = {"a":1, "b":2}
        cw = ArgNameContextWirer(context, mapping)
        wired = cw.wire(factory)
        self.assertEquals((1, 2, Peer()), wired)

    def test_call_time_wiring_args_can_override_mapping_values(self):
        context = DummyContext()
        mapping = {"a":1, "b":2}
        cw = ArgNameContextWirer(context, mapping)
        wired = cw.wire(factory, 5, b=4)
        self.assertEquals((5, 4, Peer()), wired)
    
    def test_call_time_wiring_args_can_override_context_values(self):
        context = DummyContext()
        mapping = {"a":1, "b":2}
        cw = ArgNameContextWirer(context, mapping)
        wired = cw.wire(factory, peer="foo")
        self.assertEquals((1, 2, "foo"), wired)


class TestPropertyAndContextMergingProxy(unittest.TestCase):
    def setUp(self):
        context = DummyContext()
        mapping = {"a":3, "b":4}
        self.pacmp = PropertyAndContextMergingProxy(context, mapping)

    def test_mergingproxy_fetches_value_from_mapping_if_unavailable_in_context(self):
        self.assertEquals(3, self.pacmp["a"])

    def test_mergingproxy_fetches_value_from_context_if_unavailable_in_mapping(self):
        self.assertEquals(Peer(), self.pacmp["peer"])

    def test_mergingproxy_prohibits_proxying_if_clashing_values(self):
        context = DummyContext()
        mapping = {"peer":3, "b":4}
        self.assertRaises(NameClashError, PropertyAndContextMergingProxy, context, mapping)


if __name__ == '__main__':
    unittest.main()

