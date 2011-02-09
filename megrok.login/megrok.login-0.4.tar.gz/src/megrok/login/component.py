import martian
from martian.error import GrokImportError

class enable(martian.MarkerDirective):
    scope = martian.CLASS
    store = martian.ONCE

class viewname(martian.Directive):
    scope = martian.CLASS
    store = martian.ONCE
    default = u'loginForm.html'
    
    def factory(self, viewname=None):
        if viewname is None:
            viewname = self.default
        if martian.util.not_unicode_or_ascii(viewname):
            raise GrokImportError(
                "You can only pass unicode, None or ASCII "
                "to the 'megrok.login.viewname' directive.")
        return viewname

class strict(martian.MarkerDirective):
    scope = martian.CLASS
    store = martian.ONCE

class autoregister(martian.MultipleTimesDirective):
    scope = martian.CLASS

class setup(martian.Directive):
    scope = martian.CLASS
    store = martian.ONCE
    default = None

    # XXX: Check, that the given callable exists
