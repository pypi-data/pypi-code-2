import logging

from mako.lookup import TemplateLookup
from mako.exceptions import TemplateLookupException

from rum import app
from rum import BaseRenderer

log = logging.getLogger(__name__)

class MakoRenderer(BaseRenderer):
    framework_name = 'name'
    def __init__(self, search_path=None, auto_reload=True, cache_dir=None):
        super(MakoRenderer, self).__init__(search_path, auto_reload, cache_dir)
        self.loader = TemplateLookup(
            directories = self.search_path,
            module_directory = self.cache_dir,
            filesystem_checks = self.auto_reload,
            )

    def render(self, data, possible_templates=[]):
        return self.load_template(possible_templates).render_unicode(**data)

    def load_template(self, possible_templates=[]):
        #XXX: this function could be memoized
        for template in possible_templates:
            try:
                template = self.loader.get_template(template)
                log.debug("Template found at %s", template)
                return template
            except TemplateLookupException, e:
                log.debug("Template not found at %s: %s", template, e)
        raise LookupError("None of the following templates could be loaded: " +
                          `possible_templates`)
