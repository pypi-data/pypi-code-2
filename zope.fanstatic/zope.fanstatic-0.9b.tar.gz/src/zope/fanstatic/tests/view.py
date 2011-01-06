from fanstatic import Library, Resource
from fanstatic import get_needed

foo = Library("foo", "foo_dir")

a = Resource(foo, "a.js")

b = Resource(foo, "b.js", depends=[a])

class TestSingle(object):
    def widget(self):
        a.need()
        return "the widget HTML itself"

class TestMultiple(object):
    def widget(self):
        b.need()
        return "the widget HTML itself"

class TestBottom(object):
    def widget(self):
        b.need()
        # XXX this does not use any official API and needs to be
        # reconsidered. Its done anyway now to make the tests pass,
        # instead of just removing the corresponding test.
        get_needed()._bottom = True
        get_needed()._force_bottom = True
        return "the widget HTML itself"

class TestInlineResource(object):
    pass

