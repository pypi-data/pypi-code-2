"""
KForge AccessControl plugin.

"""

import kforge.plugin.base
import os
from dm.strategy import FindProtectionObject
from dm.strategy import CreateProtectionObject
from dm.dictionarywords import DB_MIGRATION_IN_PROGRESS

class Plugin(kforge.plugin.base.NonServicePlugin):
    "AccessControl plugin."
    
    def __init__(self, domainObject):
        super(Plugin, self).__init__(domainObject)
        name = 'accesscontrol'

    def onPersonCreate(self, person):
        if self.dictionary[DB_MIGRATION_IN_PROGRESS]:
            return
        protectionObject = CreateProtectionObject(person).create()
        for permission in protectionObject.permissions:
            if not permission in person.grants:
                person.grants.create(permission)
    
    def onPersonPurge(self, person):
        if self.dictionary[DB_MIGRATION_IN_PROGRESS]:
            return
        findObject = FindProtectionObject(person)
        protectionObject = findObject.find()
        if protectionObject:
            protectionObject.delete()

    # Todo: Fix migration, so that these protection objects and grants are created for already existing members.

    def onMemberCreate(self, member):
        if self.dictionary[DB_MIGRATION_IN_PROGRESS]:
            return
        protectionObject = CreateProtectionObject(member).create()
        for permission in protectionObject.permissions:
            if permission.action.name == 'Delete':
                if not permission in member.person.grants:
                    member.person.grants.create(permission)
    
    def onMemberPurge(self, member):
        if self.dictionary[DB_MIGRATION_IN_PROGRESS]:
            return
        protectionObject = FindProtectionObject(member).find()
        if protectionObject:
            protectionObject.delete()

