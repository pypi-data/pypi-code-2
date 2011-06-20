import kforge.plugin.base
import kforge.utils.mailer
from kforge.dictionarywords import *
from kforge.command.emailpassword import EmailCommand

# Todo: Move to command module.
class EmailNotifyCommand(EmailCommand):

    def __init__(self, domainObject, transitionName):
        self.domainObject = domainObject
        self.transitionName = transitionName

    def getMessageSubject(self):
        # Todo: Make sure this is already decoded in the dictionary?
        serviceName = self.dictionary[SYSTEM_SERVICE_NAME].decode('utf-8')
        msgSubject = 'Changes to %s' % serviceName
        return msgSubject

    def getMessageBody(self):
        msgBody = '%s %s (%s) was %s.' % (
            self.domainObject.meta.name,
            self.domainObject.getLabelValue(),
            self.domainObject.getRegisterKeyValue(),
            self.transitionName,
        )
        return msgBody

    def getMessageToList(self):
        adminRole = self.registry.roles['Administrator']
        emailSet = set()
        for person in self.registry.persons:
            if person.role == adminRole and person.email:
                emailSet.add(person.email)
        if self.domainObject.meta.name == 'Project':
            project = self.domainObject
        elif self.domainObject.meta.name == 'Service':
            project = self.domainObject.project
        elif self.domainObject.meta.name == 'Member':
            project = self.domainObject.project
        else:
            project = None
        if project != None:
            for member in project.members:
                if member.role == adminRole and member.person.email:
                    emailSet.add(member.person.email)
        return emailSet


class Plugin(kforge.plugin.base.NonServicePlugin):
    "Notify Plugin"

    notifyCommandClass = EmailNotifyCommand

    def onProjectCreate(self, project):
        self.notify(project, 'created')

    def onProjectDelete(self, project):
        self.notify(project, 'deleted')
       
    def onPersonCreate(self, person):
        self.notify(person, 'created')

    def onPersonDelete(self, person):
        self.notify(person, 'deleted')

    def onServiceCreate(self, service):
        self.notify(service, 'created')

    def onServiceDelete(self, service):
        self.notify(service, 'deleted')
       
    def onMemberCreate(self, member):
        self.notify(member, 'created')

    def onMemberDelete(self, member):
        self.notify(member, 'deleted')

    def notify(self, domainObject, transitionName):
        if self.dictionary[DB_MIGRATION_IN_PROGRESS]:
            pass
        elif not self.dictionary[EMAIL_NOTIFY_CHANGES]:
            msg = "Not configured to send notification of changes by email."
            self.logger.info(msg)
        else:
            cmd = self.notifyCommandClass(domainObject, transitionName)
            cmd.execute()

