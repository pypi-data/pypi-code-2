import sys
import os

from silveregg.distext.utils import monkey_patch_mode
MONKEYPATCH_MODE = monkey_patch_mode()
if MONKEYPATCH_MODE == "setuptools":
    import setuptools
    from setuptools.command.sdist \
        import \
            sdist as old_sdist
else:
    from distutils.command.sdist \
        import \
            sdist as old_sdist

class Sdist(old_sdist):
    def run(self):
        # We cannot easily reuse parent classes for sdist AFAIK, since run make
        # a tarball, and there is no sane way that I know of to override the
        # list of files.
        # So we reproduce the run methods of distutils/setuptools/etc...
        if MONKEYPATCH_MODE == "setuptools":
            self.run_command('egg_info')
            ei_cmd = self.get_finalized_command('egg_info')
            self.filelist = ei_cmd.filelist
            self.filelist.append(os.path.join(ei_cmd.egg_info,'SOURCES.txt'))
            self.filelist.extend(self.distribution.get_custom_data_files_sources())
            self.filelist.extend(self.distribution.get_init_scripts())
            self.check_readme()
            self.check_metadata()

            self.make_distribution()

            dist_files = getattr(self.distribution,'dist_files',[])
            for file in self.archive_files:
                data = ('sdist', '', file)
                if data not in dist_files:
                    dist_files.append(data)
        elif MONKEYPATCH_MODE == "distutils":
            self.filelist = FileList()
            for cmd_name in self.get_sub_commands():
                self.run_command(cmd_name)
            self.filelist.extend(self.distribution.get_custom_data_files_sources())
            self.filelist.extend(self.distribution.get_init_scripts())
            self.check_metadata()
            self.get_file_list()
            if self.manifest_only:
                return
            self.make_distribution()
        else:
            raise NotImplementedError("Unknown monkey patching mode %s" % \
                                      MONKEYPATCH_MODE)
