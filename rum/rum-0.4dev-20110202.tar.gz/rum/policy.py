from rum.i18n import _
from rum.exceptions import SecurityDenial
from rumpolicy import Policy, DummyPolicy, Denial, filter, has_permission, NotProvided, anyone, not_anonymous
import peak.rules.core as rules_core
from prioritized_methods import prioritized_when as when,\
                                prioritized_around as around,\
                                prioritized_before as before,\
                                prioritized_after as after,\
                                generic


class Policy(Policy):
    exception_class = SecurityDenial
    def _(self, string):
        return _(string)
    def get_current_user(self):
        from rum import app
        return  app.request.current_user

class DummyPolicy(Policy): pass
DummyPolicy.register(anyone)