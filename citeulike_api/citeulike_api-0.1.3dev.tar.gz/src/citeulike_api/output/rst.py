# -*- coding: utf-8 -*-
from base import BaseRenderer
from citeulike_api.citeulike_api import strip_wrapping_braces


class Renderer(BaseRenderer):
    
    template_name = "rst_plain.rst"
    
    def __init__(self,
          *args, **kwargs):
        super(Renderer, self).__init__(*args, **kwargs)
        self.env.filters['restifytitle'] = restifty_title
        self.env.filters['stripbraces'] = strip_wrapping_braces
        
def restifty_title(title):
    t = [
      "="*len(title),
      title,
      "="*len(title),
      "",
      "",]
    return "\n".join(t)