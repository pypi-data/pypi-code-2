
import ConfigParser
import os
import tempfile
import time
import logging
import shlex
import subprocess
import sys

from paste.script import command

import pasteuwsgi
from pasteuwsgi.monitor import watch


class ServeCommand(command.Command):

    min_args = 0
    usage = ""
    summary = """Serve the described application using uWSGI"""
    description = """\
    This command serves a web application that uses a paste.deploy
    configuration file for the server and application.
    It uses uWSGI integrated http webserver, hence it is suitable for
    development only.
    """
    group_name = pasteuwsgi.paster_group_name

    parser = command.Command.standard_parser(verbose=True)

    parser.add_option("-r", "--reload",
                      action="store_true",
                      dest="reload",
                      default=False,
                      help="Use auto-restart file monitor")
    parser.add_option("-a", "--address",
                      action="store",
                      dest="address",
                      default=None,
                      help="Address to listen on")
    parser.add_option("-p", "--port",
                      action="store",
                      dest="port",
                      default=None,
                      help="Port to listen on")
    parser.add_option("-P", "--plugins",
                      action="append",
                      dest="plugins",
                      default=None,
                      help="Load uWSGI plugins")
    parser.add_option("-w", "--uwsgi",
                      action="store",
                      default=None,
                      dest="uwsgi_opts",
                      help="Additional options to uwsgi")

    def create_wsgi_script(self, ini_file, dest=None):
        template_file = os.path.join(os.path.dirname(__file__), "wsgi.py")
        with open(template_file) as f:
            template = f.read().format(ini=ini_file)

        if dest and isinstance(dest, "basestring"):
            wsgi_name = dest
            dest = open(dest)
        elif not dest:
            wsgi_name = tempfile.mkstemp(suffix=".wsgi")[1]
            dest = open(wsgi_name, "w")
        else:
            wsgi_name = None

        dest.write(template)
        dest.close()
        return wsgi_name

    def command(self):
        if not "VIRTUAL_ENV" in os.environ:
            raise command.BadCommand("This command MUST be executed "
                                     "inside a virtual env!")

        if self.verbose:
            logging.basicConfig(level=logging.DEBUG)
        else:
            logging.basicConfig(level=logging.WARN)
        self.log = logging.getLogger(__name__)

        if not self.args:
            raise command.BadCommand("You must give a config file")

        self.log.debug("Starting uWSGI")

        ini_file = self.args[0]
        if not ini_file.startswith("/"):
            ini_file = os.path.join(os.getcwd(), ini_file)
        config = ConfigParser.ConfigParser()
        config.read(ini_file)

        address = config.get("server:main", "host")
        port = int(config.get("server:main", "port"))
        if self.options.address:
            address = self.options.address
        if self.options.port:
            port = int(self.options.port)

        venv = os.environ['VIRTUAL_ENV']
        venv_site_packages = os.path.join(venv, "lib", "python%d.%d" % \
                   (sys.version_info[0], sys.version_info[1]), "site-packages")

        # We need to pass --binary-path to uwsgi or it seems to hang
        # on execve while reloading (0.9.6.6)
        uwsgibin = os.path.join(venv, "bin", "uwsgi")
        if not os.path.isfile(uwsgibin):
            uwsgibin = "/usr/bin/uwsgi"

        wsgi_name = self.create_wsgi_script(ini_file)
        pidfile = tempfile.NamedTemporaryFile(suffix=".pid", delete=False)
        pidfilename = pidfile.name

        if self.options.plugins:
            cmd = "uwsgi --plugins %s" % (','.join(self.options.plugins))
        else:
            cmd = "uwsgi"

        cmd = "%s --wsgi-file %s -H %s -M --vacuum --http %s:%d" % \
                (cmd, wsgi_name, venv, address, port)
        cmd = "%s -L -m --no-orphan --binary-path %s --pidfile %s" % \
                (cmd, uwsgibin, pidfilename)
        cmd = "%s --ini %s" % (cmd, ini_file)

        if self.options.uwsgi_opts:
            cmd = "%s %s" % (cmd, self.options.uwsgi_opts)

        self.log.info("Starting uwsgi: %s", cmd)
        try:
            uwsgi = subprocess.Popen(shlex.split(cmd))
            self.log.info("Started uwsgi with pid %s", uwsgi.pid)
            if self.options.reload:
                self.log.info("Setting up file monitor")
                pid = None
                while not pid:
                    try:
                        pid = int(pidfile.read())
                    except:
                        time.sleep(0.2)

                self.log.debug("Read uWSGI master pid: %d", pid)
                pth = os.path.join(venv_site_packages, "easy-install.pth")
                if os.path.isfile(pth):
                    with open(pth) as f:
                        paths = [os.path.realpath(p.strip())
                                 for p in f
                                 if ";" not in p and os.path.exists(p.strip())]
                else:
                    paths = []
                paths.append(venv_site_packages)
                paths.append(ini_file)
                notifier = watch(paths, pid)
                notifier.loop()

            uwsgi.wait()

        except KeyboardInterrupt:
            self.log.info("Waiting for uwsgi to shutdown")
            uwsgi.wait()

        except Exception:
            self.log.exception("Error")
            uwsgi.terminate()
            try:
                uwsgi.wait()
            except KeyboardInterrupt:
                uwsgi.wait()

        finally:
            os.unlink(wsgi_name)
