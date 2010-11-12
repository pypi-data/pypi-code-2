from AccessControl import ClassSecurityInfo, getSecurityManager
from AccessControl.SecurityManagement import newSecurityManager, \
    setSecurityManager
from Products.ATContentTypes.content.document import ATDocument
from Products.ATContentTypes.content.event import ATEvent
from Products.ATContentTypes.content.newsitem import ATNewsItem
from Products.Archetypes.utils import shasattr
from Products.CMFCore.utils import getToolByName
from collective.validator.base.browser.adapter import Parser
from collective.validator.base.config import *
from collective.validator.base.interfaces.interfaces import *
from collective.validator.xhtmlStrict.interfaces import *
from urllib import urlencode, urlopen
from zope.component import adapts, getMultiAdapter
from zope.component.interfaces import ComponentLookupError
from zope.interface import implements, alsoProvides
from zope.publisher.browser import TestRequest
import tempfile
import time
import urllib2

basic_atct = (ATDocument,ATEvent,ATNewsItem)

class W3cStrict(Parser):

    security = ClassSecurityInfo()

    implements(IW3cStrict)
    adapts(IVTPlone)


    def __init__(self, context):
        Parser.__init__(self,context)
        self.val_url = context.getValidatorUrl()
        self.val_type = 'XHTML 1.0 Strict'
        self.val_sleep = context.getValidatorSleep() 

    security.declarePrivate('getValidationResults')
    def getValidationResults(self, xhtml):
        """Returned structure:
        {'m:errors':{
                     'm:errorcount':2,
                     'm:errorlist':[
                                    {
                                     'm:line':1,
                                     'm:col':2,
                                     'm:message':'err message',
                                    },
                                    ...
                                   ],
                    },
        'm:warnings':{
                      'm:warningcount':1,
                      'm:warninglist':[
                                       {
                                        'm:line':1,
                                        'm:col':2,
                                        'm:message':'warn message',
                                       },
                                       ...
                                      ],
                      },
        'm:validity':true,
        }
        """     
        values = {'fragment': xhtml,
                  'verbose':'1',
                  'doctype':self.val_type, 
                  'output':'soap12'}
        params = urlencode(values)

        if self.context.getProxyAddress() and self.context.getProxyPassword() and self.context.getProxyUserid() and self.context.getProxyPort():
            proxy_info = {
                          'user' : self.context.getProxyUserid(),
                          'pass' : self.context.getProxyPassword(),
                          'host' : self.context.getProxyAddress(),
                          'port' : int(self.context.getProxyPort())
                          }
            # build a new opener that uses a proxy requiring authorization
            proxy_support = urllib2.ProxyHandler({"http" :"http://%(user)s:%(pass)s@%(host)s:%(port)d" % proxy_info})
            opener = urllib2.build_opener(proxy_support, urllib2.HTTPHandler)
            
            # install it
            urllib2.install_opener(opener)
        try:
            f = urllib2.urlopen(self.val_url, params)
        except IOError,e:
            logger.validator_error('Problem with %s. Retrying in 5 seconds' %self.val_url)
            err = True
            for i in range(0,5):
                try:
                    logger.validator_error("Retrying (attempt %s of 5) in 5 seconds" % (i+1))
                    if self.val_sleep:
                        time.sleep(self.val_sleep)
                    f = urllib2.urlopen(self.val_url, params)
                    logger.validator_info("Connection ok")
                    err = False
                    break
                except IOError:
                    logger.exception("Error again")
            if err:
                return self.createResult(error=True,resp=e)
        return self.createResult(resp=f.read())

    security.declareProtected(USE_VALIDATION_PERMISSION, 'runValidation')
    def runValidation(self):
        """Validate a site"""
        plone_utils = getToolByName(self.context,'plone_utils')
        pm = getToolByName(self.context,'portal_membership')
        old_security_manager= getSecurityManager()
        if self.context.getAnonymousValidation() and not pm.isAnonymousUser():
            setSecurityManager(None)
        results = self.search()
        setSecurityManager(old_security_manager)

        fileout=tempfile.TemporaryFile()
        toterr = totwarn = nerr = nwarn = 0
        valid = True
        try:
            log_path = logger.handlers[0].baseFilename
            logger.info('Starting validation. The complete log is stored in "%s"' %log_path)
        except IndexError:
            logger.info('Starting validation. The complete log will be insert into the instance log.')
        for i,brain in enumerate(results):
            logger.validator_info('Validating document "%s" (%d of %d)'%(brain.getPath(),i+1,len(results)))
            obj = brain.getObject()
            if self.context.getAnonymousValidation() and not pm.isAnonymousUser():
                setSecurityManager(None)
            if shasattr(obj,'view'):
                validation = self.getValidationResults(obj.view().encode('utf-8'))
            else:
                try:
                    request = TestRequest()
                    view=getMultiAdapter((obj,request),'view')
                except ComponentLookupError:
                    try:
                        view = obj()
                    except:
                        view= obj.unrestrictedTraverse('base_view')()
            setSecurityManager(old_security_manager)
            
            validation=self.getValidationResults(view.encode('utf-8'))
            partialReport, nerr, nwarn, valid_next = self.createReportPage(validation, obj.Title(), obj.absolute_url())
            fileout.write(partialReport)
            toterr+=nerr
            totwarn+=nwarn
            valid &=valid_next
            if self.val_sleep:
                time.sleep(self.val_sleep)
        
        fileout.seek(0)    
        report_text=fileout.read()
        id_report=''
        if self.context.getCreateReport() or self.context.getCreateReportText():
            id_report = self.createReportDocument(report_text,toterr,totwarn,len(results),valid)
        
        #if email fields are set, send the report
        if self.context.getSendReport() and self.context.getEmailAddresses():
            self.sendReportAsAttach(self.createReportMail(report_text,toterr, totwarn,len(results)),("portal-validation-report",".html"))

        # try to do the 'hide' action; default plone workflow make visible contents accessible
#        wtool = getToolByName(self.context,'portal_workflow')
#        try:
#            wtool.doActionFor(f, 'hide')
#        except:
#            pass
        
        if not id_report:
            msg_type='error'
            msg="Validation failed"
        else:
            params ={'domain':'collective.validator.xhtmlStrict',
                     'msgid':'strict_portal_message',
                     'default':'generated',
                     'context':self.context}
            generated=self.translation_service.utranslate(**params)
            msg = ("<a href='portal_validationtool/%s'>report</a> %s %s" %(id_report,
                                                                           self.val_type,
                                                                           generated))
            msg_type='info'
        
        getattr(logger,msg_type)('report %s %s' %(self.val_type, generated))
        plone_utils.addPortalMessage(msg,msg_type)
        
        
       
    security.declareProtected(USE_VALIDATION_PERMISSION, 'runValidation')
    def runDebugValidation(self):
        """Validate other view of content types selected"""
        plone_utils = self.context.plone_utils
        portal = self.context.portal_url.getPortalObject()
        portal_types = self.context.getDebugTypesList()
        if not portal_types: return
        fileout = tempfile.TemporaryFile()
        viewscount = 0
        toterr = totwarn = 0
        for type_name in portal_types:
            tmpid = portal.generateUniqueId(type_name)
            tmpobject = portal.restrictedTraverse('portal_factory/%s/%s' % (type_name, tmpid))
            tmpobject = self.setBaseType(tmpobject)        
            adapted = IValidable(tmpobject)
            validation_report_list = adapted.isValid()
            viewscount+= len(validation_report_list)
            valid = True
            for report in validation_report_list:
                nerr = nwarn = 0
                partialReport, nerr, nwarn, valid_next = self.createReportPage(report[1], tmpobject.title_or_id(), tmpobject.absolute_url()+"/"+report[0])
                fileout.write(partialReport)
                toterr+=nerr
                totwarn+=nwarn
                valid &= valid_next
                if self.val_sleep:
                    time.sleep(self.val_sleep)  
        id_report = self.createDebugReportDocument(fileout,toterr,totwarn,viewscount,valid)

        # try to do the 'hide' action; default plone workflow make visible contents accessible
        
        
        if self.context.getSendReportDebug() and self.context.getEmailAddressesDebug():
            self.sendReportAsAttach(fileout,("portal-validation-report",".html"))
        
        str = "<a href='portal_validationtool/%s'>report</a> %s debug " %(id_report,self.val_type)
        str += self.translation_service.utranslate( \
                                           domain='collective.validator.xhtmlStrict', \
                                           msgid='strict_portal_message', \
                                           default="generated", \
                                           context=self.context)
        plone_utils.addPortalMessage(str)
        
    security.declarePrivate('setBaseType')
    def setBaseType(self, tmpobject):
        """if the object is in one of the basic content types set for it the IBaseValidableType
        interface. In other case do nothing...
        """
        for t in tmpobject.__class__.__bases__+(tmpobject.__class__,):
            if t in basic_atct:
                alsoProvides(tmpobject, IBaseValidationType)
                return tmpobject
        return tmpobject
