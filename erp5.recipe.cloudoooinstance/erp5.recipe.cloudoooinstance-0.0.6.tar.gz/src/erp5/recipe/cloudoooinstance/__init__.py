from os import path, chmod
import logging
import z3c.recipe.template as z3c_template

class Recipe(object):
  __module__ = __name__

  def __init__(self, buildout, name, options):
    options['output'] = options['conf-output']
    options['input'] = path.join(path.abspath(path.dirname(__file__)), 
                                  "cloudooo.conf.in")
    # When options is parsed by buildout, all spaces are removed. For
    # mimetype-registry is need spaces for identation.
    if "mimetype-registry" in options:
      options["mimetype-registry"] = options["mimetype-registry"].replace("\n",
                                                                       "\n ")
    self.conf_template = z3c_template.Recipe(buildout, name, options)
    options['input'] = path.join(path.abspath(path.dirname(__file__)), 
                                  "cloudoooctl.in")
    options['output'] = options['ctl-output']
    self.ctl_template = z3c_template.Recipe(buildout, name, options)

  def install(self):
    self.conf_template.install()
    self.ctl_template.install()
    chmod(self.ctl_template.output, 0755)
    return []

  update = install
