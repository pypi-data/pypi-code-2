#XXX chamaleon.  genshi support is broken at the moment

import os
import logging


from rum import app
from rum import BaseRenderer

log = logging.getLogger(__name__)

try:
    from chameleon.genshi.loader import TemplateLoader
except ImportError:
    log.error("Could not import chameleon.genshi")
else:
    class ChameleonGenshiRenderer(BaseRenderer):
        framework_name = 'chameleon-genshi'
        def __init__(self, search_path=None, auto_reload=True, cache_dir=None):
            super(ChameleonGenshiRenderer, self).__init__(
                search_path, auto_reload, cache_dir
                )
            self.loader = TemplateLoader(
                search_path = self.search_path,
                auto_reload = self.auto_reload,
                )

        def render(self, data, possible_templates=[]):
            template =  self.load_template(possible_templates)
            return template.render(**data)

        def load_template(self, possible_templates=[]):
            #XXX: this function could be memoized
            for template in possible_templates:
                try:
                    template = self.loader.load(template.lstrip(os.path.sep))
                    log.debug("Template found at %s", template)
                    return template
                except ValueError, e:
                    log.debug("Template not found at %s: %s", template, e)
            raise LookupError(
                "None of the following templates could be loaded: " +
                `possible_templates`
                )
