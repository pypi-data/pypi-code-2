# code taken from collective.uploadify
# for the flashupload
# with many ameliorations

import os
import mimetypes
import random
import urllib
from Acquisition import aq_inner, aq_parent
from AccessControl import SecurityManagement
from ZPublisher.HTTPRequest import HTTPRequest

from zope.security.interfaces import Unauthorized
from zope.filerepresentation.interfaces import IFileFactory
from zope.component import getUtility

from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile 
from Products.ATContentTypes.interfaces import IImageContent
from Products.CMFPlone.interfaces import IPloneSiteRoot
from zope.app.container.interfaces import INameChooser
from plone.i18n.normalizer.interfaces import IIDNormalizer

import ticket as ticketmod
from collective.quickupload import siteMessageFactory as _
from collective.quickupload import logger
from collective.quickupload.browser.quickupload_settings import IQuickUploadControlPanel

try :
    # python 2.6
    import json
except :
    # plone 3.3
    import simplejson as json

def decodeQueryString(QueryString):
  """decode *QueryString* into a dictionary, as ZPublisher would do"""
  r= HTTPRequest(None,
		 {'QUERY_STRING' : QueryString,
		  'SERVER_URL' : '',
		  },
		 None,1)
  r.processInputs()
  return r.form 

def getDataFromAllRequests(request, dataitem) :
    """
    Sometimes data is send using POST METHOD and QUERYSTRING
    """
    data = request.form.get(dataitem, None)
    if data is None:
        # try to get data from QueryString
        data = decodeQueryString(request.get('QUERY_STRING','')).get(dataitem)
    return data    
    
def find_user(context, userid):
    """Walk up all of the possible acl_users to find the user with the
    given userid.
    """

    track = set()

    acl_users = aq_inner(getToolByName(context, 'acl_users'))
    path = '/'.join(acl_users.getPhysicalPath())
    logger.debug('Visited acl_users "%s"' % path)
    track.add(path)

    user = acl_users.getUserById(userid)
    while user is None and acl_users is not None:
        context = aq_parent(aq_parent(aq_inner(acl_users)))
        acl_users = aq_inner(getToolByName(context, 'acl_users'))
        if acl_users is not None:
            path = '/'.join(acl_users.getPhysicalPath())
            logger.debug('Visited acl_users "%s"' % path)
            if path in track:
                logger.warn('Tried searching an already visited acl_users, '
                            '"%s".  All visited are: %r' % (path, list(track)))
                break
            track.add(path)
            user = acl_users.getUserById(userid)

    if user is not None:
        user = user.__of__(acl_users)

    return user

def _listTypesForInterface(context, interface):
    """
    List of portal types that have File interface
    @param context: context
    @param interface: Zope interface
    @return: ['Image', 'News Item']
    """
    archetype_tool = getToolByName(context, 'archetype_tool')
    all_types = archetype_tool.listRegisteredTypes(inProject=True)
    # zope3 Interface
    try :
        all_types = [tipe['portal_type'] for tipe in all_types
                      if interface.implementedBy(tipe['klass'])]
    # zope2 interface
    except :
        all_types = [tipe['portal_type'] for tipe in all_types
                      if interface.isImplementedByInstancesOf(tipe['klass'])]
    return dict.fromkeys(all_types).keys() 

class QuickUploadView(BrowserView):
    """ The Quick Upload View
    """

    template = ViewPageTemplateFile("quick_upload.pt")

    def __init__(self, context, request):
        super(QuickUploadView, self).__init__(context, request)
        self.uploader_id = self._uploader_id()

    def __call__(self):
        return self.template()
    
    def header_upload(self) :
        request = self.request
        session = request.get('SESSION', {})
        medialabel = session.get('mediaupload', request.get('mediaupload', 'files'))
        if not medialabel :
            return _('Files Quick Upload')
        if medialabel == 'image' :
            return _('Images Quick Upload')
        return _('%s Quick Upload' %medialabel.capitalize())
    
    def _uploader_id(self) :
        return 'uploader%s' %str(random.random()).replace('.','')
    
    def script_content(self) :
        context = aq_inner(self.context)
        return context.restrictedTraverse('@@quick_upload_init')(for_id = self.uploader_id)


XHR_UPLOAD_JS = """       
    var fillTitles = %(ul_fill_titles)s;
    var auto = %(ul_auto_upload)s;
    addUploadFields_%(ul_id)s = function(file, id) {
        var uploader = xhr_%(ul_id)s;
        PloneQuickUpload.addUploadFields(uploader, uploader._element, file, id, fillTitles);
    }
    sendDataAndUpload_%(ul_id)s = function() {
        var uploader = xhr_%(ul_id)s;
        PloneQuickUpload.sendDataAndUpload(uploader, uploader._element, '%(typeupload)s');
    }    
    clearQueue_%(ul_id)s = function() {
        var uploader = xhr_%(ul_id)s;
        PloneQuickUpload.clearQueue(uploader, uploader._element);    
    }    
    onUploadComplete_%(ul_id)s = function(id, fileName, responseJSON) {       
        var uploader = xhr_%(ul_id)s;
        PloneQuickUpload.onUploadComplete(uploader, uploader._element, id, fileName, responseJSON);
    }
    createUploader_%(ul_id)s= function(){    
        xhr_%(ul_id)s = new qq.FileUploader({
            element: jQuery('#%(ul_id)s')[0],
            action: '%(context_url)s/@@quick_upload_file',
            autoUpload: auto,
            onAfterSelect: addUploadFields_%(ul_id)s,
            onComplete: onUploadComplete_%(ul_id)s,
            allowedExtensions: %(ul_file_extensions_list)s,
            sizeLimit: %(ul_xhr_size_limit)s,
            simUploadLimit: %(ul_sim_upload_limit)s,
            template: '<div class="qq-uploader">' +
                      '<div class="qq-upload-drop-area"><span>%(ul_draganddrop_text)s</span></div>' +
                      '<div class="qq-upload-button">%(ul_button_text)s</div>' +
                      '<ul class="qq-upload-list"></ul>' + 
                      '</div>',
            fileTemplate: '<li>' +
                    '<a class="qq-upload-cancel" href="#">&nbsp;</a>' +
                    '<div class="qq-upload-infos"><span class="qq-upload-file"></span>' +
                    '<span class="qq-upload-spinner"></span>' +
                    '<span class="qq-upload-failed-text">%(ul_msg_failed)s</span></div>' +
                    '<div class="qq-upload-size"></div>' +
                '</li>',                      
            messages: {
                serverError: "%(ul_error_server)s",
                serverErrorAlwaysExist: "%(ul_error_always_exists)s {file}",
                serverErrorZODBConflict: "%(ul_error_zodb_conflict)s {file}, %(ul_error_try_again)s",
                serverErrorNoPermission: "%(ul_error_no_permission)s",
                typeError: "%(ul_error_bad_ext)s {file}. %(ul_error_onlyallowed)s {extensions}.",
                sizeError: "%(ul_error_file_large)s {file}, %(ul_error_maxsize_is)s {sizeLimit}.",
                emptyError: "%(ul_error_empty_file)s {file}, %(ul_error_try_again_wo)s"            
            }            
        });           
    }
    jQuery(document).ready(createUploader_%(ul_id)s); 
"""        

FLASH_UPLOAD_JS = """
    var fillTitles = %(ul_fill_titles)s;
    var autoUpload = %(ul_auto_upload)s;
    clearQueue_%(ul_id)s = function() {
        jQuery('#%(ul_id)s').uploadifyClearQueue();
    }
    addUploadifyFields_%(ul_id)s = function(event, data ) {
        if (fillTitles && !autoUpload)  {
            var labelfiletitle = jQuery('#uploadify_label_file_title').val();
            jQuery('#%(ul_id)sQueue .uploadifyQueueItem').each(function() {
                ID = jQuery(this).attr('id').replace('%(ul_id)s','');
                if (!jQuery('.uploadField' ,this).length) {
                  jQuery('.cancel' ,this).after('\
                      <div class="uploadField">\
                          <label>' + labelfiletitle + ' : </label> \
                          <input type="hidden" \
                                 class="file_id_field" \
                                 name="file_id" \
                                 value ="'  + ID + '" /> \
                          <input type="text" \
                                 class="file_title_field" \
                                 id="title_' + ID + '" \
                                 name="title" \
                                 value="" />\
                      </div>\
                  ');            
                }
            });
        }
        if (!autoUpload) return showButtons_%(ul_id)s();
        return 'ok';
    }
    showButtons_%(ul_id)s = function() {
        if (jQuery('#%(ul_id)sQueue .uploadifyQueueItem').length) {
            jQuery('.uploadifybuttons').show();
            return 'ok';
        }
        return false;
    }
    sendDataAndUpload_%(ul_id)s = function() {
        QueueItems = jQuery('#%(ul_id)sQueue .uploadifyQueueItem');
        nbItems = QueueItems.length;
        QueueItems.each(function(i){
            filesData = {};
            ID = jQuery('.file_id_field',this).val();
            if (fillTitles && !autoUpload) {
                filesData['title'] = jQuery('.file_title_field',this).val();
            }
            jQuery('#%(ul_id)s').uploadifySettings('scriptData', filesData);     
            jQuery('#%(ul_id)s').uploadifyUpload(ID);       
        })
    }
    onAllUploadsComplete_%(ul_id)s = function(event, data){
        if (!data.errors) {
           Browser.onUploadComplete();
        }
        else {
           msg= data.filesUploaded + '%(ul_msg_some_sucess)s' + data.errors + '%(ul_msg_some_errors)s';
           alert(msg);
        }
    }
    jQuery(document).ready(function() {
        jQuery('#%(ul_id)s').uploadify({
            'uploader'      : '%(portal_url)s/++resource++quickupload_static/uploader.swf',
            'script'        : '%(context_url)s/@@flash_upload_file',
            'cancelImg'     : '%(portal_url)s/++resource++quickupload_static/cancel.png',
            'folder'        : '%(physical_path)s',
            'onAllComplete' : onAllUploadsComplete_%(ul_id)s,
            'auto'          : autoUpload,
            'multi'         : true,
            'simUploadLimit': %(ul_sim_upload_limit)s,
            'sizeLimit'     : '%(ul_size_limit)s',
            'fileDesc'      : '%(ul_file_description)s',
            'fileExt'       : '%(ul_file_extensions)s',
            'buttonText'    : '%(ul_button_text)s',
            'scriptAccess'  : 'sameDomain',
            'hideButton'    : false,
            'onSelectOnce'  : addUploadifyFields_%(ul_id)s,
            'scriptData'    : {'ticket' : '%(ticket)s', 'typeupload' : '%(typeupload)s'}
        });
    });
"""

        
class QuickUploadInit(BrowserView):
    """ Initialize uploadify js
    """

    def __init__(self, context, request):
        super(QuickUploadInit, self).__init__(context, request)
        self.context = aq_inner(context)
        portal = getUtility(IPloneSiteRoot)
        self.qup_prefs = IQuickUploadControlPanel(portal)

    def ul_content_types_infos (self, mediaupload):
        """
        return some content types infos depending on mediaupload type
        mediaupload could be 'image', 'video', 'audio' or any
        extension like '*.doc'
        """
        context = aq_inner(self.context)
        ext = '*.*;'
        extlist = []
        msg = u'Choose files to upload'
        if mediaupload == 'image' :
            ext = '*.jpg;*.jpeg;*.gif;*.png;'
            msg = u'Choose images to upload'
        elif mediaupload == 'video' :
            ext = '*.flv;*.avi;*.wmv;*.mpg;'
            msg = u'Choose video files to upload'
        elif mediaupload == 'audio' :
            ext = '*.mp3;*.wav;*.ogg;*.mp4;*.wma;*.aif;'
            msg = u'Choose audio files to upload'
        elif mediaupload == 'flash' :
            ext = '*.swf;'
            msg = u'Choose flash files to upload'
        elif mediaupload :
            # you can also pass a list of extensions in mediaupload request var
            # with this syntax '*.aaa;*.bbb;'
            ext = mediaupload 
            msg = u'Choose file for upload : ' + ext 
        
        try :
            extlist = [f.split('.')[1].strip() for f in ext.split(';') if f.strip()]
        except :
            extlist = []
        if extlist==['*'] :
            extlist = []
        
        return ( ext, extlist, self._utranslate(msg))
    
    def _utranslate(self, msg):
        # XXX fixme : the _ (SiteMessageFactory) doesn't work
        context = aq_inner(self.context)
        return context.translate(msg, domain="collective.quickupload")

    def upload_settings(self):
        context = aq_inner(self.context)
        request = self.request
        session = request.get('SESSION', {})
        portal_url = getToolByName(context, 'portal_url')()    
        # use a ticket for authentication (used for flashupload only)
        ticket = context.restrictedTraverse('@@quickupload_ticket')()
        
        settings = dict(
            ticket                 = ticket,
            portal_url             = portal_url,
            typeupload             = '',
            context_url            = context.absolute_url(),
            physical_path          = "/".join(context.getPhysicalPath()),
            ul_id                  = self.uploader_id,
            ul_fill_titles         = self.qup_prefs.fill_titles and 'true' or 'false',
            ul_auto_upload         = self.qup_prefs.auto_upload and 'true' or 'false',
            ul_size_limit          = self.qup_prefs.size_limit and str(self.qup_prefs.size_limit*1024) or '',
            ul_xhr_size_limit      = self.qup_prefs.size_limit and str(self.qup_prefs.size_limit*1024) or '0',
            ul_sim_upload_limit    = str(self.qup_prefs.sim_upload_limit),
            ul_button_text         = self._utranslate(u'Browse'),
            ul_draganddrop_text    = self._utranslate(u'Drag and drop files to upload'),
            ul_msg_all_sucess      = self._utranslate( u'All files uploaded with success.'),
            ul_msg_some_sucess     = self._utranslate( u' files uploaded with success, '),
            ul_msg_some_errors     = self._utranslate( u" uploads return an error."),
            ul_msg_failed          = self._utranslate( u"Failed"),
            ul_error_try_again_wo  = self._utranslate( u"please select files again without it."),
            ul_error_try_again     = self._utranslate( u"please try again."),
            ul_error_empty_file    = self._utranslate( u"This file is empty :"),
            ul_error_file_large    = self._utranslate( u"This file is too large :"),
            ul_error_maxsize_is    = self._utranslate( u"maximum file size is :"),
            ul_error_bad_ext       = self._utranslate( u"This file has invalid extension :"),
            ul_error_onlyallowed   = self._utranslate( u"Only allowed :"),
            ul_error_no_permission = self._utranslate( u"You don't have permission to add this content in this place."),
            ul_error_always_exists = self._utranslate( u"This file always exists with the same name on server :"),
            ul_error_zodb_conflict = self._utranslate( u"A data base conflict error happened when uploading this file :"),
            ul_error_server        = self._utranslate( u"Server error, please contact support and/or try again."),
        )        
        
        mediaupload = session.get('mediaupload', request.get('mediaupload', ''))  
        typeupload = session.get('typeupload', request.get('typeupload', ''))
        settings['typeupload'] = typeupload
        if mediaupload :
            ul_content_types_infos = self.ul_content_types_infos(mediaupload)
        elif typeupload :
            imageTypes = _listTypesForInterface(context, IImageContent)
            if typeupload in imageTypes :
                ul_content_types_infos = self.ul_content_types_infos('image')
        else :
            ul_content_types_infos = ('*.*;', [], '')
        
        settings['ul_file_extensions'] = ul_content_types_infos[0]
        settings['ul_file_extensions_list'] = str(ul_content_types_infos[1])
        settings['ul_file_description'] = ul_content_types_infos[2]
            
        return settings

    def __call__(self, for_id="uploader"):
        self.uploader_id = for_id
        settings = self.upload_settings()
        if self.qup_prefs.use_flashupload :
            return FLASH_UPLOAD_JS % settings     
        return XHR_UPLOAD_JS % settings   
        

class QuickUploadAuthenticate(BrowserView):
    """
    base view for quick upload authentication
    ticket is used only with flash upload
    nothing is done with xhr upload.
    Note : we don't use the collective.uploadify method
    for authentication because sending cookie in all requests
    is not secure.
    """
    def __init__(self, context, request):        
        self.context = context
        self.request = request     
        portal = getUtility(IPloneSiteRoot)
        self.qup_prefs = IQuickUploadControlPanel(portal)
        self.use_flashupload = self.qup_prefs.use_flashupload
            
    def _auth_with_ticket (self):
        """
        with flashupload authentication is done using a ticket
        """
        
        context = aq_inner(self.context)
        request = self.request
        url = context.absolute_url()

        ticket = getDataFromAllRequests(request, 'ticket')  
        if ticket is None:
            raise Unauthorized('No ticket specified')        
        
        logger.info('Authenticate using ticket, the ticket is "%s"' % str(ticket)) 
        username = ticketmod.ticketOwner(url, ticket)
        if username is None:
            logger.info('Ticket "%s" was invalidated, cannot be used '
                        'any more.' % str(ticket))
            raise Unauthorized('Ticket is not valid')

        self.old_sm = SecurityManagement.getSecurityManager()
        user = find_user(context, username)
        SecurityManagement.newSecurityManager(self.request, user)
        logger.info('Switched to user "%s"' % username)   

        
class QuickUploadFile(QuickUploadAuthenticate):
    """ Upload a file
    """  
    
    def __call__(self):
        """
        """        
        if self.use_flashupload :
            return self.flash_upload_file()  
        return self.quick_upload_file()
                            
    def flash_upload_file(self) :
        
        context = aq_inner(self.context)
        request = self.request        
        self._auth_with_ticket()         
            
        file_name = request.form.get("Filename", "")
        file_data = request.form.get("Filedata", None)
        content_type = mimetypes.guess_type(file_name)[0]
        portal_type = request.form.get('typeupload', '')
        title =  request.form.get("title", None)
        
        if not portal_type :
            ctr = getToolByName(context, 'content_type_registry')
            portal_type = ctr.findTypeName(file_name.lower(), '', '') or 'File'
        
        if file_data:
            factory = IFileFactory(context)
            logger.info("uploading file with flash: filename=%s, title=%s, content_type=%s, portal_type=%s" % \
                    (file_name, title, content_type, portal_type))                             
            
            try :
                f = factory(file_name, title, content_type, file_data, portal_type)
            except :
                # XXX todo : improve errors handlers for flashupload
                raise
            if f['success'] is not None :
                o = f['success']
                logger.info("file url: %s" % o.absolute_url())
                SecurityManagement.setSecurityManager(self.old_sm)   
                return o.absolute_url()         

    def quick_upload_file(self) :
        
        context = aq_inner(self.context)
        request = self.request
        response = request.RESPONSE      
        
        response.setHeader('Expires', 'Sat, 1 Jan 2000 00:00:00 GMT')
        response.setHeader('Cache-control', 'no-cache') 
        # the good content type woul be text/json or text/plain but IE 
        # do not support it
        response.setHeader('Content-Type', 'text/html; charset=utf-8')               

        if request.HTTP_X_REQUESTED_WITH :
            # using ajax upload
            try :
                file_data = request.BODY
            except :
                # in case of cancel during xhr upload
                logger.info("An upload has been aborted")
                # not really useful here since the upload block
                # is removed by "cancel" action, but
                # could be useful if someone change the js behavior
                return  json.dumps({u'error': u'emptyError'})
            file_name = urllib.unquote(request.HTTP_X_FILE_NAME)       
            upload_with = "XHR"
        else :
            # using classic form post method (MSIE<=8)
            file_data = request.get("qqfile", None)
            filename = getattr(file_data,'filename', '')
            file_name = filename.split("\\")[-1]  
            upload_with = "CLASSIC FORM POST"
            # we must test the file size in this case (no client test)
            if not self._check_file_size(file_data) :
                logger.info("Test file size : the file %s is too big, upload rejected" % file_name) 
                return json.dumps({u'error': u'sizeError'})


        if not self._check_file_id(file_name) :
            logger.info("The file id for %s always exist, upload rejected" % file_name)
            return json.dumps({u'error': u'serverErrorAlwaysExist'})

        content_type = mimetypes.guess_type(file_name)[0]
        portal_type = getDataFromAllRequests(request, 'typeupload') or ''
        title =  getDataFromAllRequests(request, 'title') or ''
        
        if not portal_type :
            ctr = getToolByName(context, 'content_type_registry')
            portal_type = ctr.findTypeName(file_name.lower(), '', '') or 'File'
        
        if file_data:
            factory = IFileFactory(context)
            logger.info("uploading file with %s : filename=%s, title=%s, content_type=%s, portal_type=%s" % \
                    (upload_with, file_name, title, content_type, portal_type))                             
            
            try :
                f = factory(file_name, title, content_type, file_data, portal_type)
            except :
                return json.dumps({u'error': u'serverError'})
            
            if f['success'] is not None :
                o = f['success']
                logger.info("file url: %s" % o.absolute_url()) 
                msg = {u'success': True}
            else :
                msg = {u'error': f['error']}
        else :
            msg = {u'error': u'emptyError'}
            
        return json.dumps(msg)          
        
    def _check_file_size(self, data):
        max_size = int(self.qup_prefs.size_limit)
        if not max_size :
            return 1
        #file_size = len(data.read()) / 1024
        data.seek(0, os.SEEK_END)
        file_size = data.tell() / 1024
        data.seek(0, os.SEEK_SET )
        max_size = int(self.qup_prefs.size_limit)
        if file_size<=max_size:
            return 1
        return 0    
    
    def _check_file_id(self, id):
        context = aq_inner(self.context)
        charset = context.getCharset()
        id = id.decode(charset)
        normalizer = getUtility(IIDNormalizer)
        chooser = INameChooser(context)
        newid = chooser.chooseName(normalizer.normalize(id), self.context.aq_parent)
        if newid in context.objectIds() :
            return 0
        return 1

class QuickUploadCheckFile(BrowserView):
    """
    check if file exists
    """
     

    def quick_upload_check_file(self) :
        
        context = aq_inner(self.context)
        request = self.request          
        url = context.absolute_url()       
        
        always_exist = {}
        formdict = request.form
        ids = context.objectIds()
        
        for k,v in formdict.items():
            if k!='folder' :
                if v in ids :
                    always_exist[k] = v
        
        return str(always_exist)
    
    
    def __call__(self):
        """
        """        
        return self.quick_upload_check_file()  
        
                             