from hurry.resource import Library, ResourceInclusion, bottom


foo = Library("foo", "foo_dir")

a = ResourceInclusion(foo, "a.js")

b = ResourceInclusion(foo, "b.js", depends=[a])


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
        bottom(force=True)
        return "the widget HTML itself"
