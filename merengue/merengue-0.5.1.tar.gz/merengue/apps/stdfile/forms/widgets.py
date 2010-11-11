from django import forms
from django.conf import settings
from django.utils.translation import ugettext as _


class DeleteCheckboxWidget(forms.CheckboxInput):

    def __init__(self, *args, **kwargs):
        self.is_image = kwargs.pop('is_image')
        self.value = kwargs.pop('initial')
        super(DeleteCheckboxWidget, self).__init__(*args, **kwargs)

    def render(self, name, value, attrs=None):
        value = value or self.value
        if value:
            s = u'<table style="border-style:none;margin-left:9em;" class="DeleteCheckboxWidget">'
            s += u'<tr><td style="vertical-align: middle;">%s:</td>' % _('Currently')
            if self.is_image:
                s += u'<td><img src="%s%s" width="50"></td></tr>' % (settings.MEDIA_URL, value)
            elif getattr(value, 'url', None):
                s += u'<td><a href="%s%s">%s</a></td></tr>' % (settings.MEDIA_URL, value, value.url)
            else:
                s += u'<td>%s</td></tr>' % _('If you want to see the old file refresh the page. Do not press F5')
            s += u'<tr><td style="vertical-align: middle;">%s:</td><td>%s</td>' % (_('Delete'), super(DeleteCheckboxWidget, self).render(name, False, attrs))
            s += u'</table>'
            return s
        else:
            return u''


class RemovableFileFormWidget(forms.MultiWidget):

    def __init__(self, is_image=False, initial=None, **kwargs):
        widgets = (forms.FileInput(), DeleteCheckboxWidget(is_image=is_image, initial=initial))
        super(RemovableFileFormWidget, self).__init__(widgets)

    def decompress(self, value):
        return [None, value]
