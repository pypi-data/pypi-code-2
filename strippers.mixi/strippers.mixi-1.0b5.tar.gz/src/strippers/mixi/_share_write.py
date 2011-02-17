# vim:fileencoding=utf-8
try:
    import json
except ImportError:
    try:
        from django.utils import simplejson as json
    except ImportError:
        import simplejson as json

SHARE_URI = 'http://api.mixi-platform.com/2/share'

def _share(self, key, title, url, image=None, pc_url=None, smartphone_url=None, mobile_url=None, description=None, comment=None, visibility='self'):
    params = {
            'key'            : key,
            'title'          : title,
            'description'    : description,
            'primary_url'    : url,
            'comment'        : comment,
            'image'          : image,
            'pc_url'         : pc_url,
            'smartphone_url' : smartphone_url,
            'mobile_url'     : mobile_url,
            'privacy'        : { 'visibility' : visibility },
            }
    data = json.dumps(params)
    self.post(SHARE_URI, data, self.CONTENT_TYPE_JSON)
    

API_METHODS = { 'share' : _share, }
