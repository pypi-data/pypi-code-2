# -*- coding: utf-8 -*-
import ConfigParser
from tg import tmpl_context
import StringIO
from libacr.lib import url as acr_url
from libacr.lib import language
from genshi.template import MarkupTemplate

from libacr.model.core import DBSession
from libacr.model.content import Page
import os
from tg import config
import Image
import tw.forms as twf

class LinkedImageRenderer(object):
    def __init__(self):
        self.name = 'linked_image'
        self.exposed = 'RDisk'
        self.form_fields = [twf.TextField('path', label_text="Path:",
                                                  validator=twf.validators.String(not_empty=True, strip=True)),
                            twf.TextField('link', label_text="Link:",
                                                  validator=twf.validators.String(not_empty=True, strip=True)),
                            twf.TextField('title', label_text="Title:",
                                                  validator=twf.validators.String(not_empty=True, strip=True)),
                            twf.TextField('size', label_text="Size (auto or 320x240):", default='auto',
                                                  validator=twf.validators.String(not_empty=True, strip=True)),
                            twf.SingleSelectField('show_title', label_text="Show Title", default='none',
                                                                options=(('none', "No"),
                                                                         ('top', "On Top"),
                                                                         ('bottom', 'Under Image'))),
                            twf.SingleSelectField('show_desc', label_text="Show Description", default='none',
                                                                options=(('none', "No"),
                                                                         ('bottom', "Under Image"))),
                            twf.TextArea('description', label_text="Description:",
                                                        validator=twf.validators.String())]

    def to_dict(self, data):
        config = ConfigParser.ConfigParser({'description':'', 'show_title':'None','show_desc':'None'})
        config.readfp(StringIO.StringIO(data))

        d = {'show_title' : config.get('image', 'show_title'),
              'show_desc' : config.get('image', 'show_desc'),
                   'path' : config.get('image', 'path'),
                   'link' : config.get('image', 'link'),
                  'title' : config.get('image', 'title'),
                   'size' : config.get('image', 'size'),
            'description' : config.get('image', 'description')}

        return d

    def from_dict(self, dic):
        config = ConfigParser.ConfigParser()
        config.add_section('linked_image')
        config.set('linked_image', 'show_title', dic.get('show_title', 'none'))
        config.set('linked_image', 'show_desc', dic.get('show_desc', 'none'))
        config.set('linked_image', 'path', dic.get('path', ''))
        config.set('linked_image', 'size', dic.get('size', 'auto'))
        config.set('linked_image', 'link', dic.get('link', ''))
        config.set('linked_image', 'title', dic.get('title', ''))
        config.set('linked_image', 'description', dic.get('description', ''))

        s = StringIO.StringIO()
        config.write(s)
        return s.getvalue()

    def thumbnail(self, image_path):
        if image_path.startswith('/rdisk/'):
            image_path = image_path[len('/rdisk/'):]

        thumb_path = os.path.splitext(image_path)[0] + '.png'
        full_path = os.path.join(config.get('public_dir'), 'rdisk', image_path)

        thumb_uri = '/rdisk/thumbs/'+thumb_path
        thumb_full_path = os.path.join(config.get('public_dir'), 'rdisk', 'thumbs', thumb_path)

        if not os.path.exists(thumb_full_path):
            try:
                os.makedirs(os.path.split(thumb_full_path)[0])
            except:
                pass

            full_path_path=full_path.rstrip('\r')
            thumb = Image.open(full_path_path)
            thumb.thumbnail((140, 140))
            thumb.save(thumb_full_path, "PNG")

        return thumb_uri

    def preview(self, page, slice, data):
        config = ConfigParser.ConfigParser({'description':'', 'show_title':'None','show_desc':'None'})
        config.readfp(StringIO.StringIO(data))

        image_path = config.get('linked_image', 'path')
        image_title = config.get('linked_image', 'title')
        image_size = config.get('linked_image', 'size')
        image_show = config.get('linked_image', 'show_title')
        image_desc= config.get('linked_image', 'description')
        show_desc = config.get('linked_image', 'show_desc')

        uri = slice.page and slice.page.uri or image_path
        image = '<div class="acr_image_preview">'
        image += '<a name="%s" href="%s" title="%s">' % (image_path, uri, image_title)

        if image_show=='top':
           image += '<div>%s</div>' % image_title

        image += '<img src="%s" />' % (self.thumbnail(image_path))

        if image_show =='bottom':
           image += '<div>%s</div>' % image_title

        image += '</a>'

        if show_desc=='bottom' and image_desc!='' :
           image +='<p class="acr_image_preview_desc">%s<p>' % (image_desc)

        image += '</div>'
        return image


    def render(self, page, slice, data):
        config = ConfigParser.ConfigParser({'description':'', 'show_title':'None','show_desc':'None'})
        config.readfp(StringIO.StringIO(data))

        path= config.get('linked_image', 'path')
        title= config.get('linked_image', 'title')
        link= config.get('linked_image', 'link')
        size= config.get('linked_image', 'size')
        show_title= config.get('linked_image', 'show_title')
        desc= config.get('linked_image', 'description')
        show_desc = config.get('linked_image', 'show_desc')

        image = '<div class="acr_image"><a href="%s" alt="">' % (link)
        if show_title=='top':
           image += '<div>%s</div>' %(title)

        if size== 'auto':
           image += '<img src="%s"/>' % (link, path)
        else:
           size2= size.split('x')
           image += '<img src="%s" style="width:%spx; height:%spx;"/>' % (path,size2[0],size2[1])

        if show_title=='bottom':
           image += '<div>%s</div>' %(title)

        if show_desc=='bottom' and desc != '':
           image +='<p class="acr_image_desc">%s<p>' % (desc)
        image +='</a></div>'
        return image
