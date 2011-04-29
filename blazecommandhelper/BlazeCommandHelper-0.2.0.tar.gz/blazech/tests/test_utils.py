from blazech.application import _BCHApp, Application
from blazech.commands import BaseCommand
from nose.tools import eq_

# don't let nose test it, so rename it
from .helpers import set_test_fpath_root as stfp

from ..tests.cmdapp import commands as cmdapp_commands_mod

def setup_module():
    stfp('both')

def test_gather_commands():
    cmds = _BCHApp()._commands
    eq_(cmds['hw'].__module__, 'command_hw')
    eq_(cmds['hwu'].__module__, 'command_hwu')
    eq_(len(cmds), 2)

def test_cmdapp_gather_commands():
    app = Application('cmdapp')
    cmds = app._commands
    assert len(cmds) == 3, cmds
    eq_(cmds['cahw'].__module__, 'cmdapp_cmd_hw')
    eq_(cmds['cahwu'].__module__, 'cmdapp_cmd_hwu')
    eq_(cmds['foo'].__module__, 'blazech.tests.cmdapp.entry_points')

    app.load_commands(cmdapp_commands_mod)
    assert len(cmds) == 4
    eq_(cmds['bar'].__module__, 'blazech.tests.cmdapp.commands')

    class LocalCmd(BaseCommand):
        name = 'lc'

    app.load_commands(locals())
    assert len(cmds) == 5
    assert cmds['lc'] is LocalCmd
