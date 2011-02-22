# Trosnoth (UberTweak Platform Game)
# Copyright (C) 2006-2011 Joshua D Bartlett
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

from collections import defaultdict
import string
import logging

from trosnoth.model.universe import Abort
from trosnoth.model.upgrades import allUpgrades
from trosnoth.model.zone import ZoneState
from trosnoth.messages import (AchievementUnlockedMsg, TaggingZoneMsg,
        PlayerKilledMsg, PlayerHasUpgradeMsg, ShotFiredMsg, DeleteUpgradeMsg,
        ChatMsg, ShotAbsorbedMsg, RespawnMsg, RemovePlayerMsg, GameOverMsg)
from trosnoth.utils.event import Event

log = logging.getLogger('achievementlist')

###########
# Helpers #
###########

def checkPlayerId(fn):
    def newFn(self, msg):
        if msg.playerId == self.player.id:
            return fn(self, msg)
    newFn.__name__ = fn.__name__
    return newFn

############################
# Achievement base classes #
############################

class Achievement(object):

    keepProgress = False
    afterGame = False

    def rejoined(self, player):
        pass

    def processMessage(self, msg):
        msgType = type(msg).__name__
        methodname = 'got%s' % (msgType,)
        if hasattr(self, methodname):
            proc = getattr(self, methodname)
            proc(msg)

    def _sendUnlocked(self, player):
        self.outPlug.send(AchievementUnlockedMsg(player.id,
                self.idstring.encode()))
        log.debug(self.achievementString(player))

    def achievementString(self, player):
        if self.name == "":
            return 'Achievement unlocked by %s! - %s' % (player.nick,
                                                         self.idstring)
        else:
            return 'Achievement unlocked by %s! - %s' % (player.nick,
                                                         self.name)

    def __str__(self):
        return '%s' % self.idstring

    def describe(self):
        '''
        Used when saving achievement meta-information to file. Should be
        overwritten by higher level classes.
        '''
        information = {'name': self.name,
                       'description': self.description,
                       'type': 'boolean'}
        return {self.idstring: information}

class PlayerAchievement(Achievement):
    def __init__(self, player, world, outPlug):
        super(PlayerAchievement, self).__init__()
        self.player = player
        self.world = world
        self.outPlug = outPlug

    def rejoined(self, player):
        self.player = player


class OncePerGame(Achievement):
    def __init__(self, world, outPlug):
        super(OncePerGame, self).__init__()
        self.world = world
        self.outPlug = outPlug
        self.unlocked = False

    def achievementUnlocked(self, playerList):
        if not self.unlocked:
            self.unlocked = True
            for player in playerList:
                self._sendUnlocked(player)

    def listeningForMessages(self):
        return not self.unlocked

class OncePerTeamPerGame(Achievement):
    def __init__(self, world, team, outPlug):
        super(OncePerTeamPerGame, self).__init__()
        self.world = world
        self.outPlug = outPlug
        self.team = team
        self.unlocked = False

    def achievementUnlocked(self, playerList):
        if not self.unlocked:
            self.unlocked = True
            for player in playerList:
                self._sendUnlocked(player)

    def listeningForMessages(self):
        return not self.unlocked

class OncePerPlayerPerGame(PlayerAchievement):
    def __init__(self, player, world, outPlug):
        super(OncePerPlayerPerGame, self).__init__(player, world, outPlug)
        self.unlocked = False

    def achievementUnlocked(self):
        if not self.unlocked:
            self.unlocked = True
            self._sendUnlocked(self.player)

    def listeningForMessages(self):
        return not self.unlocked

class NoLimit(PlayerAchievement):
    def __init__(self, player, world, outPlug):
        super(NoLimit, self).__init__(player, world, outPlug)
        self.unlocked = False

    def achievementUnlocked(self):
        self.unlocked = True
        self._sendUnlocked(self.player)

    def listeningForMessages(self):
        return True

class OnceEverPerPlayer(PlayerAchievement):
    '''
    self.unlocked is "unlocked this time".
    self.previouslyUnlocked is "unlocked previously".
    '''
    keepProgress = True
    def __init__(self, player, world, outPlug):
        super(OnceEverPerPlayer, self).__init__(player, world, outPlug)
        self.unlocked = False
        self.previouslyUnlocked = False
        if self.player is not None:
            self.readExistingData()

    def readExistingData(self):
        user = self.player.user
        if user is None:
            self.previouslyUnlocked = False
            self.progress = 0
        else:
            userAchievements = user.achievements.get(self.idstring, {})
            self.previouslyUnlocked = userAchievements.get('unlocked', False)
            self.progress = userAchievements.get('progress', 0)

    def achievementUnlocked(self):
        if not self.unlocked and not self.previouslyUnlocked:
            self.unlocked = True
            self._sendUnlocked(self.player)

    def listeningForMessages(self):
        return not self.unlocked and not self.previouslyUnlocked

    def getJsonString(self):
        return {
            'unlocked' : self.unlocked or self.previouslyUnlocked,
            'progress' : self.progress,
        }


###################
# Streak subclass #
###################

class IncrementingAchievement(Achievement):
    requiredQuantity = -1
    def __init__(self, player, world, outPlug):
        self.progress = 0
        super(IncrementingAchievement, self).__init__(player, world, outPlug)

    def increment(self, amount=1):
        self.progress = min(self.requiredQuantity, self.progress + amount)

        if self.progress == self.requiredQuantity:
            self.achievementUnlocked()

    def reset(self):
        self.progress = 0

    def __str__(self):
        return "%s: %d/%d" % (self.idstring, self.progress,
                self.requiredQuantity)

    def describe(self):
        information = {'name': self.name,
                       'description': self.description,
                       'type': 'incremental',
                       'requirements': self.requiredQuantity,
                       'keepProgress': self.keepProgress}
        return {self.idstring: information}

class Streak(IncrementingAchievement):
    '''
    Base class for streak achivements. Subclasses must define:
     * streakTarget - the number to aim for
     * incrementTrigger - a Trigger class on which increments occur
     * resetTrigger (optional) - a Trigger class on which resets occur
    '''
    resetTrigger = None

    def __init__(self, player, world, outPlug):
        self.progress = 0
        super(Streak, self).__init__(player, world, outPlug)
        self.incrementTrigger = self.incrementTrigger(player, world)
        self.incrementTrigger.onTrigger.addListener(self.increment)
        if self.resetTrigger is not None:
            self.resetTrigger = self.resetTrigger(player, world)
            self.resetTrigger.onTrigger.addListener(self.reset)
        self.requiredQuantity = self.streakTarget

    def processMessage(self, msg):
        msgClass = msg.__class__
        if msgClass in self.incrementTrigger.messages:
            self.incrementTrigger.processMessage(msg)
        if (self.resetTrigger is not None and msgClass in
                self.resetTrigger.messages):
            self.resetTrigger.processMessage(msg)

    def rejoined(self, player):
        super(Streak, self).rejoined(player)
        if self.resetTrigger is not None:
            self.resetTrigger.rejoined(player)
        self.incrementTrigger.rejoined(player)

class Trigger(object):
    def __init__(self, player, world):
        self.player = player
        self.world = world
        self.onTrigger = Event()

    def processMessage(self, msg):
        msgType = type(msg).__name__
        methodname = 'got%s' % (msgType,)
        proc = getattr(self, methodname)
        proc(msg)

    def rejoined(self, player):
        self.player = player

class ZoneTagTrigger(Trigger):
    messages = (TaggingZoneMsg,)

    @checkPlayerId
    def gotTaggingZoneMsg(self, msg):
        self.onTrigger.execute()

class TagAssistTrigger(Trigger):
    messages = (TaggingZoneMsg,)

    def processMessage(self, msg):
        if (self.player.team and msg.teamId == self.player.team.id):
            if msg.playerId == self.player.id:
                return
            zone = self.world.getZone(msg.zoneId)
            if self.player in zone.players:
                self.onTrigger.execute()

class PlayerDeathTrigger(Trigger):
    messages = (PlayerKilledMsg,)

    def processMessage(self, msg):
        if msg.targetId == self.player.id:
            self.onTrigger.execute()

class PlayerKillTrigger(Trigger):
    messages = (PlayerKilledMsg,)

    def gotPlayerKilledMsg(self, msg):
        if msg.killerId == self.player.id:
            self.onTrigger.execute()

class UseUpgradeTrigger(Trigger):
    messages = (PlayerHasUpgradeMsg,)

    @checkPlayerId
    def processMessage(self, msg):
        self.onTrigger.execute()

class FireShotTrigger(Trigger):
    messages = (ShotFiredMsg,)

    @checkPlayerId
    def processMessage(self, msg):
        self.onTrigger.execute()

class EarnStarTrigger(PlayerKillTrigger, ZoneTagTrigger):
    messages = (PlayerKilledMsg, TaggingZoneMsg)

##########################
# Achievement subclasses #
##########################

class KilledSomeoneAchievement(Achievement):
    messages = (PlayerKilledMsg,)

    def gotPlayerKilledMsg(self, msg):
        if msg.killerId == self.player.id:
            self.killedSomeone(msg)

    def killedSomeone(self, msg):
        pass # To be implemented in subclasses

class ChecklistAchievement(Achievement):
    requiredItems = set()
    def __init__(self, player, world, outPlug):
        self.progress = set()
        super(ChecklistAchievement, self).__init__(player, world, outPlug)

    def addItem(self, item):
        self.progress.add(item)

        if self.requiredItems == self.progress:
            self.achievementUnlocked()

    def __str__(self):
        return "%s: %d/%d items" % (self.idstring, len(self.progress),
                len(self.requiredItems))

    def describe(self):
        information = {'name': self.name,
                       'description': self.description,
                       'type': 'checklist',
                       'requirements': list(self.requiredItems),
                       'keepProgress': self.keepProgress}
        return {self.idstring: information}

class PersistedChecklistAchievement(ChecklistAchievement, OnceEverPerPlayer):
    def readExistingData(self):
        user = self.player.user
        if user is None:
            self.previouslyUnlocked = False
            self.progress = set()
        else:
            userAchievements = user.achievements.get(self.idstring, {})
            self.previouslyUnlocked = userAchievements.get('unlocked', False)
            self.progress = set(userAchievements.get('progress', []))

    def getJsonString(self):
        return {
            'unlocked' : self.unlocked or self.previouslyUnlocked,
            # JSON doesn't support sets:
            'progress' : list(self.progress),
        }

class TimedAchievement(Achievement):
    requiredValue = -1
    timeWindow = -1

    def __init__(self, player, world, outPlug):
        super(TimedAchievement, self).__init__(player, world, outPlug)
        self.rollingList = []

    def addToList(self):
        now = self.world.getGameTime()
        self.rollingList.append(now)

        while (len(self.rollingList) > 0 and (now - self.rollingList[0]) >
                self.timeWindow):
            del self.rollingList[0]

        if len(self.rollingList) >= self.requiredValue:
            self.achievementUnlocked()
            self.rollingList = []


class QuickKillAchievement(TimedAchievement, KilledSomeoneAchievement):
    deathTypes = ''

    def killedSomeone(self, msg):
        if msg.deathType in self.deathTypes:
            self.addToList()


#########################
# Concrete Achievements #
#########################

class MultiTagSmall(Streak, OncePerPlayerPerGame):
    idstring = 'multiTagSmall'
    name = 'I Ain\'t Even Winded'
    description = 'Capture three zones in a single life'

    incrementTrigger = ZoneTagTrigger
    resetTrigger = PlayerDeathTrigger
    streakTarget = 3
    messages = incrementTrigger.messages + resetTrigger.messages

class MultiTagMedium(Streak, OncePerPlayerPerGame):
    idstring = 'multiTagMedium'
    name = 'The Long Way Home'
    description = 'Capture five zones in a single life'

    incrementTrigger = ZoneTagTrigger
    resetTrigger = PlayerDeathTrigger
    streakTarget = 5
    messages = incrementTrigger.messages + resetTrigger.messages

class MultiTagLarge(Streak, OncePerPlayerPerGame):
    idstring = 'multiTagLarge'
    name = 'Cross-Country Marathon'
    description = 'Capture eight zones in a single life'

    incrementTrigger = ZoneTagTrigger
    resetTrigger = PlayerDeathTrigger
    streakTarget = 8
    messages = incrementTrigger.messages + resetTrigger.messages

class TotalTagsSmall(Streak, OnceEverPerPlayer):
    idstring = 'totalTagsSmall'
    name = 'Captured 20 Zones'
    description = 'Capture 20 zones'

    incrementTrigger = ZoneTagTrigger
    streakTarget = 20
    messages = incrementTrigger.messages

class TotalTagsMedium(Streak, OnceEverPerPlayer):
    idstring = 'totalTagsMedium'
    name = 'Captured 50 Zones'
    description = 'Capture 50 zones'

    incrementTrigger = ZoneTagTrigger
    streakTarget = 50
    messages = incrementTrigger.messages

class MultiKillSmall(Streak, OncePerPlayerPerGame):
    idstring = 'multikillSmall'
    name = 'Triple Threat'
    description = 'Kill three enemies in a single life'

    incrementTrigger = PlayerKillTrigger
    resetTrigger = PlayerDeathTrigger
    streakTarget = 3
    messages = incrementTrigger.messages + resetTrigger.messages

class MultiKillMedium(Streak, OncePerPlayerPerGame):
    idstring = 'multikillMedium'
    name = 'High Five'
    description = 'Kill five enemies in a single life'

    incrementTrigger = PlayerKillTrigger
    resetTrigger = PlayerDeathTrigger
    streakTarget = 5
    messages = incrementTrigger.messages + resetTrigger.messages

class MultiKillLarge(Streak, OncePerPlayerPerGame):
    idstring = 'multikillLarge'
    name = 'Seriously Ten'
    description = 'Kill ten enemies in a single life'

    incrementTrigger = PlayerKillTrigger
    resetTrigger = PlayerDeathTrigger
    streakTarget = 10
    messages = incrementTrigger.messages + resetTrigger.messages

class TotalKillsSmall(Streak, OnceEverPerPlayer):
    idstring = 'totalKillsSmall'
    name = 'Family Friendly Fun'
    description = 'Kill 50 enemies'

    incrementTrigger = PlayerKillTrigger
    streakTarget = 50
    messages = incrementTrigger.messages

class TotalKillsMedium(Streak, OnceEverPerPlayer):
    idstring = 'totalKillsMedium'
    name = 'We All Fall Down'
    description = 'Kill 100 enemies'

    incrementTrigger = PlayerKillTrigger
    streakTarget = 100
    messages = incrementTrigger.messages

class ShoppingSpree(Streak, OncePerPlayerPerGame):
    idstring = 'multiUpgradesSmall'
    name =  'Shopping Spree'
    description = 'Buy two upgrades in a single life'

    incrementTrigger = UseUpgradeTrigger
    resetTrigger = PlayerDeathTrigger
    streakTarget = 2
    messages = incrementTrigger.messages + resetTrigger.messages

class SmartShopper(Streak, OncePerPlayerPerGame):
    idstring = 'multiUpgradesMedium'
    name = 'Smart Shopper'
    description = 'Buy five upgrades in a single game'

    incrementTrigger = UseUpgradeTrigger
    streakTarget = 5
    messages = incrementTrigger.messages

class BulletsSmall(Streak, OncePerPlayerPerGame):
    idstring = 'bulletsSmall'
    name = 'Machine Gunner'
    description = 'Shoot 100 bullets in a single life'

    incrementTrigger = FireShotTrigger
    resetTrigger = PlayerDeathTrigger
    streakTarget = 100
    messages = incrementTrigger.messages + resetTrigger.messages

class BulletsMedium(Streak, OncePerPlayerPerGame):
    idstring = 'bulletsMedium'
    name = 'Ammunition Overdrive'
    description = 'Shoot 500 bullets in a single game'

    incrementTrigger = FireShotTrigger
    streakTarget = 500
    messages = incrementTrigger.messages

class AssistTags(Streak, OncePerPlayerPerGame):
    idstring = 'assistTags'
    name = 'Credit to Team'
    description = 'Assist in the tagging of five zones in a single game'

    incrementTrigger = TagAssistTrigger
    streakTarget = 5
    messages = incrementTrigger.messages

class QuickKillSmall(QuickKillAchievement, NoLimit):
    requiredValue = 2
    timeWindow = 5
    deathTypes = 'ST'
    idstring = 'quickKillSmall'
    name = 'Double Kill'
    description = 'Kill two enemies within five seconds (no grenades)'

class QuickKillMedium(QuickKillAchievement, NoLimit):
    requiredValue = 3
    timeWindow = 5
    deathTypes = 'ST'
    idstring = 'quickKillMedium'
    name = 'Triple Kill'
    description = 'Kill three enemies within five seconds (no grenades)'

class GrenadeMultiKill(QuickKillAchievement, NoLimit):
    requiredValue = 3
    # Processing of achievements should happen within 0.25 secs
    timeWindow = 0.25
    deathTypes = 'G'
    idstring = 'grenadeMultikill'
    name = "It's Super Effective!"
    description = 'Kill three enemies with a single grenade'

# More complicated ones:
class DestroyStars(KilledSomeoneAchievement, IncrementingAchievement,
        OnceEverPerPlayer):
    idstring = 'destroyStars'
    name = 'The Recession we Had to Have'
    description = 'Destroy 100 stars by killing the players carrying them'
    requiredQuantity = 100

    def killedSomeone(self, msg):
        self.increment(msg.stars)

class EarnStars(IncrementingAchievement, OnceEverPerPlayer):
    idstring = 'earnStars'
    name = 'Stimulus Package'
    description = 'Earn 100 stars'

    incrementTrigger = EarnStarTrigger
    requiredQuantity = 100
    messages = incrementTrigger.messages

class BuyEveryUpgrade(PersistedChecklistAchievement):
    idstring = 'buyEveryUpgrade'
    name = 'Technology Whiz'
    description = 'Use every upgrade at least once'
    requiredItems = set(u.upgradeType for u in allUpgrades)
    messages = (PlayerHasUpgradeMsg,)

    @checkPlayerId
    def gotPlayerHasUpgradeMsg(self, msg):
        self.addItem(msg.upgradeType)

class UseMinimapDisruption(OncePerPlayerPerGame):
    idstring = 'minimapDisruption'
    name = 'The Rader Appears to be... Jammed!'
    description = 'Use a minimap disruption'
    messages = (PlayerHasUpgradeMsg,)

    @checkPlayerId
    def gotPlayerHasUpgradeMsg(self, msg):
        if msg.upgradeType == 'm':
            self.achievementUnlocked()

class EarlyAbandon(OncePerPlayerPerGame):
    idstring = 'abandonEarly'
    name = 'Reduce, Reuse, Recycle'
    description = 'Abandon a turret or phase shift before it runs out'
    messages = (DeleteUpgradeMsg,)

    @checkPlayerId
    def gotDeleteUpgradeMsg(self, msg):
        '''
        Don't award if it was within 3 seconds of running out anyway.
        '''
        if (msg.deleteReason == 'A' and msg.upgradeType in 'th' and
                self.player.upgradeGauge >= 3):
            self.achievementUnlocked()

class GoodManners(OncePerPlayerPerGame):
    idstring = 'goodManners'
    name = 'Good Manners'
    description = 'Say "gg" after the game finishes'
    afterGame = True
    messages = (ChatMsg,)

    @checkPlayerId
    def gotChatMsg(self, msg):
        if msg.kind == 'o' and msg.text.decode().lower().strip() == 'gg':
            self.achievementUnlocked()

class DarkZoneKills(IncrementingAchievement, KilledSomeoneAchievement,
        OncePerPlayerPerGame):
    idstring = 'darkZoneKills'
    name = 'Behind Enemy Lines'
    description = "Kill five enemies when you're in a dark zone of their colour"
    requiredQuantity = 5

    def killedSomeone(self, msg):
        if self.player.team is None:
            return
        if (self.player.isEnemyTeam(self.player.currentZone.zoneOwner)
                and not self.player.ghost):
            self.increment()

class PhaseShiftAbsorb(IncrementingAchievement, OncePerPlayerPerGame):
    idstring = 'phaseShiftAbsorb'
    name = "Can't Touch This"
    description = 'Get hit by 30 bullets in a single phase shift'
    requiredQuantity = 30
    messages = (ShotAbsorbedMsg, DeleteUpgradeMsg)

    def gotShotAbsorbedMsg(self, msg):
        if (msg.targetId == self.player.id and self.player.upgrade is not None
                and self.player.upgrade.upgradeType == 'h'):
            self.increment()

    @checkPlayerId
    def gotDeleteUpgradeMsg(self, msg):
        if msg.upgradeType == 'h':
            self.reset()

class RicochetAchievement(KilledSomeoneAchievement, OncePerPlayerPerGame):
    name = 'Bouncy Flag'
    description = ('Kill an enemy with a bullet that has ricocheted at least '
            'once')
    idstring = 'ricochetKill'

    def killedSomeone(self, msg):
        try:
            shot = self.world.getShot(self.player.id, msg.shotId)
        except Abort:
            # This doesn't yet work, because the world deletes the shot before
            # we get here
            pass
        else:
            if shot.bounced:
                self.achievementUnlocked()

class KillEnemyWithStars(KilledSomeoneAchievement, OncePerPlayerPerGame):
    name = 'Stop Right There, Criminal Scum'
    description = 'Kill an enemy holding five stars or more'
    idstring = 'killEnemyWithStars'

    def killedSomeone(self, msg):
        if msg.stars >= 5:
            self.achievementUnlocked()

class KillAsRabbit(KilledSomeoneAchievement, OncePerPlayerPerGame):
    name = 'Never Surrender'
    description = 'Kill an enemy after losing a game'
    idstring = 'killAsRabbit'
    afterGame = True

    def killedSomeone(self, msg):
        if (self.player.team is not None and
                self.player.isEnemyTeam(self.world.winningTeam)):
            self.achievementUnlocked()

class RabbitKill(KilledSomeoneAchievement, OncePerPlayerPerGame):
    name = 'Icing on the Cake'
    description = 'Kill an enemy after winning a game'
    idstring = 'killRabbit'
    afterGame = True

    def killedSomeone(self, msg):
        if (self.world.winningTeam == self.player.team and
                self.player.isEnemyTeam(self.world.getPlayer(msg.targetId
                ).team)):
            self.achievementUnlocked()

class TurretKill(KilledSomeoneAchievement, OncePerPlayerPerGame):
    name = 'Sentry Mode Activated'
    description = 'Kill an enemy as a turret'
    idstring = 'turretKill'

    def killedSomeone(self, msg):
        if (self.player.upgrade is not None and self.player.upgrade.upgradeType
                == 't'):
            self.achievementUnlocked()

class FirstKill(OncePerGame):
    name = 'First Blood'
    description = 'Make the first kill of the game'
    idstring = 'firstKill'
    messages = (PlayerKilledMsg,)

    def gotPlayerKilledMsg(self, msg):
        if not self.unlocked:
            try:
                killer = self.world.getPlayer(msg.killerId)
            except Abort:
                return
            else:
                players = set([killer])
                self.achievementUnlocked(players)

class FirstTag(OncePerGame):
    name = 'Game On'
    description = 'Tag or assist in the tagging of the first zone in a game'
    idstring = 'firstTag'
    messages = (TaggingZoneMsg,)

    def gotTaggingZoneMsg(self, msg):
        if not self.unlocked:
            zone = self.world.getZone(msg.zoneId)
            team = self.world.getTeam(msg.teamId)
            helpers = set([])
            for player in zone.players:
                if player.team == team:
                    helpers.add(player)
            self.achievementUnlocked(helpers)

class LastTag(OncePerGame):
    name = 'And the Dirt is Gone'
    description = 'Tag or assist in the tagging of the final zone'
    idstring = 'finalTag'
    messages = (TaggingZoneMsg,)

    def gotTaggingZoneMsg(self, msg):
        team = self.world.getTeam(msg.teamId)

        if team and team.opposingTeam.numOrbsOwned == 0:
            zone = self.world.getZone(msg.zoneId)
            winners = set([])
            for player in zone.players:
                if player.team == team:
                    winners.add(player)
            self.achievementUnlocked(winners)

class Domination(KilledSomeoneAchievement, OncePerPlayerPerGame):
    name = 'Domination'
    description = 'Kill the same enemy five times in a single game'
    idstring = 'domination'
    requiredQuantity = 5

    def __init__(self, player, world, outPlug):
        super(Domination, self).__init__(player, world, outPlug)
        self.playerKills = defaultdict(int)

    def killedSomeone(self, msg):
        nick = self.world.getPlayer(msg.targetId).identifyingName
        self.playerKills[nick] += 1
        if self.playerKills[nick] == self.requiredQuantity:
            self.achievementUnlocked()

class MinimapDisruptionTag(OncePerPlayerPerGame):
    name = 'Tag in the Dark'
    description = 'Tag a zone while the enemy\'s minimap is disrupted'
    idstring = 'disruptionTag'
    messages = (TaggingZoneMsg,)

    @checkPlayerId
    def gotTaggingZoneMsg(self, msg):
        for player in self.world.players:
            if (player.team == self.player.team and player.upgrade is not None
                    and player.upgrade.upgradeType == 'm'):
                self.achievementUnlocked()
                break

class MutualKill(NoLimit):
    name = 'Eye for an Eye'
    description = 'Kill an enemy at the same time he kills you'
    idstring = 'mutualKill'
    messages = (PlayerKilledMsg, RespawnMsg, RemovePlayerMsg)

    def __init__(self, player, world, outPlug):
        super(MutualKill, self).__init__(player, world, outPlug)
        # Keep a record of the people we kill. If they kill us while they're
        # dead, achievement unlocked.  Similarly, keep a record of who killed
        # us. If we kill them while we're dead, achievement unlocked.
        self.ourKiller = None
        self.kills = set([])


    def gotPlayerKilledMsg(self, msg):
        if msg.targetId == self.player.id:
            self.ourKiller = msg.killerId
            if msg.killerId in self.kills:
                self.achievementUnlocked()
        elif msg.killerId == self.player.id:
            self.kills.add(msg.targetId)
            if msg.targetId == self.ourKiller:
                self.achievementUnlocked()

    def gotRespawnMsg(self, msg):
        if msg.playerId == self.player.id:
            self.ourKiller = None
        else:
            self.tryRemove(msg.playerId)

    def tryRemove(self, playerId):
        if playerId in self.kills:
            self.kills.remove(playerId)

    def gotRemovePlayerMsg(self, msg):
        self.tryRemove(msg.playerId)

class SnatchedZone(OncePerPlayerPerGame):
    idstring = 'snatched'
    name = 'Snatched from the Jaws'
    # This should not be awarded if the tagging team would have been able to tag
    # anyway
    description = 'Tag a zone just before an enemy was about to respawn in it'
    snatchTime = 0.5
    messages = (TaggingZoneMsg,)

    @checkPlayerId
    def gotTaggingZoneMsg(self, msg):
        zone = self.world.getZone(msg.zoneId)
        team = self.world.getTeam(msg.teamId)

        almostDefenders = 0
        for ghost in zone.nonPlayers:
            assert ghost.ghost
            if ghost.team != team and ghost.respawnGauge < self.snatchTime:
                almostDefenders += 1
        actualDefenders = 0
        actualAttackers = 0
        for player in zone.players:
            if player.team == team:
                actualAttackers += 1
            else:
                if not player.turret:
                    actualDefenders += 1
        if (not ZoneState.canTag(actualAttackers, actualDefenders +
                almostDefenders) and zone.previousOwner is not None):
            # Couldn't have tagged if we'd been half a second later
            self.achievementUnlocked()

class KilledByNobody(KilledSomeoneAchievement, OncePerPlayerPerGame):
    name = 'And Who Deserves the Blame?'
    description = 'Die with no-one being awarded a kill'
    idstring = 'killedByNobody'
    messages = (PlayerKilledMsg,)

    def gotPlayerKilledMsg(self, msg):
        if msg.targetId == self.player.id and msg.killerId == '\x00':
            self.achievementUnlocked()

class ShieldRevenge(OncePerPlayerPerGame):
    name = 'Shields Up, Weapons Online'
    description = 'Kill the enemy who shot your shield within ten seconds'
    idstring = 'shieldRevenge'

    timeWindow = 10 # Seconds
    messages = (ShotAbsorbedMsg, PlayerKilledMsg)

    def __init__(self, player, world, outPlug):
        super(ShieldRevenge, self).__init__(player, world, outPlug)
        self.shieldKillers = []

    def gotShotAbsorbedMsg(self, msg):
        if msg.targetId == '\x00':
            return
        if (msg.targetId == self.player.id and self.player.upgrade is not None
                and self.player.upgrade.upgradeType == 's'):
            # Our shield got hit
            self.shieldKillers.append((self.world.getGameTime(),
                    self.world.getPlayer(msg.shooterId)))

    def gotPlayerKilledMsg(self, msg):
        if msg.killerId == self.player.id:
            self.killedSomeone(msg)
        elif msg.targetId == self.player.id:
            self.gotKilled(msg)

    def gotKilled(self, msg):
        self.shieldKillers = []

    def killedSomeone(self, msg):
        target = self.world.getPlayer(msg.targetId)
        currentTime = self.world.getGameTime()
        for time, attacker in list(self.shieldKillers):
            if currentTime - time > self.timeWindow:
                self.shieldKillers.remove((time, attacker))
            elif attacker == target:
                self.achievementUnlocked()
                break

class ShieldThenKill(OncePerPlayerPerGame):
    name = 'Armour-Piercing Bullets'
    description = 'Kill an enemy after destroying their shields'
    idstring = 'destroyShield'

    timeWindow = 10 # Seconds
    messages = (ShotAbsorbedMsg, PlayerKilledMsg)

    def __init__(self, player, world, outPlug):
        super(ShieldThenKill, self).__init__(player, world, outPlug)
        self.shieldsKilled = []

    def gotShotAbsorbedMsg(self, msg):
        if msg.targetId == '\x00':
            return
        target = self.world.getPlayer(msg.targetId)
        if (msg.shooterId == self.player.id and target.upgrade is not None and
                target.upgrade.upgradeType == 's'):
            # We hit their shield
            self.shieldsKilled.append((self.world.getGameTime(), target))

    def gotPlayerKilledMsg(self, msg):
        if msg.targetId == self.player.id:
            self.gotKilled(msg)
        elif msg.killerId == self.player.id:
            self.killedSomeone(msg)

    def gotKilled(self, msg):
        self.shieldsKilled = []

    def killedSomeone(self, msg):
        target = self.world.getPlayer(msg.targetId)
        currentTime = self.world.getGameTime()
        for time, victim in list(self.shieldsKilled):
            if currentTime - time > self.timeWindow:
                self.shieldsKilled.remove((time, victim))
            elif victim == target:
                self.achievementUnlocked()
                break

class LastManStanding(OncePerTeamPerGame):
    name = 'Never Give Up'
    description = 'Be the last surviving member of your team'
    idstring = 'surviveLast'
    afterGame = True
    messages = (PlayerKilledMsg, GameOverMsg)

    def __init__(self, world, team, outPlug):
        super(LastManStanding, self).__init__(world, team, outPlug)

    def gotPlayerKilledMsg(self, msg):
        self.check()
    def gotGameOverMsg(self, msg):
        self.check()

    def check(self):
        remaining = []
        for player in self.world.players:
            if player.team == self.team:
                remaining.append(player)
        if len(remaining) == 1:
            self.achievementUnlocked([remaining[0]])

##################
# Leader Killing #
##################
leaderAchievements = {'kjohns': 'Vespene Geyser Exhausted',
    'jbartl': 'The Bigger They Are...', 'mwalla': "School's Out",
    'jredmo': 'Kernel Panic', 'tirwin': 'Uncomfortably Energetic',
    'dmengl': "Trolling Ain't Easy", 'shorn': 'Employee of the Month',
    'adonal': 'Drum Solo', 'dcatch': 'Jerakeen Genocide',
    'jowen': 'Zergling Rush', 'lsharl': 'Knight of Catan'}

additionalLeaders = {
    'gsearl': 'Galapagos',
    'dholme': 'Jyolanar',
    'mdaman': 'MaZ',
}
leaderAchievements = additionalLeaders = {} # We are not on camp.

def getLeaderDescription(name):
    return 'Kill %s three times in a single game' % (name,)
def stripPunctuation(nick):
    exclude = set(string.punctuation + ' ')
    return ''.join(ch for ch in nick if ch not in exclude)

class LeaderMultiKill(KilledSomeoneAchievement, IncrementingAchievement,
        OnceEverPerPlayer):
    requiredQuantity = 3
    def __init__(self, player, world, outPlug, leaderName, achievementName):
        self.idstring = 'leader' + stripPunctuation(leaderName)
        super(LeaderMultiKill, self).__init__(player, world, outPlug)
        self.leaderName = leaderName
        self.name = achievementName
        self.description = getLeaderDescription(self.leaderName)

    def killedSomeone(self, msg):
        player = self.world.getPlayer(msg.targetId)
        if player.user is None:
            return
        nick = stripPunctuation(player.user.username)
        if nick.lower() == self.leaderName.lower():
            self.increment()


def lower(string):
    return string.lower()

class KillEveryLeader(KilledSomeoneAchievement, PersistedChecklistAchievement):
    idstring = 'killEveryLeader'
    name = 'Leaders vs Campers'
    description = 'Kill every leader at least once'
    requiredItems = set(map(stripPunctuation,
                            map(lower, leaderAchievements.keys()
                                    + additionalLeaders.keys())))

    def killedSomeone(self, msg):
        player = self.world.getPlayer(msg.targetId)
        if player.user is None:
            return
        nick = stripPunctuation(player.user.username).lower()
        if nick in self.requiredItems:
            self.addItem(nick)

concreteAchievements = (MultiTagSmall, MultiTagMedium, MultiTagLarge,
    TotalTagsSmall, TotalTagsMedium, MultiKillSmall, MultiKillMedium,
    MultiKillLarge, TotalKillsSmall, TotalKillsMedium, ShoppingSpree,
    SmartShopper, FirstTag, KillEnemyWithStars, RicochetAchievement, FirstKill,
    Domination, DestroyStars, EarnStars, BulletsSmall, BulletsMedium,
    AssistTags, KillAsRabbit, RabbitKill, UseMinimapDisruption, BuyEveryUpgrade,
    KillEveryLeader, MutualKill, GrenadeMultiKill, QuickKillSmall,
    QuickKillMedium, SnatchedZone, TurretKill, PhaseShiftAbsorb, EarlyAbandon,
    GoodManners, MinimapDisruptionTag, LastTag, DarkZoneKills, KilledByNobody,
    ShieldRevenge, ShieldThenKill, LastManStanding)

achievementDict = {}
for achv in concreteAchievements:
    achievementDict[achv.idstring] = achv
for idstring, name in leaderAchievements.iteritems():
    achievementDict['leader'+idstring] = (lambda player, world, outPlug,
            idstring=idstring, name=name: LeaderMultiKill(player, world,
            outPlug, idstring, name))


# Get the name and description, given an idstring
def getAchievementDetails(idstring):
    for achievementClass in concreteAchievements:
        if achievementClass.idstring == idstring:
            if achievementClass.name == "":
                return idstring, achievementClass.description
            else:
                return achievementClass.name, achievementClass.description
    for leaderName, achievementName in leaderAchievements.iteritems():
        if 'leader'+leaderName == idstring:
            return achievementName, getLeaderDescription(leaderName)
    return None, None
