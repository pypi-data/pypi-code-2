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

import sys
import os
import operator

from trosnoth.data import getPath, user, makeDirs
from trosnoth.src.utils.jsonImport import json
from trosnoth.src.utils.utils import hasher
import trosnoth.data.statGeneration as statGeneration

def generateHtml(htmlPath, statPath):

    def plural(value):
        if value == 1:
            return ""
        else:
            return "s"

    def add(value, statName = None, altText = None, spacing = True):
        if altText is not None:
            points = pointValues[altText] * value
            if type(points) == float:
                points = '%2.2f' % points
            altText = ' title="%s point%s\"' % (points, plural(points))
        else:
            altText = ''

        if type(value) == float:
            value = '%2.2f' % value    

        if statName is None:
            html.append("\t\t\t\t<td%s>%s</td>" % (altText, value))
        else:
            nbsp = ""
            if spacing is False:
                pluralStr = ""
            else:
                nbsp = "&nbsp;"
                pluralStr = plural(value)
            html.append("\t\t\t\t<td%s>%s%s%s%s</td>" % (altText, value, nbsp, statName, pluralStr))

    def addList(title, data):
        html.append("\t\t\t\t\t<li><b>%s:</b> " % title)

        if len(data) == 0:
            html.append("\t\t\t\t\t\tNone")
        else:
            data = sorted(data.iteritems(), key=operator.itemgetter(1), reverse = True)
            string = []
            for details in data:
                string.append("%s (%d)" % details)
            html.append("\t\t\t\t\t\t"+", ".join(string))
            
        html.append("\t\t\t\t\t</li>")

    def accuracy(shotsHit, shotsFired):
        try:
            return ((shotsHit ** 2) / (shotsFired + 0.0)) * 30
        except ZeroDivisionError:
            return 0

    from trosnoth.src.gamerecording.gamerecorder import statDir        

    makeDirs(statDir)

    if statPath == '':
        files = os.listdir(statDir)
    else:
        files = [statPath]

    stats = {}
    statNames = ['aliveStreak', 'deaths', 'killStreak', 'kills',
                 'killsAsRabbit', 'rabbitStreak', 'rabbitsKilled',
                 'roundsLost', 'roundsWon', 'shotsFired', 'shotsHit',
                 'starsEarned', 'starsUsed',
##                 'starsWasted',
                 'tagStreak',
                 'timeAlive', 'timeDead', 'timeRabbit', 'zoneAssists',
                 'zoneTags']
    statEnemies = ['playerDeaths', 'playerKills', 'upgradesUsed']
    pointValues = {'kills': 10, 'deaths': 1, 'zoneTags': 20, 'accuracy': 20,
                   'starsUsed': 3, 'zoneAssists': 5}
    leaders = []    # For camp only

    tableHeaders = [['#', 'Nick', 'Kills', 'Deaths', 'KDR', 'Zone Tags',
                     'Shots Fired', 'Shots Hit', 'Accuracy', 'Stars Used',
                     'Killed the most:', 'Died the most to:', 'Points'],
                    ['#', 'Nick', 'Stars Earned', 'Stars Used',
                     'Favourite Upgrade', 'Time Alive', 'Time Dead', 'ADR',
                     'Longest Life', 'Points'],
                    ['#', 'Nick', 'Kills', 'Kill Streak', 'Rabbits Killed',
                     'Zone Tags', 'Zone Assists', 'Tag Streak', 'Points'],
                    ['#', 'Nick', 'Shots Fired', 'Shots Hit', 'Accuracy',
                     'Old Score', 'New Score', 'Difference', 'Points']]
    
    tableNames = ['General Overview', 'Stars and Time', 'Kills and Tags', 'Accuracy Beta']

    for x in range(0, len(tableNames)):
        style = ""
        if x == 0:
            style = " style='color: black;'"
        tableNames[x] = '<span class="name topLink" id="link%s" onClick="navigate(\'%s\', %d)"%s>%s</span>' % \
                        (x, x, len(tableHeaders[x]), style, tableNames[x])
        
    navigation = " &ndash; ".join(tableNames)
    
    html = []
    fileMatrix = {}

    for filename in files:

        if filename[-9:] != ".trosstat":
            filename = filename + ".trosstat"
        statLocation = os.path.join(statPath, filename)
        
        try:
            statFile = open(statLocation)
        except IOError:
            raise Exception("'%s' does not exist!" % filename)

        loadedStats = json.load(statFile)

        for nick in loadedStats:
            if nick not in stats:
                stats[nick] = loadedStats[nick]
                fileMatrix[nick] = [filename]
            else:
                for stat in statNames:
                    stats[nick][stat] += loadedStats[nick][stat]
                for stat in statEnemies:
                    for enemy in loadedStats[nick][stat]:
                        if enemy not in stats[nick][stat]:
                            stats[nick][stat][enemy] = 0
                        stats[nick][stat][enemy] += loadedStats[nick][stat][enemy]
                fileMatrix[nick].append(filename)

    ranking = {}
    allData = {}

    for nick in stats:
        data = stats[nick]
        try:
            data['accuracy'] = float(data['shotsHit']) / float(data['shotsFired']) * 100.0
        except ZeroDivisionError:
            data['accuracy'] = 0

        for stat in statEnemies:
            data[stat + "Full"] = data[stat].copy()
            highest = 0
            highestName = "----"
            names = data[stat]
            for k, v in names.items():
                if v > highest:
                    highest = v
                    highestName = k
            if highest == 0:
                data[stat] = highestName
            else:
                data[stat] = "%s (%s)" % (highestName, highest)

        data['score'] = 0
        for stat, value in pointValues.items():
            points = data[stat] * value
            data['score'] += points

        try:
            data['kdr'] = '%2.2f' % (float(data['kills']) / float(data['deaths']))
        except ZeroDivisionError:
            data['kdr'] = "----"

        try:
            data['adr'] = '%2.2f' % (float(data['timeAlive']) / float(data['timeDead']))
        except ZeroDivisionError:
            data['adr'] = "----"

        ranking[nick] = data['score']
        allData[nick] = data

    rankingList = sorted(ranking.iteritems(), key=operator.itemgetter(1), reverse = True)
    ranking = {}

    rankCount = 0

    html.append("\t\t<table class='ladder'>");

    for count in range(0, len(tableNames)):
        style = ""
        if count != 0:
            style = " style='display: none;'"
        html.append("\t\t\t<tr class='allRows group%s'%s>" % (count, style))
        for caption in tableHeaders[count]:
            html.append("\t\t\t\t<th>%s</th>" % caption)
        html.append("\t\t\t</tr>")

    for pair in rankingList:

        nick = pair[0]
        rankCount += 1
        rankStr = str(rankCount)

        classy = ""
        if nick in leaders:
            classy = " leader";
            rankCount -= 1
            rankStr = '--'
        
        data = allData[nick]

        nickHash = hasher(nick).hexdigest()

        for count in range(0, len(tableNames)):

            style = ""
            if count != 0:
                style = " style='display: none;'"
            
            html.append("\t\t\t<tr class='allRows group%s%s'%s>" % (count, classy, style))
            
            add('<strong>%s</strong>' % rankStr)
            add('<span class="name" onClick="toggle(\'details-%s\')">%s</span>' % (nickHash, nick))
                
            if count == 0:
                add(data['kills'], 'kill', 'kills')
                add(data['deaths'], 'death', 'deaths')
                add(data['kdr'])
                add(data['zoneTags'], 'tag', 'zoneTags')
                add(data['shotsFired'], 'shot')
                add(data['shotsHit'], 'shot')
                add(data['accuracy'], '%', 'accuracy', False)
                add(data['starsUsed'], 'star', 'starsUsed')
                add(data['playerKills'])
                add(data['playerDeaths'])
            elif count == 1:
                add(data['starsEarned'], 'star')
                add(data['starsUsed'], 'star', 'starsUsed')
##                add(data['starsWasted'], 'star')
                add(data['upgradesUsed'])
                add(int(data['timeAlive']), 'second')
                add(int(data['timeDead']), 'second')
                add(data['adr'])
                add(int(data['aliveStreak']), 'second')
            elif count == 2:
                add(data['kills'], 'kill', 'kills')
                add(data['killStreak'], 'kill')
                add(data['rabbitsKilled'], 'rabbit')
                add(data['zoneTags'], 'tag', 'zoneTags')
                add(data['zoneAssists'], 'assist', 'zoneAssists')
                add(data['tagStreak'], 'zone')
            elif count == 3:
                add(data['shotsFired'], 'shot')
                add(data['shotsHit'], 'shot')
                add(data['accuracy'], '%', spacing = False)
                old = data['accuracy'] * 20
                new = accuracy(data['shotsHit'], data['shotsFired'])
                add(old, 'point')
                add(new, 'point')
                add(new - old)
                
            add('<strong>%2.2f</strong>' % data['score'])            
            html.append("\t\t\t</tr>")

            if count == len(tableNames) - 1:
                html.append("\t\t\t<tr id='details-%s' style='display: none;'>" % nickHash)
                html.append("\t\t\t\t<td colspan='%d' class='details' style='text-align: left;'>" % len(tableHeaders[0]))
                html.append("\t\t\t\t\t<ul>")

                addList("Players killed", data['playerKillsFull'])
                addList("Players died to", data['playerDeathsFull'])
                addList("Upgrades used", data['upgradesUsedFull'])
                    
                html.append("\t\t\t\t\t</ul>")
                html.append("\t\t\t\t</td>")
                html.append("\t\t\t</tr>")
        
    html.append("\t\t</table>")

    html = "\n" + "\n".join(html) + "\n"
    
    baseHTML = open(getPath(statGeneration, 'statGenerationBase.htm'), 'r').read()

    html = baseHTML.replace("[[TABLE]]", html)
    html = html.replace("[[NAVIGATION]]", navigation)

    htmlFile = open(htmlPath, "w")
    htmlFile.write(html)
    htmlFile.flush()
    htmlFile.close()

# Uncomment these lines and hit F5 for temporary testing of stat files
#import webbrowser
#generateStats(raw_input("Enter filename without extension (or just hit Enter): "))
#generateStats("Grommit's game (4)")
#webbrowser.open(getPath(user, 'stats.htm'))
