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

from libacr.mediaWorker import generate_thumb_cmd, convert_video
import tempfile
import tw.forms as twf

class VideoRenderer(object):       
    def __init__(self):
        self.name = 'video'
        self.exposed = 'RDisk'

        self.form_fields = [twf.TextField('path', label_text="Path:",
                                                  validator=twf.validators.String(not_empty=True, strip=True)),
                            twf.TextField('title', label_text="Title:",
                                                  validator=twf.validators.String(not_empty=True, strip=True)),
                            twf.SingleSelectField('show_title', label_text="Show Title", default='none',
                                                                options=(('none', "No"),
                                                                         ('top', "On Top"),
                                                                         ('bottom', 'Under Image'))),
                            twf.TextField('size', label_text="Size (auto or 320x240):", default='auto',
                                                  validator=twf.validators.String(not_empty=True, strip=True))]

    def to_dict(self, data):
        config = ConfigParser.ConfigParser()
        config.readfp(StringIO.StringIO(data))

        d = {'show_title' : config.get('video', 'show_title'),
                   'path' : config.get('video', 'path'),
                  'title' : config.get('video', 'title'),
                   'size' : config.get('video', 'size')}

        return d

    def from_dict(self, dic):
        config = ConfigParser.ConfigParser()
        config.add_section('video')
        config.set('video', 'show_title', dic['show_title'])
        config.set('video', 'path', dic['path'])
        config.set('video', 'size', dic['size'])
        config.set('video', 'title', dic['title'])

        s = StringIO.StringIO()
        config.write(s)
        return s.getvalue()

    def thumbnail(self, video_path):
        if video_path.startswith('/rdisk/'):
            video_path = video_path[len('/rdisk/'):]

        full_path = os.path.join(config.get('public_dir'), 'rdisk', video_path).strip()
        thumb_path = os.path.splitext(video_path)[0] + '.png'
        thumb_uri = '/rdisk/thumbs/'+thumb_path
        thumb_full_path = os.path.join(config.get('public_dir'), 'rdisk', 'thumbs', thumb_path)

        if not os.path.exists(thumb_full_path):
            os.system(generate_thumb_cmd % (full_path, thumb_full_path))

            video_name = os.path.split(video_path)[-1]
            video_name = os.path.splitext(video_name)[0]
            convert_video(config.get('public_dir'), video_name, full_path)

        return thumb_uri
  
    def preview(self, page, slice, data):
        config = ConfigParser.ConfigParser()
        config.readfp(StringIO.StringIO(data))

        video_path = config.get('video', 'path')
        video_title = config.get('video', 'title')
        video_size = config.get('video', 'size')
        video_show = config.get('video', 'show_title')
        
        uri = slice.page and slice.page.uri or video_path
        video = '<div class="acr_video_preview">'
        video += '<a href="%s" title="%s">' % (uri, video_title)

        if video_show == 'top':
           video += '<div class="video_title">%s</div>' % video_title
        
        if video_path.startswith('/rdisk/'):
            video_path = video_path[len('/rdisk/'):]

        video += '<img src="/rdisk/thumbs/%s"/>' % self.thumbnail(video_path)
        
        if video_show == 'bottom':
           video += '<div class="video_title">%s</div>' % video_title
        
        video += '</a> </div>'
        return video
   
    def render(self, page, slice, data):
        config = ConfigParser.ConfigParser()
        config.readfp(StringIO.StringIO(data))

        path= config.get('video', 'path')
        title= config.get('video', 'title')
        size= config.get('video', 'size')
        show_title= config.get('video', 'show_title')
        
        video = '<div class="acr_video">'
        if show_title=='top':
           video += '<div class="video_title">%s</div>' %(title)

        video_p=os.path.splitext(path)[0]
        name_video=video_p.split('/')[2]
        
        if size == 'auto':
           video += '<video  controls="true" poster="%s">' % self.thumbnail(path)
        else: 
           size2 = size.split('x')
           video += '<video  controls="true" poster="%s" style="width:%spx;height:%spx;">'% (self.thumbnail(path),size2[0],size2[1])

        video += '<source src="/rdisk/video/video_%s.ogg" type="video/ogg"/>'% (name_video)
        video += '<source src="/rdisk/video/video_%s.mov"/>'% (name_video)
        video += '</video>'

        if show_title=='bottom':
           video += '<div class="video_title">%s</div>' %(title)

        video +='</div>'
        return video
