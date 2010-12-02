import re
import os
import subprocess
from twisted.python import log
# Circular dependency, cannot import grate.mongo here.
import grate


class GitHandler(object):
    """
    The Git handler.
    """
    PATH_REGEX = re.compile(r"^'/*(.+)'$")
    COMMANDS = {
        'git-upload-pack': 'r',
        'git upload-pack': 'r',
        'git-receive-pack': 'w',
        'git receive-pack': 'w',
    }

    @staticmethod
    def parse_command(command):
        """
        >>> GitHandler.parse_command('git pull . origin')
        ('git pull', '. origin')
        >>> GitHandler.parse_command('git-upload-pack hello')
        ('git-upload-pack', 'hello')
        >>> GitHandler.parse_command('git upload-pack ')
        Traceback (most recent call last):
          ...
        ValueError: need more than 1 value to unpack
        """
        first, rest = command.split(None, 1)
        if first == 'git':
            second, rest = rest.split(None, 1)
            first = 'git %s' % second
        return first, rest

    @staticmethod
    def init(path):
        os.makedirs(path, 0700)
        p = subprocess.Popen(['git', 'init', '--bare'], cwd=path)
        return p.wait()

    @classmethod
    def get_command(cls, user, command):
        first, rest = cls.parse_command(command)
        if first not in cls.COMMANDS.keys():
            raise Exception('Unknown command')
        perm = cls.COMMANDS[first]
        match = cls.PATH_REGEX.match(rest)
        if not match:
            raise Exception('Cannot understand path: %s' % rest)
        path = match.group(1)
        if path.endswith('.git'):
            path = path[:-4]
        # Grab the repository object.
        repo = grate.mongo.Repo.get_from_path(path)
        if not repo:
            raise Exception('Repository not found: %s' % path)
        # Check access.
        access = repo.get_access(user)
        log.msg('User has access "%s" to %r' % (access, repo))
        if perm not in access:
            raise Exception('Not enough access.')
        cfg = grate.mongo.GrateConfig.get_config()
        path = os.path.join(cfg.root, path)
        log.msg('Full Path: %s' % path)
        if not os.path.exists(path) and perm == 'w':
            # If the repository does not exist and this is a push,
            # the directory has to be initialized.
            if not cls.init(path) == 0:
                raise Exception('Error while initializing.')
        return "%s '%s'" % (first, path)
