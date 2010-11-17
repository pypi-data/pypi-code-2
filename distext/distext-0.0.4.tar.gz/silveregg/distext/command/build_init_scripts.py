import os
import shutil
import collections
from stat \
    import \
        ST_MODE
from distutils.cmd \
    import \
        Command

from silveregg.distext.utils \
    import \
        ensure_directory

class BuildInitScripts(Command):
    description = "Build init scripts for python daemons/services."

    user_options = [
        ('build-dir=', 'd', "directory to \"build\" (copy) to")]

    def initialize_options(self):
        self.build_dir = None

    def finalize_options(self):
        self.init_scripts = self.distribution.init_scripts
        self.set_undefined_options('build', ('build_init_scripts', 'build_dir'))

    def run(self):
        instcmd = self.get_finalized_command("install")
        install_scheme = instcmd.get_expanded_scheme()

        for script in self.init_scripts:
            script.finalize(install_scheme)
            path = instcmd.get_expanded_path(script.destination)
            target = os.path.join(self.build_dir, script.encoded_path(path))
            ensure_directory(target)

            with open(target, "w") as fid:
                fid.write(script.content)

            if os.name == 'posix':
                oldmode = os.stat(target)[ST_MODE] & 07777
                newmode = (oldmode | script.mode) & 07777
                if newmode != oldmode:
                    os.chmod(target, newmode)
