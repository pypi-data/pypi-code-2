import Acquisition
import logging
from zope.formlib import form
try:
    from five.formlib import formbase
except ImportError:
    from Products.Five.formlib import formbase
from Products.PloneFlashUpload import interfaces
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.PloneFlashUpload import ticket as ticketmod
from Products.PloneFlashUpload import utils
from Products.CMFCore import utils as cmfutils
from zope import event
from z3c.widgets.flashupload import upload
from z3c.widgets.flashupload.interfaces import FlashUploadedEvent
from zope.traversing.browser.absoluteurl import absoluteURL
from zope.security.interfaces import Unauthorized
from AccessControl import SecurityManagement
from zope.filerepresentation.interfaces import IFileFactory

logger = logging.getLogger('PloneFlashUpload')
logger.level = logging.getLogger().level


class UploadForm(BrowserView, upload.UploadForm):
    """displays the swf for uploading files
    """

    template = ViewPageTemplateFile('uploadform.pt')

    def upload_action(self):
        """Location for uploading.
        """

        settings = interfaces.IFlashUploadSettings(self.context)
        return settings.completion_url

    def __call__(self):
        return self.template(template_id='flashupload')


class FlashUploadVars(BrowserView, upload.FlashUploadVars):
    """simple view for the flashupload.pt
    to configure the flash upload swf"""

    allowedFileTypes = () # empty means everything


class UploadFile(BrowserView, upload.UploadFile):
    """handles file upload for the flash client.
    flash client sends the data via post as u'Filedata'
    the filename gets sent as: u'Filename'
    """

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        ticket = self.request.form.get('ticket',None)
        if ticket is None:
            # we cannot set post headers in flash, so get the
            # querystring manually
            qs = self.request.get('QUERY_STRING','ticket=')
            ticket = qs.split('=')[-1] or None

        logger.debug('Ticket being used is "%s"' % str(ticket))

        if ticket is None:
            raise Unauthorized('No ticket specified')

        context = utils.non_view_context(self.context)
        url = absoluteURL(context, self.request)
        username = ticketmod.ticketOwner(url, ticket)
        if username is None:
            logger.warn('Ticket "%s" was invalidated, cannot be used '
                        'any more.' % str(ticket))
            raise Unauthorized('Ticket is not valid')

        old_sm = SecurityManagement.getSecurityManager()
        user = utils.find_user(context, username)
        SecurityManagement.newSecurityManager(self.request, user)
        logger.debug('Switched to user "%s"' % username)

        ticketmod.invalidateTicket(url,ticket)
        if self.request.form.get('Filedata', None) is None:
            # flash sends a emtpy form in a pre request in flash version 8.0
            return ""
        fileUpload = self.request.form['Filedata']
        fileName = self.request.form['Filename']
        contentType = self.request.form.get('Content-Type',None)
        factory = IFileFactory(self.context)
        f = factory(fileName, contentType, fileUpload, request=self.request)

        event.notify(FlashUploadedEvent(f))
        result = "filename=%s" %f.getId()

        SecurityManagement.setSecurityManager(old_sm)

        return result


class Configlet(formbase.EditForm):
    """A view for configuring flash upload settings.
    """

    label = u'Plone Flash Upload Configuration'
    form_name = u'Settings'

    template = ViewPageTemplateFile('configlet.pt')
    form_fields = form.FormFields(interfaces.IFlashUploadSettings)


class DisplayUploadView(BrowserView):
    """Returns True or False depending on whether the upload tab is allowed
    to be displayed on the current context.
    """

    def allowed_types(self):
        return [x.getId() for x in self.context.getAllowedTypes()]

    def can_upload(self):
        context = Acquisition.aq_inner(self.context)

        if not context.displayContentsTab():
            return False

        pu = cmfutils.getToolByName(context, 'portal_url')
        portal = pu.getPortalObject()
        settings = interfaces.IFlashUploadSettings(portal)

        # make sure the currently allowed addable types to the folderish
        # context contains at least one of the items defined in
        # IFlashUploadSettings.valid_types

        allowed = set(self.allowed_types())
        valid_types = settings.valid_types.split('\n')
        can_upload = set(valid_types)
        if len(allowed.intersection(can_upload)) == 0:
            return False

        obj = context
        if context.restrictedTraverse('@@plone').isDefaultPageInFolder():
            obj = Acquisition.aq_parent(Acquisition.aq_inner(obj))

        return interfaces.IUploadingCapable.providedBy(obj)

    def upload_url(self):
        context = Acquisition.aq_inner(self.context)
        if context.restrictedTraverse('@@plone').isStructuralFolder():
            url = context.absolute_url()
        else:
            url = Acquisition.aq_parent(context).absolute_url()
        return url + '/flashupload'


class SuccessView(object):

    def upload_contents(self):
        """Return list of files uploaded for use in folder_listing macro.
        """
        filename = self.request.get('filename')
        context = utils.non_view_context(self.context)
        return [context[filename]]


class UploadInit(BrowserView):

    def __call__(self):
        context = utils.non_view_context(self.context)

        sp = cmfutils.getToolByName(context, "portal_properties").site_properties
        settings = dict(
                    portal_url = cmfutils.getToolByName(context, 'portal_url')(),
                    url = absoluteURL(context, self.request),
                    debug = 'false',
                    file_size_limit = sp.getProperty('pfu_file_size_limit', '100 MB'),
                    )
        return """
var swfu;
jq( function() {
    var settings = {
        flash_url : "%(portal_url)s/++resource++swfupload/swfupload.swf",
        upload_url: "%(url)s/uploadfile",
        file_size_limit : "%(file_size_limit)s",
        file_types : "*.*",
        file_types_description : "All Files",
        file_upload_limit : 100,
        file_queue_limit : 0,
        custom_settings : {
            progressTarget : "fsUploadProgress",
            cancelButtonId : "btnCancel"
        },
        debug: %(debug)s,

        // Button settings
        button_width: jq("#btnUpload").outerWidth(),
        button_height: jq("#btnUpload").outerHeight(),
        button_placeholder_id: "flashuploadtarget",
        button_window_mode: SWFUpload.WINDOW_MODE.TRANSPARENT,
        button_cursor: SWFUpload.CURSOR.HAND,

        // The event handler functions are defined in handlers.js
        file_queued_handler : fileQueued,
        file_queue_error_handler : fileQueueError,
        file_dialog_complete_handler : fileDialogComplete,
        upload_start_handler : uploadStartPlone,
        upload_progress_handler : uploadProgress,
        upload_error_handler : uploadError,
        upload_success_handler : uploadSuccessPlone,
        upload_complete_handler : uploadComplete,
        queue_complete_handler : queueComplete // Queue plugin event
    };
    swfu = new SWFUpload(settings);
});

function uploadStartPlone(file) {
    swfu.setPostParams({
        "ticket": jq.ajax({
              url: swfu.settings.upload_url+"/ticket",
              cache: false,
              async: false
              }).responseText});
    return uploadStart(file);
}

function uploadSuccessPlone(file, serverData) {
    try {
        jq.ajax({
          url: swfu.settings.upload_url+"/success?"+serverData,
          cache: false,
          success: function(html){
              jq(".upload-folder-listing dl").append(jq(".upload-folder-listing dl > *", html));
          }
        });
        var progress = new FileProgress(file, this.customSettings.progressTarget);
        progress.setComplete();
        progress.setStatus("Complete.");
        progress.toggleCancel(false);
    } catch (ex) {
        this.debug(ex);
    }
}

""" % settings
