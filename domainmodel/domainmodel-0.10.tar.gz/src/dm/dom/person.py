from dm.dom.stateful import *
from dm.ioc import *
from dm.messagedigest import md5
#import dm.messagedigest import sha

class Person(StandardObject):
    "Registered person."

    searchAttributeNames = ['name', 'fullname']

    password = Password(default='')
    fullname = String(default='')
    email    = String(default='')
    role     = HasA('Role', default=StandardObject.dictionary['person_role'])
    sessions = HasMany('Session', 'key')
    grants   = HasMany('PersonalGrant', 'permission')
    bars     = HasMany('PersonalBar', 'permission')

    def initialise(self, register=None):
        super(Person, self).initialise(register)
        if not self.role:
            roleName = self.dictionary['person_role']
            self.role = self.registry.roles[roleName]
            self.isChanged = True

    def isPassword(self, password):
        if not self.password:
            return False
        return self.password == self.makeDigest(password)

    def setPassword(self, password):
        if password:
            self.password = self.makeDigest(password)
        else:
            self.password = ''

    def makeDigest(self, clearText):
        passwordAttr = self.meta.attributeNames['password']
        return passwordAttr.makeDigest(clearText)

    def delete(self):
        for session in self.sessions:
            session.delete()
        super(Person, self).delete()

    def undelete(self):
        super(Person, self).undelete()

    def purge(self):
        for session in self.sessions:
            session.delete()
        for grant in self.grants:
            grant.delete()
        for bar in self.bars:
            bar.delete()
        super(Person, self).purge()


class PersonalGrant(SimpleObject):
    "Positively associates a Person directly with a Permission."

    person      = HasA('Person')
    permission  = HasA('Permission')

    def getLabelValue(self):
        return "%s-%s" % (
            self.person.getLabelValue(),
            self.permission.getLabelValue(),
        )


class PersonalBar(PersonalGrant):
    "Negatively associates a Person directly with a Permission."
    pass

