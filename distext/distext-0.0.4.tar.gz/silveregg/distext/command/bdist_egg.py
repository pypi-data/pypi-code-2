import sys
import os

from silveregg.distext.utils import monkey_patch_mode
MONKEYPATCH_MODE = monkey_patch_mode()
if MONKEYPATCH_MODE == "setuptools":
    import setuptools
    from setuptools.command.bdist_egg \
        import \
            bdist_egg as old_bdist_egg
else:
    from distutils.command.bdist_egg \
        import \
            bdist_egg as old_bdist_egg

class BdistEgg(old_bdist_egg):
    def run(self):
        self.run_command("build")
        old_bdist_egg.run(self)
