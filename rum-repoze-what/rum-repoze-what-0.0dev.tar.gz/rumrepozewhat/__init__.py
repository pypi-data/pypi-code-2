import logging
from rum.genericfunctions import when, around
from rum.policy import Denial, Policy, anyone, NotProvided
from repoze.what.predicates import NotAuthorizedError, Predicate
from rum import app

log = logging.getLogger(__name__)

def adapt_rw_predicate(predicate):
    def checker(policy, obj, action, attr, user):
        #WARNING: user parameter is always ignored when adapting repoze.what
        # since r.w unconditionally uses the currently logged in user
        try:
            predicate.check_authorization(app.request.environ)
            return True
        except NotAuthorizedError, e:
            return Denial(unicode(e))
    return checker#


def adapt_repoze_what_to_policy_class(policy):
    """docstring for adapt_repoze_what_to_policy_class"""
    @when(policy.register.im_func, "isinstance(predicate, Predicate)")
    def __register_adapted_repoze_what_predicate(
        cls, predicate, obj=None, action=None, attr=None, rule=None
        ):
        predicate = adapt_rw_predicate(predicate)
        return cls.register(predicate, obj, action, attr, rule)
