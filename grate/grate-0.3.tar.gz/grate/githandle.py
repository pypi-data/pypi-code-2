import re
import os
import subprocess
from twisted.python import log
# Circular dependency, cannot import grate.mongo here.
import grate


class UnknownCommandException(Exception):
    pass

class InvalidPathException(Exception):
    pass

class NoSuchRepoException(Exception):
    pass

class NotAllowedException(Exception):
    pass

class GitException(Exception):
    pass

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
        try:
            first, rest = cls.parse_command(command)
        except Exception as e:
            raise UnknownCommandException(e)
        if first not in cls.COMMANDS.keys():
            raise UnknownCommandException
        perm = cls.COMMANDS[first]
        match = cls.PATH_REGEX.match(rest)
        if not match:
            raise InvalidPathException('Invalid path: %s' % rest)
        path = match.group(1)
        if path.endswith('.git'):
            path = path[:-4]
        # Grab the repository object.
        repo = grate.mongo.Repo.get_from_path(path)
        if not repo:
            raise NoSuchRepoException('Repo not found: %s')
        # Check access.
        access = repo.get_access(user)
        log.msg('User has access "%s" to %r' % (access, repo))
        if perm not in access:
            raise NotAllowedException('Not enough access.')
        cfg = grate.mongo.GrateConfig.get_config()
        path = os.path.join(cfg.root, path)
        log.msg('Full Path: %s' % path)
        if not os.path.exists(path):
            # If the repository does not exist,
            # the directory has to be initialized.
            if not cls.init(path) == 0:
                raise GitException('Error while initializing.')
        return "%s '%s'" % (first, path)
