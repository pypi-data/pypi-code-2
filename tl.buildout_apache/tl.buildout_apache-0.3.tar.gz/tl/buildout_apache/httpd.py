# Copyright (c) 2007-2010 Thomas Lotze
# See also LICENSE.txt

"""zc.buildout recipe for building an Apache HTTP server from source.
"""

import os.path
import zc.recipe.cmmi

from tl.buildout_apache import config


class Recipe(zc.recipe.cmmi.Recipe):
    """zc.buildout recipe for building an Apache HTTP server from source.

    Configuration options:
        url
        md5sum
        extra-options
        extra-vars

    Exported options:
        httpd-path
        envvars-path
        apxs-path
        module-dir
        htdocs
        cgi-bin
    """

    def __init__(self, buildout, name, options):
        for key, value in config.items("httpd"):
            options.setdefault(key, value)

        options['extra_options'] = (
            '--enable-so ' + options.get('extra-options', ''))
        options['environment'] = options.get('extra-vars', '')

        super(Recipe, self).__init__(buildout, name, options)

        location = options["location"]

        # Export some options.
        for name in "httpd", "envvars", "apxs":
            options[name + "-path"] = os.path.join(location, "bin", name)
        options["module-dir"] = os.path.join(location, "modules")
        options["htdocs"] = os.path.join(location, "htdocs")
        options["cgi-bin"] = os.path.join(location, "cgi-bin")
