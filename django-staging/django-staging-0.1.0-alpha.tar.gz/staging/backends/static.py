import os
import shutil

from django.conf import settings

from staging.backends.base import StagingBackend


class StaticStagingBackend(StagingBackend):

    def export_to_staging(self):
        static_dirs = settings.STATICFILES_DIRS
        for dir_path in static_dirs:
            if not os.path.exists(dir_path):
                continue
            dir_name = os.path.basename(dir_path)
            repo_dir = os.path.join(self.path, dir_name)
            shutil.copytree(dir_path, repo_dir)

    def import_from_staging(self):
        static_dirs = settings.STATICFILES_DIRS
        for dir_path in static_dirs:
            dir_name = os.path.basename(dir_path)
            if os.path.exists(dir_path):
                shutil.rmtree(dir_path)
            repo_dir = os.path.join(self.path, dir_name)
            if os.path.exists(repo_dir):
                shutil.copytree(repo_dir, dir_path)
        return
