"""Paste installer for Pyramid."""
import pkg_resources
from paste.script.appinstall import Installer


class PyramidInstaller(Installer):
    """Paste installer for Pyramid projects.

    This installer is used by ``paster make-config`` or ``paster setup-app``
    to create config file and setup application respectively.

    This class is based on :class:`pylons.util.PylonsInstaller`.

    """
    use_cheetah = False
    config_file = 'deployment.ini_tmpl'

    def config_content(self, command, vars):
        """
        Called by ``self.write_config``, this returns the text content
        for the config file, given the provided variables.

        """
        modules = [
            line.strip()
            for line in self.dist.get_metadata_lines('top_level.txt')
            if line.strip() and not line.strip().startswith('#')]
        if not modules:
            print 'No modules are listed in top_level.txt'
            print 'Try running python setup.py egg_info to regenerate that file'

        for mod_name in modules:
            if pkg_resources.resource_exists(mod_name, self.config_file):
                return self.template_renderer(
                    pkg_resources.resource_string(mod_name, self.config_file),
                    vars, filename=self.config_file)

        # Legacy support for the old location in egg-info
        return super(PyramidInstaller, self).config_content(command, vars)
