import os

from django.utils.importlib import import_module

from staging import exceptions
from staging import settings
from staging.hg_utils import (hg_check_repo, hg_get_tip, hg_diff,
                              hg_get_removed_files, hg_get_added_files,
                              hg_commit, hg_init_repo, hg_log, hg_files,
                              hg_serve, hg_update, hg_push, hg_bundle,
                              hg_unbundle, hg_server_ready)


class StagingManager(object):

    def __init__(self):
        self.repo = self.get_repo()
        self.backends = self.get_backends()

    def get_backends(self):
        backends = []
        for backend_path in settings.STAGING_BACKEND_CLASSES:
            try:
                module, classname = backend_path.rsplit('.', 1)
            except ValueError:
                raise exceptions.ImproperlyConfigured('%s isn\'t a backend module' % backend_path)
            try:
                mod = import_module(module)
            except ImportError, e:
                raise exceptions.ImproperlyConfigured('Error importing backend %s: "%s"' % (module, e))
            try:
                ob_class = getattr(mod, classname)
            except AttributeError:
                raise exceptions.ImproperlyConfigured('Backend module "%s" does not define a "%s" class' % (module, classname))
            instance = ob_class(self.repo, backend_path)
            backends.append(instance)
        return backends

    def get_repo(self):
        path = settings.STAGING_REPO_DIR
        if not path:
            raise exceptions.ImproperlyConfigured('STAGING_REPO_DIR')

        if not os.path.exists(path) or not hg_check_repo(path):
            if not settings.STAGING_AUTOCREATE_REPO:
                raise exceptions.RepoNotFound(path)
            else:
                hg_init_repo(path)
        return path

    def is_initialized(self):
        return not self.get_revision().split('\n')[0].replace('changeset:', '').strip().startswith('-1')

    def staging_export(self):
        for b in self.backends:
            b.do_export()

    def staging_import(self):
        hg_update(self.repo)
        for b in self.backends:
            b.do_import()

    def get_revision(self):
        return hg_get_tip(self.repo)

    def get_diff(self):
        return hg_diff(self.repo)

    def get_added_files(self):
        return hg_get_added_files(self.repo)

    def get_removed_files(self):
        return hg_get_removed_files(self.repo)

    def commit(self, message='Default commit message'):
        return hg_commit(self.repo, message)

    def get_logs(self):
        full_log = hg_log(self.repo)
        commits = []
        log = ''
        changeset = None
        for line in full_log.split('\n'):
            if not line:
                if not changeset:
                    continue
                commits.append({'changeset': changeset,
                                'log': log})
                log = ''
                changeset = None
                continue
            log += line
            log += '\n'
            if line.startswith('changeset:'):
                changeset = line.replace('changeset:', '').strip()
        return commits

    def get_log_for_revision(self, revision):
        files = hg_files(self.repo, revision)
        modified_files, added_files, removed_files = files.split('\n')
        removed_files = [i for i in removed_files.split(' ') if i]
        added_files = [i for i in added_files.split(' ') if i]
        modified_files = [i for i in modified_files.split(' ') if i not in added_files and i not in removed_files]
        log = hg_log(self.repo, revision).split('\n\n')
        return {'modified_files': modified_files,
                'added_files': added_files,
                'removed_files': removed_files,
                'head': log[0],
                'diff': log[1]}

    def start_server(self):
        self.server = hg_serve(self.repo, settings.STAGING_HG_SERVE_PORT)
        return True

    def end_server(self):
        self.server.kill()
        return True

    def make_push(self, url):
        return hg_push(self.repo, url)

    def make_bundle(self):
        return hg_bundle(self.repo)

    def unbundle(self, stream):
        return hg_unbundle(self.repo, stream)

    def check_repository(self):
        return hg_server_ready(settings.STAGING_HG_SERVE_PORT)

staging_manager = StagingManager()
