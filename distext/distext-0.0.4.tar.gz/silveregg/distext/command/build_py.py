import sys
import os

from silveregg.distext.utils import monkey_patch_mode
MONKEYPATCH_MODE = monkey_patch_mode()
if MONKEYPATCH_MODE == "setuptools":
    import setuptools
    from setuptools.command.build_py \
        import \
            build_py as old_build_py
else:
    from distutils.command.build_py \
        import \
            build_py as old_build_py
from silveregg.distext.utils \
    import \
        ensure_directory

class BuildPy(old_build_py):
    def run(self):
        old_build_py.run(self)

        if self.distribution.scheme_module_path is not None:
            target = os.path.join(self.build_lib, self.distribution.scheme_module_path)

            instcmd = self.get_finalized_command('install')
            scheme = instcmd.get_expanded_scheme()
            content = []
            for name, value in scheme.items():
                content += ["%-16s = '%s'" % (name.upper(),  value)]

            ensure_directory(target)
            f = open(target, "w")
            try:
                f.write("\n".join(content))
            finally:
                f.close()

