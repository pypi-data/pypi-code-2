from tw.api import Widget, JSLink, CSSLink, js_function, Link
from tw.jquery import jquery_js

from tw.forms import FileField

__all__ = ["Uploadify"]

uploadify_css = CSSLink(modname=__name__,
                        filename="static/css/uploadify.css")

uploadify = JSLink(modname=__name__,
               filename='static/js/jquery.uploadify.v2.1.4.min.js',
               css = [uploadify_css,],
               javascript = [jquery_js,],)

swfobject = JSLink(modname=__name__,
               filename='static/js/swfobject.js',
               )


flash_uploadify = Link(modname=__name__,
                filename='static/swf/uploadify.swf')
flash_install = Link(modname=__name__,
                filename='static/swf/expressInstall.swf')

cancel_img = Link(modname=__name__,
                filename='static/images/cancel.png')


class Uploadify(FileField):

    javascript = [uploadify, swfobject]
    css = [uploadify_css,]

    # all available options: http://www.uploadify.com/documentation/
    params = {
           "auto" : "Automatically upload files as they are added to the queue.",
           "buttonText" : "The text that appears on the default button.",
           "cancelImg" : "The path to an image you would like to use as the cancel button.",
           "expressInstall" : "The path to the expressInstall.swf file.",
           "fileDataName" : "The name of your files array in the back-end script.",
           "fileDesc" : "The text that will appear in the file type drop down at the bottom of the browse dialog box.",
           "fileExt" : "A list of file extensions that are allowed for upload.",
           "multi": "The multi option allows the user to add multiple files to the queue for upload.",
           "removeCompleted" : "Enable automatic removal of the queue item for completed uploads.",
           "script": "Tells us where to get the data.",
           "scriptAccess": "The scriptAccess option sets the scriptAccess property for the flash button file.",
           "scriptData" : "An object containing name/value pairs with additional information that should be sent to the back-end script when processing a file upload.",
           "uploader" : "The path to the uploadify.swf file.",
           }

    #defaults
    auto = True
    buttonText = 'SELECT FILES'
    cancelImg = cancel_img.link
    expressInstall = flash_install.link
    fileDataName = "Filedata"
    fileDesc = None # "Document Files (.DOC, .ODT, .PDF)"
    fileExt = None # "*.doc;*.odt;*.pdf"
    multi = False
    removeCompleted = True
    scriptAccess = "sameDomain" # or always
    scriptData = {}
    uploader = flash_uploadify.link


    def __init__(self, id=None, parent=None, children=[], **kw):
        super(Uploadify, self).__init__(id, parent, children, **kw)
        if not kw.get("script", False):
            raise ValueError, "Uploadify must have script for sending files"

    def update_params(self, d):
        """This method is called every time the widget is displayed. It's task
        is to prepare all variables that are sent to the template. Those
        variables can accessed as attributes of d."""
        super(Uploadify, self).update_params(d)
        upload_params = dict(
                auto=d.auto,
                buttonText=d.buttonText,
                cancelImg=d.cancelImg,
                expressInstall=d.expressInstall,
                fileDataName=d.fileDataName,
                fileDesc=d.fileDesc,
                fileExt=d.fileExt,
                multi=d.multi,
                removeCompleted=d.removeCompleted,
                script=d.script,
                scriptAccess=d.scriptAccess,
                scriptData=d.scriptData,
                uploader=d.uploader,
                             )
        call = js_function('$("#%s").uploadify' % d.id)(upload_params)
        self.add_call(call)