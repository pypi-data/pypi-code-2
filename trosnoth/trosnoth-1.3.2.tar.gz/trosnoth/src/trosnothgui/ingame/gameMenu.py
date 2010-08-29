# Trosnoth (UberTweak Platform Game)
# Copyright (C) 2006-2009 Joshua D Bartlett
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# version 2 as published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301, USA.

from trosnoth.src.trosnothgui.ingame.ingameMenu import InGameMenu
from trosnoth.src.trosnothgui.ingame.dialogs import JoinGameDialog, JoiningDialog
from trosnoth.src.gui.framework.dialogbox import DialogResult
from trosnoth.src.gui.screenManager.windowManager import MultiWindowException

from trosnoth.src.utils.getUserInfo import writeName
from trosnoth.src.trosnothgui.defines import maxNameLength

class GameMenu(InGameMenu):
    '''This is not actually a menu any more, but rather a controller used only
    when joining the game.'''
    
    def __init__(self, app, gameInterface, world):
        super(GameMenu, self).__init__(app)
        self.interface = gameInterface
        self.joined = False
        self.joiningInfo = None
        self.gameInterface = gameInterface
        
        self.joinGameDialog = JoinGameDialog(self.app, self, world)
        self.joinGameDialog.onClose.addListener(self._joinDlgClose)

        self.joiningScreen = JoiningDialog(self.app, self)

        self.joinGameDialog.Show()

    def cleanUp(self):
        try:
            self.joinGameDialog.Close()
        except MultiWindowException:
            pass
        try:
            self.joiningScreen.Close()
        except MultiWindowException:
            pass

    def _joinDlgClose(self):
        if self.joinGameDialog.result is None:
            return
        elif self.joinGameDialog.result != DialogResult.OK:
            self.interface.disconnect()
        else:
            nick = self.joinGameDialog.nickBox.value.strip()
            nick = nick[:maxNameLength]
            writeName(nick)

            team = self.joinGameDialog.selectedTeam
            self.joiningInfo = nick, team
            self.joiningScreen.show(nick)
            self.interface.joinGame(nick, team).addCallback(self.joinComplete
                    ).addErrback(self.joinErrback)
        
    def showMessage(self, text):
        self.joinGameDialog.cantJoinYet.setText(text)

    def cancelJoin(self, sender):
        self.joiningScreen.Close()
        self.joinGameDialog.Show()

    def joinComplete(self, result):
        if result[0] == 'success':
            # Join was successful.
            player = result[1]
            self.joined = True
            self.interface.joined(player)
            self.joiningScreen.Close()
            self.interface.gameViewer.leaderboard.update()
            return

        self.joiningScreen.Close()
        self.joinGameDialog.Show()

        if result[0] == 'full':
            # Team is full.
            self.showMessage('That team is full!')
        elif result[0] == 'over':
            # The game is over.
            self.showMessage('The game is over!')
        elif result[0] == 'nick':
            # Nickname is already being used.
            self.showMessage('That name is already being used!')
        elif result[0] == 'wait':
            # Need to wait a few seconds before rejoining.
            self.showMessage('You need to wait ' + result[1] + ' seconds before rejoining.')
        elif result[0] == 'timeout':
            self.showMessage('Join timed out.')
        elif result[0] == 'error':
            # Python error.
            self.showMessage('Join failed: python error')
        elif result[0] == 'cancel':
            # Do nothing: join cancelled.
            print 'Join cancelled'
        else:
            # Unknown reason.
            self.showMessage('Join failed: ' + result[0])

    def joinErrback(self, error):
        'Errback for joining game.'
        # TODO: Produce some kind of traceback of the error.
        error.printTraceback()
        self.joinComplete(['There was an error'])
