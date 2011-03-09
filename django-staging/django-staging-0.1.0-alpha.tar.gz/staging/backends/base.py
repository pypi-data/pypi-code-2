import os
import shutil

from staging.hg_utils import (hg_get_lost_files, hg_get_new_files,
                              hg_remove_files, hg_add_files)


class StagingBackend(object):

    def __init__(self, repo, module_name):
        self.repo = repo
        self.module_name = module_name
        self.path = os.path.join(repo, module_name)

    def clean(self):
        if os.path.exists(self.path):
            shutil.rmtree(self.path)
        os.mkdir(self.path)

    def mark_deleted(self):
        lost = hg_get_lost_files(self.repo, self.path)
        hg_remove_files(self.repo, lost)

    def mark_append(self):
        new_files = hg_get_new_files(self.repo, self.path)
        hg_add_files(self.repo, new_files)

    def pre_export(self):
        self.clean()

    def post_export(self):
        self.mark_deleted()
        self.mark_append()

    def export_to_staging(self):
        raise NotImplemented

    def do_export(self):
        self.pre_export()
        self.export_to_staging()
        self.post_export()

    def do_import(self):
        self.import_from_staging()

    def import_from_staging(self):
        raise NotImplemented
