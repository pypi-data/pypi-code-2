import dm.command
import dm.command.person

import kforge.utils.mailer
from kforge.dictionarywords import SYSTEM_NAME
from kforge.dictionarywords import SYSTEM_SERVICE_NAME
from kforge.dictionarywords import SERVICE_EMAIL
from kforge.dictionarywords import DOMAIN_NAME
from kforge.dictionarywords import SMTP_HOST
from kforge.command.emailpassword import EmailCommand

class EmailJoinRequest(EmailCommand):
        
    def __init__(self, project, person):
        super(EmailJoinRequest, self).__init__()
        self.project = project
        self.person = person

    def execute(self):
        super(EmailJoinRequest, self).execute()
        if self.isDispatchedOK:
            msg = "Join request mail sent for project %s, person %s" % (self.project.name, self.person.name)
            self.logger.info(msg)
        else:
            msg = "Join request mail could not be sent for project %s, person %s" % (self.project.name, self.person.name)
            self.logger.warn(msg)

    def getMessageToList(self):
        emails = []
        adminRole = self.registry.roles['Administrator']
        for member in self.project.members:
            if member.role == adminRole:
                emails.append(member.person.email)
        return emails

    def getMessageSubject(self):
        subject =  '%s membership request' % self.project.name
        return self.wrapMessageSubject(subject)

    def getMessageBody(self):
        serviceName = self.dictionary[SYSTEM_SERVICE_NAME].decode('utf-8')
        msgBody = \
'''A request has been made to join a project you administer.

Project: %s
Person: %s

You may wish to log in to your account to service this request.

Regards,

The %s Team
''' % (self.project.name, self.person.name, serviceName)
        return msgBody


class EmailJoinApprove(EmailCommand):
        
    def __init__(self, project, person):
        super(EmailJoinApprove, self).__init__()
        self.project = project
        self.person = person

    def execute(self):
        super(EmailJoinApprove, self).execute()
        if self.isDispatchedOK:
            msg = "Approve mail sent for project %s, person %s" % (self.project.name, self.person.name)
            self.logger.info(msg)
        else:
            msg = "Approve mail could not be sent for project %s, person %s" % (self.project.name, self.person.name)
            self.logger.warn(msg)

    def getMessageToList(self):
        if self.person is None:
            return []
        return [self.person.email]

    def getMessageSubject(self):
        subject =  '%s membership request approved' % self.project.name
        return self.wrapMessageSubject(subject)

    def getMessageBody(self):
        serviceName = self.dictionary[SYSTEM_SERVICE_NAME].decode('utf-8')
        msgBody = \
'''The following membership request has been approved by the project administrator:

Project: %s
Person: %s
Role: %s

You should now be able to access the project when you log into your account.

Regards,

The %s Team
''' % (self.project.name, self.person.name, self.project.members[self.person].role.name, serviceName)
        return msgBody

class EmailJoinReject(EmailCommand):
        
    def __init__(self, project, person):
        super(EmailJoinReject, self).__init__()
        self.project = project
        self.person = person

    def execute(self):
        super(EmailJoinReject, self).execute()
        if self.isDispatchedOK:
            msg = "Reject mail sent for project %s, person %s" % (self.project.name, self.person.name)
            self.logger.info(msg)
        else:
            msg = "Reject mail could not be sent for project %s, person %s" % (self.project.name, self.person.name)
            self.logger.warn(msg)

    def getMessageToList(self):
        if self.person is None:
            return []
        return [self.person.email]

    def getMessageSubject(self):
        subject =  '%s membership request rejected' % self.project.name
        return self.wrapMessageSubject(subject)

    def getMessageBody(self):
        serviceName = self.dictionary[SYSTEM_SERVICE_NAME].decode('utf-8')
        msgBody = \
'''The following membership request has been rejected by the project administrator:

Project: %s
Person: %s

Regards,

The %s Team
''' % (self.project.name, self.person.name, serviceName)
        return msgBody
