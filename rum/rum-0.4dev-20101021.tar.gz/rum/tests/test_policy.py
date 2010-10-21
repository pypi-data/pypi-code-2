from unittest import TestCase
from rum import policy

class TestingPolicy(policy.Policy):
    pass

class Edible(object): pass
class Potato(Edible): pass
class Tomato(Edible): pass
class Chili(Edible): pass
class Cookie(Edible): pass

class User(object):
    def __init__(self, permissions):
        self.permissions = permissions

def all_permissions(*perms):
    def check(self, obj, action, attr, user):
        allowed = all(map(user.permissions.__contains__, perms))
        if not allowed:
            return policy.Denial("Need to have all: %r"%(perms,))
        return True
    return check

def any_permission(*perms):
    def check(self, obj, action, attr, user):
        allowed = any(map(user.permissions.__contains__, perms))
        if not allowed:
            return policy.Denial("Need to have at least one: %r"%(perms,))
        return True
    return check

# A permission on an action on an obj
TestingPolicy.register(
    predicate=any_permission("edit", "edit_potato"),
    obj=Potato,
    action="edit"
    )

TestingPolicy.register(
    predicate=policy.not_anonymous,
    obj=Cookie
)

# A permission on an action and any obj
TestingPolicy.register(
    predicate=any_permission("edit"),
    action="edit"
    )

# Overlapping rules
TestingPolicy.register(
    predicate=any_permission("new"),
    obj=Tomato,
    action="new"
    )
TestingPolicy.register(
    predicate=any_permission("new_tomato"),
    obj=Tomato,
    action="new"
    )

TestingPolicy.register(
    predicate=any_permission("cook"),
    obj=Chili,
    action="cook",
    attr="hotness"
)
class TestPolicy(TestCase):
    def makeOne(self):
        return TestingPolicy()

    def test_register_action_on_obj(self):
        policy = self.makeOne()
        allowed = policy.has_permission(
            Potato(), 'edit', user=User(['edit_potato'])
            )
        self.failUnless(allowed)

        allowed = policy.has_permission(Potato(), 'edit', user=User(['add']))
        self.failUnless(not allowed, allowed)

    def test_register_action(self):
        policy = self.makeOne()
        allowed = policy.has_permission(Potato(), 'edit', user=User(['edit']))
        self.failUnless(allowed)
        allowed = policy.has_permission(Tomato(), 'edit', user=User(['edit']))
        self.failUnless(allowed)
    
    def test_not_anonymous(self):
        policy = self.makeOne()
        allowed=policy.has_permission(Cookie(), 'eat them all')
        self.failUnless(not allowed, allowed)
        allowed=policy.has_permission(Cookie(), 'eat them all', user=User([]))
        self.failUnless(allowed)

    def test_register_overlapping_rules(self):
        # When two rules with the same preference exist then if any one of
        # them grants permission then access is granted
        policy = self.makeOne()
        allowed = policy.has_permission(Tomato(), 'new', user=User(['new']))
        self.failUnless(allowed)
        allowed = policy.has_permission(Tomato(), 'new', user=User(['new_tomato']))
        self.failUnless(allowed)
        allowed = policy.has_permission(Tomato(), 'new', user=User(['foo']))
        self.failUnless(not allowed)

    def test_deny_when_no_rules_apply(self):
        policy = self.makeOne()
        allowed = policy.has_permission(Edible(), 'new', user=User(['new']))
        self.failUnless(not allowed)
    def test_attr_permissions(self):
        policy = self.makeOne()
        u=User(["cook"])
        allowed = policy.has_permission(Chili(),"cook", user=u)
        self.failUnless(allowed)
        allowed = policy.has_permission(Chili(),"cook", attr="hotness", user=u)
        self.failUnless(allowed)
        allowed = policy.has_permission(Chili(),"cook", attr="amount", user=u)
        self.failUnless(not allowed)