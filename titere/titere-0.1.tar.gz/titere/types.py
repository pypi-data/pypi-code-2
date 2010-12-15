import yaml
import fabric


class User(yaml.YAMLObject):

    yaml_tag = u'!User'

    def __init__(self, username, home=None, password=None, \
                 system=True, uid=None, gid=None):

        self.username = username
        self.home = home
        self.password = password
        self.uid = uid
        self.gid = gid
        self.system = system

    def apply(self):

        args = ' '

        # Home path
        if isinstance(self.home, basestring):
            args += '--home %s ' % (self.home, )

        # system user.
        if self.system:
            args += '--system '

        cmd = 'useradd%(args)s%(username)s' % {
            'args': args,
            'username': self.username}

        # Create user.
        fabric.api.local(cmd)
