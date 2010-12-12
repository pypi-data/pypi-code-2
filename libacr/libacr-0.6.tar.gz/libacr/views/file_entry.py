from tg import config
from libacr.lib import url as acr_url
import mimetypes, os
import Image
from libacr.mediaWorker import generate_thumb_cmd
from libacr.lib import icons
import tw.forms as twf

class FileRenderer(object):
    def __init__(self):
        self.name = 'file'
        self.exposed = 'RDisk'
        self.form_fields = [twf.TextField('path', label_text="Path:",
                                                       validator=twf.validators.String(not_empty=True, strip=True)),
                            twf.TextField('title', label_text="Title:",
                                                        validator=twf.validators.String(not_empty=True, strip=True)),
                            twf.TextArea('desc', label_text="Description:",
                                                      validator=twf.validators.String())]

    def to_dict(self, data):
        data = data.split('\n', 3)
        file_path = data[0].strip()
        file_title = data[1]
        file_desc = data[2]
        
        d = {'path' : data[0].strip(),
            'title' : data[1],
             'desc' : data[2]}

        return d

    def from_dict(self, dic):
        return """%(path)s
%(title)s
%(desc)s""" % dic

    def thumbnail(self, type, file_path):
        if file_path.startswith('/rdisk/'):
            file_path = file_path[len('/rdisk/'):]

        thumb_path = os.path.splitext(file_path)[0] + '.png'
        full_path = os.path.join(config.get('public_dir'), 'rdisk', file_path)
        
        thumb_uri = '/rdisk/thumbs/'+thumb_path
        thumb_full_path = os.path.join(config.get('public_dir'), 'rdisk', 'thumbs', thumb_path)
        
        if not os.path.exists(thumb_full_path):
            try:
                os.makedirs(os.path.split(thumb_full_path)[0])
            except:
                pass
            
            if type == 'image':
                thumb = Image.open(full_path)
                thumb.thumbnail((140, 140))
                thumb.save(thumb_full_path, "PNG")
            elif type == 'video':
                os.system(generate_thumb_cmd % (full_path, thumb_full_path))
                
        return thumb_uri
    
    def preview(self, page, slice, data):
        data = data.split('\n', 3)
        
        file_path = data[0].strip()
        file_title = data[1]
        file_desc = data[2]

        file_type = mimetypes.guess_type(file_path)
        
        result = '<div class="acr_file_preview">'

        result += '<table>'
        result += '<tr>'
        result += '<td>'
        if file_type[0].startswith('application'):
           result += '<img src="%s" />'% (icons['pdf'].link)
        elif file_type[0].startswith('audio'):
           result += '<img src="%s" />'% (icons['audio'].link)
        elif file_type[0].startswith('image'):
           result += '<img src="%s" />'% (self.thumbnail('image', file_path))
        elif file_type[0].startswith('video'):
           result += '<img src="%s" />'% (self.thumbnail('video', file_path))
        else:
           result += '<img src="%s" />'% (icons['document'].link)
        result += '</td>'

        result += '<td>'
        result +='<a href="%s" >' % (file_path)
        result += '<h3>%s</h3>' % (file_title)
        result += '</a>'
        result += '</td>'

        result += '</tr>'
        result += '</table>'
        
        result += '</div>'
                
        return result

    def render(self, page, slice, data):
        data = data.split('\n', 3)
        
        file_path = data[0].strip()
        file_title = data[1]
        file_desc = data[2]
        file_type = mimetypes.guess_type(file_path)

        result = '<div class="acr_file_render">'

        result +='<a href="%s" >' % (file_path)
        if file_type[0].startswith('application'):
           result += '<img src="%s" />'% (icons['pdf'].link)
        elif file_type[0].startswith('audio'):
           result += '<img src="%s" />'% (icons['audio'].link)
        elif file_type[0].startswith('image'):
           result += '<img src="%s" />'% (self.thumbnail('image', file_path))
        elif file_type[0].startswith('video'):
           result += '<img src="%s" />'% (self.thumbnail('video', file_path))
        else:
           result += '<img src="%s" />'% (icons['document'].link)
        result += '</a>'
        
        result += '<div class=acr_body_file>'
        result += '<div class="acr_title_file"><h3>%s</h3></div>' %(file_title)
        result += '<div class="acr_desc_file">%s</div>' %(file_desc)
        result += '</div>'

        result += '</div>'
        
        
        return result
    
    