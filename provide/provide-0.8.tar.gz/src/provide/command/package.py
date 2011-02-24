from dm.command import *
import provide.regexps
import re

class PackageCommand(Command):
    "Abstract Package command."
        
    def __init__(self, name):
        super(PackageCommand, self).__init__(packageName=name)
        self.name = name
        self.package = None
        self.packages = self.registry.packages


class PackageCreate(DomainObjectCreate):
    "Command to create a new package."

    reservedNames = re.compile('^%s$' % provide.regexps.reservedPackageName)

    def __init__(self, name='', **kwds):
        super(PackageCreate, self).__init__(
            typeName='Package', objectId=name, objectKwds=kwds
        )
        self.package = None

    def execute(self):
        super(PackageCreate, self).execute()
        self.package = self.object


class PackageRead(DomainObjectRead):
    "Command to read a registered package."

    def __init__(self, name='', **kwds):
        super(PackageRead, self).__init__(
            typeName='Package', objectId=name, objectKwds=kwds
        )
        self.package = None

    def execute(self):
        super(PackageRead, self).execute()
        self.package = self.object


class PackageDelete(PackageCommand):
    "Command to delete a registered package."

    def __init__(self, name):
        super(PackageDelete, self).__init__(name)

    def execute(self):
        "Make it so."
        super(PackageDelete, self).execute()
        if not self.name in self.packages:
            message = "No package found with name '%s'." % self.name
            self.raiseError(message)
        package = self.packages[self.name]
        try:
            package.delete()
        except Exception, inst:
            message = "Couldn't delete package: %s" % str(inst)
            self.raiseError(message)
        else:
            self.commitSuccess()


class PackageUndelete(PackageCommand):
    "Command to undelete a deleted registered package."

    def __init__(self, name):
        super(PackageUndelete, self).__init__(name)

    def execute(self):
        "Make it so."
        super(PackageUndelete, self).execute()
        if not self.name in self.packages.deleted:
            message = "No deleted package found with name '%s'." % self.name
            self.raiseError(message)
        package = self.packages.deleted[self.name]
        package.undelete()
        self.commitSuccess()


class PackagePurge(PackageCommand):
    "Command to purge a deleted registered package."

    def __init__(self, name):
        super(PackagePurge, self).__init__(name)

    def execute(self):
        "Make it so."
        super(PackagePurge, self).execute()
        if not self.name in self.packages.deleted:
            message = "No deleted package found with name '%s'." % self.name
            self.raiseError(message)
        package = self.packages.deleted[self.name]
        package.purge()
        self.commitSuccess()


class AllPackageRead(PackageRead):
    "Command to read any package, regardless of state."

    def __init__(self, name):
        super(AllPackageRead, self).__init__(name)
        self.packages = self.registry.packages.all


class PackageList(PackageCommand):
    "Command to list registered packages."

    def __init__(self, userQuery='', startsWith='', startsWithAttributeName=''):
        super(PackageList, self).__init__('')
        self.userQuery= userQuery
        self.startsWith = startsWith
        self.startsWithAttributeName = startsWithAttributeName

    def execute(self):
        "Make it so."
        super(PackageList, self).execute()
        if self.startsWith:
            selection = self.packages.startsWith(
                value=self.startsWith,
                attributeName=self.startsWithAttributeName
            )
            self.results = [p for p in selection]
        elif self.userQuery:
            selection = self.packages.search(
                userQuery=self.userQuery
            )
            self.results = [p for p in selection]
        else:
            self.results = [p for p in self.packages]

