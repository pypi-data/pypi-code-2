from blazech.utils import gather_commands
from nose.tools import eq_

from helpers import set_test_fpath_root

def test_gather_commands():
    set_test_fpath_root('both')
    cmds = gather_commands()
    eq_(cmds['hw'].__module__, 'command_hw')
    eq_(cmds['hwu'].__module__, 'command_hwu')
    eq_(cmds['hwp'].__module__, 'blazech.tests.command_hwp')
    eq_(len(cmds), 3)
