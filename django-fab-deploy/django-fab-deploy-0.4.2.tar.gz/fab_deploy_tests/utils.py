import subprocess
from functools import partial
from fabric import state
from fabric.main import get_hosts
from fabric.network import interpret_host_string, HostConnectionCache

def fab(command, *args, **kwargs):
    """ Runs fab command. Accepts callable. """
    state.connections = HostConnectionCache()
    state.env.command = command.__name__
    state.env.all_hosts = hosts = get_hosts(command, None, None)
    for host in hosts:
        interpret_host_string(host)
        command(*args, **kwargs)


class VirtualBox(object):
    def __init__(self, name):
        self.name = name

    def __getattr__(self, name):
        """
        Attributes are converted to a functions calling
        VBoxManage shell command.
        """
        return partial(self, name)

    def __call__(self, command, *args):
        params = ['VBoxManage', command, self.name] + list(args)
        print '$ ' + ' '.join(params)
        return subprocess.call(params)

    def start(self):
        # headless variant leads to invalid snapshots for some reason
        # (bug in virtualbox?)
        # self.startvm('--type', 'headless')
        self.startvm()

    def stop(self):
        self.controlvm('poweroff')
