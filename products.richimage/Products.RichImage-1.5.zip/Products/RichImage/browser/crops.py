from Products.Five.browser import BrowserView
from Products.statusmessages.interfaces import IStatusMessage
from Products.RichImage import RichImageMessageFactory as _

class EditCrop(BrowserView):
    """
    """

    def __call__(self):
        content = self.context
        request = self.request

        field = content.getField('image')

        field.editCrop(content,
                      request.crop,
                      request.x1,
                      request.y1,
                      request.x2,
                      request.y2,
                      scale = request.cropScale,
                      forced_size = True,
                      )

        # Issue a status message
        confirm = _(u"Crop saved")
        IStatusMessage(self.request).addStatusMessage(confirm, type='info')

        dest = request.get('last_referer', content.absolute_url())
        return request.response.redirect(dest)
