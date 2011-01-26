"""Setup the ordf.onto application"""
import logging
import pkg_resources
from pylons.util import PylonsInstaller
from ordf.onto.config.environment import load_environment

log = logging.getLogger(__name__)

def setup_app(command, conf, vars):
    """Place any commands to setup ordf.onto here"""
    load_environment(conf.global_conf, conf.local_conf)

class Installer(PylonsInstaller):
    use_cheetah = False
    config_file = 'config/deployment.ini_tmpl'

    def config_content(self, command, vars):
        """
        Called by ``self.write_config``, this returns the text content
        for the config file, given the provided variables.
        """
        module = "ordf.onto"
        if pkg_resources.resource_exists(module, self.config_file):
            return self.template_renderer(
                pkg_resources.resource_string(module, self.config_file),
                vars, filename=self.config_file)
        # Legacy support for the old location in egg-info
        return super(Installer, self).config_content(command, vars)

