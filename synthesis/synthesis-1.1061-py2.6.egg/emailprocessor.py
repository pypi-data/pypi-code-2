
from smtplibrary import smtpInterface
from conf import settings
import os
from clssecurity import ClsSecurity

class XMLProcessorNotifier(smtpInterface):
    # adding encyrption switch.  emailed sensitive data must be encrypted.
    def __init__(self, docName, docs=[], encrypt=False):
        # turn on encryption switch
        if encrypt:
            self.encrypt = encrypt
            self.security = ClsSecurity()
        
        self.mailSystem = smtpInterface(settings)
        if docName <> '':
            folderName = os.path.split(docName)[0]
            self.mailSystem.setRecipients(settings.SMTPRECIPIENTS[folderName])
            self.docName = docName
        else:
            if len(docs) > 0:
                # first file dictates where this is going, mostly files will be in the output location.
                try:
                    folderName = os.path.split(docs[0])[0]
                    self.mailSystem.setRecipients(settings.SMTPRECIPIENTS[folderName])
                except KeyError:
                    raise
            

    def sendDocumentAttachment(self, Subject='Your Message Subject', Message='Message Body goes here.', attachment=None):
        self.mailSystem.setMessageSubject(Subject)
        self.mailSystem.setMessage(Message)
        self.mailSystem.formatMessage()
        for file in attachment:
            if self.encrypt:
                attachment = 'encryptdAttachment.enc'
                # FIXME encrypt the file before attaching.
                self.security.encryptFile(file, attachment)
                
            else:
                attachment = file
            
            print 'file: %s' % file
            self.mailSystem.setAttachmentText(attachment)
        try:
            self.sendMessage()
        except Exception, detail:
            if settings.DEBUG:
                print "problem sending notification", detail.value
            return
        
    def notifyValidationFailure(self, failureMsgs=''):
        self.mailSystem.setMessageSubject('XMLDocument FAILED Validation')
        self.mailSystem.setMessage('This email is a notification that we received XML document: %s.  \r\n' \
                                   'This Document FAILED to Validate properly.\r\n ' \
                                   'Error is: %s' % (self.docName, failureMsgs))
        try:
            self.sendMessage()
        except Exception, detail:
            if settings.DEBUG:
                print "problem sending notification", detail.value
            return
        
    def notifyDuplicateDocumentError(self, failureMsgs=''):
        self.mailSystem.setMessageSubject('XMLDocument Process Import FAILED')
        self.mailSystem.setMessage('This email is a notification that we received XML document: %s.  \r\n' \
                                   'This Document FAILED to import because it would create duplicate records in the database.\r\n ' \
                                   'Error is: %s' % (self.docName, failureMsgs))
        try:
            self.sendMessage()
        except Exception, detail:
            if settings.DEBUG:
                print "problem sending notification", detail.value
            return
        
    
    def notifyValidationSuccess(self):
        self.mailSystem.setMessageSubject('Success: XMLDocument PASSED Validation')
        self.mailSystem.setMessage('This email is a notification that we received XML document: %s.  This Document PASSED Validation proprerly.' % self.docName)
        try:
            self.sendMessage()
        except Exception, detail:
            if settings.DEBUG:
                print "problem sending notification", detail.value
            return
    
    def sendMessage(self):
        #self.mailSystem.formatMessage()
        #mailSystem.setAttachmentText(os.path.join(smtp.settings.BASE_PATH, 'emailprocessor.py'))
        try:
            self.mailSystem.sendMessage()
        except Exception, detail:
            if settings.DEBUG:
                print "problem sending notification through mail system", detail.value
            return

if __name__ == '__main__':
    
    
    msgBody = "Test Msg"
    filesToTransfer = ['/home/user/Documents/Development/AlexandriaConsulting/repos/trunk/synthesis/OutputFiles/page.xml']
    email = XMLProcessorNotifier("", filesToTransfer, True)
    email.sendDocumentAttachment('Your report results', msgBody, filesToTransfer)
    