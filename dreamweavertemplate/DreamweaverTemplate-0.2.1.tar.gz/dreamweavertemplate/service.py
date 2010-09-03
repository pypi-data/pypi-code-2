"""\
Dreamweaver Template Service

Caches templates in memory for faster re-use.
"""

import logging
import os

from bn import AttributeDict, uniform_path
from dreamweavertemplate import DWT
from pipestack.pipe import Marble, MarblePipe
from conversionkit import Field, set_result, chainPostConverters, Conversion, noConversion
from recordconvert import toRecord
from configconvert import existingDirectory

log = logging.getLogger(__name__)

class DwtMarble(Marble):

    def render(
        self,
        template, 
        regions=None,
        new_path=None,
        template_path='Templates',
        cache=False,
    ):
        if regions is None:
            regions = {}
        if new_path is None:
            new_path = self.bag.http.environ['PATH_INFO'][1:]
        add_slash= False
        if new_path.endswith('/'):
            add_slash = True
        if not template.startswith('/'):
            template = uniform_path(
                os.path.join(
                    self.bag.app.config[self.name].directory,
                    template,
                )
            )
        if not cache or not self.persistent_state.cache.has_key(template):
            fp = open(template, 'rb')
            output = fp.read()
            fp.close()
            self.persistent_state.cache[template] = output
        tmpl = DWT(template=self.persistent_state.cache[template])
        trs = [x[0] for x in tmpl.template_regions]
        if self.config.get('instance_stylesheet') and regions \
           and 'instance_stylesheet' in trs \
           and not regions.has_key('instance_stylesheet') \
           and self.config.has_key('instance_stylesheet'):
            regions['instance_stylesheet'] = (
                '<link rel="stylesheet" type="text/css" href="%s" />'%(
                    self.config.instance_stylesheet,
              	)
            )
        for k, v in regions.items():
            tmpl.set(k, v)
        template_path=template
        if not os.path.exists(template_path):
            raise Exception('No such template %r'%template_path)
        new_path=uniform_path(
            os.path.join(
                self.bag.app.config[self.name].directory, 
                '../', 
                new_path,
            )
        )
        if add_slash:
            new_path += '/'
        return tmpl.save_as_page(
            new_path=new_path,
            template_path=uniform_path(
                os.path.join(self.bag.app.config[self.name].directory, '../', template_path)
            ),
        )

def existingDirectoryWithConfigDefault():
    def existingDirectoryWithConfigDefault_post_converter(conversion, state):
        bag = state.bag
        pipe = state.pipe
        # Try and get the value from the 
        if conversion.successful and not conversion.result.has_key('directory'):
            if bag.app.config.has_key(pipe.aliases.static) and bag.app.config[pipe.aliases.static].has_key('site_root'):
                directory = os.path.join(bag.app.config[pipe.aliases.static]['site_root'], 'Templates')
                conversion.children['directory'] = Conversion(directory).perform(existingDirectory())
                if conversion.successful:
                    result = conversion.result
                    result['directory'] = conversion.children['directory'].result
                    set_result(conversion, result)
                else:
                    set_error(conversion, "No template directory specified for '%(name)s.directory"%pipe.name)
    return existingDirectoryWithConfigDefault_post_converter

class DwtPipe(MarblePipe):
    marble_class = DwtMarble
    default_aliases = AttributeDict(static='static')
    options = dict(
        directory = Field(
            existingDirectory(),
        ),
        instance_stylesheet = Field(
            noConversion(),
        ),
    )
    persistent_state = AttributeDict(
        cache = {}
    )


