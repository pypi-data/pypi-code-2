# Copyright (c) 2007-2009 Thomas Lotze
# See also LICENSE.txt

"""zc.buildout recipe for an Apache HTTP server root and apachectl script.
"""

import os
import os.path
import stat
import subprocess
import re
import warnings

import pkg_resources
import zc.buildout

from tl.buildout_apache import config


MOD_LINE = re.compile("^\s*mod_(.*)\.c\s*$")


read_resource = lambda filename: pkg_resources.resource_string(__name__,
                                                               filename)

egg_recipe = pkg_resources.load_entry_point(
    "zc.recipe.egg", "zc.buildout", "scripts")


class Recipe(object):
    """zc.buildout recipe for an Apache HTTP server root and apachectl script.

    Configuration options that apply only to the root part:
        httpd

        ulimit
        sysconf-dir
        lynx-path

        user
        group
        listen

        python

        virtual-hosts

    Configuration options that apply to both the root part and virtual hosts:
        servername (mandatory for virtual hosts)
        serveradmin
        htdocs
        cgi-bin
        log-dir

        index

    Configuration options that apply to config-parts, including the root and
    virtual host parts:
        modules
        extra-env
        extra-config

        eggs
        find-links
        extra-paths

        config-parts
    """

    def __init__(self, buildout, name, options):
        self.buildout = buildout
        self.name = name
        self.options = options

        for key, value in config.items("root"):
            options.setdefault(key, value)

        options["location"] = os.path.join(
            buildout["buildout"]["parts-directory"], name)

        host_defaults = dict(config.items("host"))

        # Collect some httpd options for the config files.
        httpd_options = buildout[options.get("httpd", "httpd")]
        for key in "httpd-path", "envvars-path", "module-dir":
            options.setdefault(key, httpd_options[key])

        for key in "htdocs", "cgi-bin":
            if key in httpd_options:
                host_defaults[key] = httpd_options[key]

        # We need to re-install after httpd was built differently in order to
        # query the built-in modules again.
        options["httpd-sig"] = (httpd_options.get("md5sum", "") +
                                httpd_options.get("extra-options", ""))

        # Create hosts, collect unique config-parts.
        self.host = host = Host(buildout, host_defaults, name)
        self.virtual_hosts = virtual_hosts = []
        config_parts = host.config_parts[:]
        for item in options.get("virtual-hosts", "").split():
            part_name, address = item.split("=")
            vhost = Host(buildout, host_defaults, part_name, address)
            virtual_hosts.append(vhost)
            config_parts.extend(part for part in vhost.config_parts
                                if part not in config_parts)

        # Collect unique modules from config-parts, in order.
        self.modules = []
        if "python" in options:
            modpython_options = buildout[options["python"]]
            self.modules.append(("python", modpython_options["modpython"]))
        seen = {}
        for part in config_parts:
            for item in part.get("modules", "").split():
                if "=" in item:
                    module, path = item.split("=", 1)
                else:
                    module, path = item, ""
                if module in seen:
                    if seen[module] != path:
                        raise zc.buildout.UserError(
                            "Conflicting module paths for Apache module %r." %
                            module)
                    continue
                seen[module] = path
                self.modules.append((module, path))
        options["modules"] = " ".join("%s=%s" % item for item in self.modules)

        # Collect extra environment variables from config-parts, in order.
        lines = []
        for part in config_parts:
            lines.extend(part.get("extra-env", "").splitlines())
        options["extra-env"] = "\n".join(filter(None, lines))

        # Initialize eggs. Do so even if no python is configured to warn if
        # egg-specific options are encountered.
        host.initialize_eggs()
        python = options.get("python")
        for vhost in virtual_hosts:
            if python is not None:
                vhost.options["python"] = python
            vhost.initialize_eggs()

        # Copy options from virtual hosts for buildout book-keeping.
        for vhost in virtual_hosts:
            for key, value in vhost.options.iteritems():
                if key in ("modules", "extra-env"):
                    continue
                options["__vhost_%s_%s" % (vhost.name, key)] = value

    def install(self):
        options = self.options.copy()
        location = options["location"]

        # ctl script
        options["env-path"] = ""
        if "executable" in options:
            # If we have a Python executable, put its location to the front of
            # the systems binary search path. mod_python uses whatever the OS
            # turns up under the name "python" as its Python interpreter.
            options["env-path"] = os.path.dirname(options["executable"]) + ":"

        options["extra-env"] = "\n".join(
            "export " + line for line in options["extra-env"].splitlines())

        # main server config
        listen = set(options["listen"].split() +
                     [vhost.address for vhost in self.virtual_hosts])
        options["listen"] = "\n".join("Listen " + line for line in listen)

        builtins = set(builtin_modules(options["httpd-path"]))
        load_modules = []
        for module, path in self.modules:
            if module in builtins:
                if path:
                    raise zc.buildout.UserError(
                        "Shared object path specified "
                        "for built-in Apache module %r." % module)
                continue
            if not path:
                path = "%s/mod_%s.so" % (options["module-dir"], module)
            load_modules.append((module, path))
        options["load-module"] = "\n".join(
            "LoadModule %s_module %s" % (module, path)
            for module, path in load_modules)

        addresses = set(vhost.address for vhost in self.virtual_hosts)
        options["name-virtual-hosts"] = "\n".join(
            "NameVirtualHost " + address for address in sorted(addresses))

        options["host-config"] = self.host.install()
        options["virtual-host-configs"] = "\n\n".join(
            '<VirtualHost "%s">\n%s\n</VirtualHost>' %
            (vhost.address, vhost.install())
            for vhost in self.virtual_hosts)

        # directories
        directories = set(("", "conf", "lock", "run"))
        directories.update(self.host.directories)
        for vhost in self.virtual_hosts:
            directories.update(vhost.directories)
        for sub in sorted(directories):
            path = os.path.join(location, sub)
            if not os.path.exists(path):
                os.mkdir(path)
            else:
                assert os.path.isdir(path)

        #files
        conf_path = os.path.join(location, "conf", "httpd.conf")
        ctl_path = os.path.join(self.buildout["buildout"]["bin-directory"],
                                self.name)

        options["conf-path"] = conf_path
        options["serverroot"] = location

        open(conf_path, "w").write(read_resource("httpd.conf.in") % options)

        open(ctl_path, "w").write(read_resource("apachectl.in") % options)
        os.chmod(ctl_path, (os.stat(ctl_path).st_mode |
                            stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH))

        return [location,
                ctl_path,
                ]

    def update(self):
        pass


def builtin_modules(httpd_path):
    """Query the httpd binary for its built-in modules.
    """
    stdout, ignored = subprocess.Popen([httpd_path, "-l"],
                                       stdout=subprocess.PIPE).communicate()
    return (mo.groups(0)[0]
            for mo in (MOD_LINE.search(line)
                       for line in stdout.splitlines())
            if mo)


class Host(object):
    """An Apache host configuration (either main or virtual).

    This is not a zc.buildout recipe.
    """

    def __init__(self, buildout, host_defaults, name, address=None):
        self.buildout = buildout
        self.name = name
        self.address = address
        self.options = options = buildout[name]

        for key, value in host_defaults.items():
            options.setdefault(key, value)

        # Normalize some options for the config files.
        for key in "htdocs", "cgi-bin":
            options[key] = os.path.normpath(os.path.join(
                buildout["buildout"]["directory"], options[key]))

        # Recursively collect unique config-parts, depth-first, considering
        # root as the initial part.
        self.config_parts = config_parts = []
        def walk(part):
            config_parts.append(part)
            for name in part.get("config-parts", "").split():
                part = buildout[name]
                if part not in config_parts:
                    walk(part)
        walk(options)

        # Collect extra configuration from config-parts.
        items = (part.get("extra-config", "") for part in config_parts)
        options["extra-config"] = "\n".join(filter(None, items))

        # Determine directories to create.
        self.directories = [options["log-dir"]]

    def initialize_eggs(self):
        # Collect Python-path-related options from config-parts.
        options = self.options

        for key in "eggs", "find-links", "extra-paths":
            values = set()
            for part in self.config_parts:
                values.update(part.get(key, "").split())
            options[key] = "\n".join(values)
            if values and "python" not in options:
                warnings.warn("%r uses the %r option but doesn't have a "
                              "mod_python installation specified." %
                              (self.name, key), Warning, stacklevel=2)

        if "python" in options:
            self.egg = egg_recipe(self.buildout, self.name, options)

    def install(self):
        options = self.options

        names = options["servername"].split()
        options["servername"] = "ServerName " + names.pop(0)
        options["serveralias"] = "\n".join(
            "ServerAlias " + name for name in names)

        admin = options.setdefault("serveradmin", "")
        if admin:
            options["serveradmin"] = "ServerAdmin " + admin

        # mod_python
        if "python" in options:
            ignored, working_set = self.egg.working_set(())
            python_path = [spec.location for spec in working_set]
            python_path.extend(self.egg.extra_paths)
            if python_path:
                options["python-path"] = PYTHON_PATH % ",\\\n ".join(
                    repr(path) for path in python_path)

        return read_resource("host.conf.in") % options


PYTHON_PATH = r"""PythonPath "[\
 %s,\
] + sys.path"
"""
