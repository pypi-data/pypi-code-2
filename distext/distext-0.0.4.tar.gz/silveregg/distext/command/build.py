import os
import sys

from silveregg.distext.utils import monkey_patch_mode
MONKEYPATCH_MODE = monkey_patch_mode()
if MONKEYPATCH_MODE == "setuptools":
    import setuptools
    # setuptools has no top build command
    from distutils.command.build \
        import \
            build as old_build
else:
    from distutils.command.build \
        import \
            build as old_build

class Build(old_build):
    user_options = old_build.user_options + \
            [('build-init-scripts=', None, "build directory for init scripts")]

    def initialize_options(self):
        old_build.initialize_options(self)
        self.build_init_scripts = None

    def finalize_options(self):
        old_build.finalize_options(self)
        if self.build_init_scripts is None:
            self.build_init_scripts = os.path.join(self.build_base,
                                                   'init-scripts-' + sys.version[0:3])

    def run(self):
        old_build.run(self)

    def has_init_scripts (self):
        return self.distribution.has_init_scripts()

    sub_commands = old_build.sub_commands + [('build_init_scripts', has_init_scripts)]
