import dm.command
import dm.command.person

import kforge.utils.mailer
import kforge.utils.password
from kforge.dictionarywords import *

# Todo: Extract this to general command package.
class EmailCommand(dm.command.Command):

    def execute(self):
        msgFrom = self.getMessageFrom()
        msgToList = self.getMessageToList()
        msgSubject = self.getMessageSubject()
        msgBody = self.getMessageBody()
        self.dispatchEmailMessage(msgFrom, msgToList, msgSubject, msgBody)

    def dispatchEmailMessage(self, msgFrom, msgToList, msgSubject, msgBody):
        smtpHost = self.dictionary[SMTP_HOST]
        msg = "email from: %s to: %s subject: %s body: %s host: %s" % (
            repr(msgFrom), repr(msgToList), repr(msgSubject), repr(msgBody), repr(smtpHost)
        )
        self.isDispatchedOK = False
        if not self.dictionary[ENABLE_EMAIL_SENDING]:
            self.logger.info("Skipping sending %s" % msg)
        else:
            self.logger.info("Sending %s" % msg)
            for msgTo in msgToList:
                if msgTo:
                    try:
                        kforge.utils.mailer.sendmail(msgFrom, msgTo, msgSubject, msgBody, smtpHost)
                        self.isDispatchedOK = True
                    except Exception, inst:
                        msg = "Couldn't send %s: %s" % (msg, inst)
                        self.logger.error(msg)


    def getMessageFrom(self):
        msgFrom = self.dictionary[SERVICE_EMAIL]
        if not msgFrom:
            domainName = self.dictionary[DOMAIN_NAME]
            msgFrom = 'kforge-noreply@%s' % domainName
        return msgFrom

    def getMessageToList(self):
        return []

    def getMessageSubject(self):
        return self.wrapMessageSubject("Service message")

    def wrapMessageSubject(self, msgSubject):
        systemName = self.dictionary[SYSTEM_NAME]
        return '[%s]: %s' % (systemName, msgSubject)

    def getMessageBody(self):
        return ""


class EmailNewPassword(EmailCommand):
        
    def __init__(self, personName):
        super(EmailNewPassword, self).__init__()
        command = dm.command.person.PersonRead(personName)
        command.execute()
        self.person = command.person

    def execute(self):
        self.newPassword = kforge.utils.password.generate()
        super(EmailNewPassword, self).execute()
        if self.isDispatchedOK:
            self.person.setPassword(self.newPassword)
            self.person.save()
            msg = "Set password for '%s', and sent notification by email." % self.person.name
            self.logger.info(msg)
        else:
            msg = "Not setting password for '%s' because notification email can not be sent." % self.person.name
            self.logger.warn(msg)

    def getMessageToList(self):
        if self.person.email:
            return [self.person.email]
        else:
            return []

    def getMessageSubject(self):
        return self.wrapMessageSubject('Your new password')

    def getMessageBody(self):
        serviceName = self.dictionary[SYSTEM_SERVICE_NAME].decode('utf-8')
        msgBody = \
'''Your new password is: %s

It is strongly recommended that you update your password when you next login.

Regards,

The %s Team
''' % (self.newPassword, serviceName)
        return msgBody


