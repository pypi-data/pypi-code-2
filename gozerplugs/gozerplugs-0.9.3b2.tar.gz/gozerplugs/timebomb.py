# gozerplugs/timebomb.py
#
# Gozerbot Timebomb plugin v1.1 by Clone 2009 
# Idea not so loosely based on jotham.read@gmail.com's eggdrop timebomb 

""" do the timebomb dance. """

__copyright__ = 'BSD'
__author__ = 'clone at magtar.org'
__depend__ = ['ops', ]

from gozerbot.generic import getwho
from gozerbot.commands import cmnds
from gozerbot.plughelp import plughelp
from gozerbot.persist.persist import PlugPersist
from gozerbot.aliases import aliasset

from time import sleep, time
from random import randint, shuffle

plughelp.add('timebomb', 'blow your buddies to smithereens !timebomb <victim>')
plughelp.add('cut', 'try to defuse a bomb placed with !timebomb by cutting a wire i.e. !cut blue')

# define plugpersist outside localscope, you only want to initiate it once.
bomb = PlugPersist('bomb')
bomb.data = []

# Adjustable variables
wires = ['blue','black','red','green','purple','white','silver']
kickchance = 80


def timebomb(bot, ievent):
    # check if we have ops
    if ievent.channel not in bot.state['opchan']:
        bot.action(ievent.channel, "bends over and farts in %s's general direction." % ievent.nick)
        return
    # check if we are already running a bomb
    if bomb.data:
        bot.action(ievent.channel ,"points at the bulge in %s's pants." % bomb.data[0])
        return
    try:
        userhost = getwho(bot, ievent.args[0])
    except IndexError:
        ievent.reply('timebomb requires victim, see !help timebomb.')
        return
    # check if the victim userhost exists on this channel
    if not userhost:
         ievent.reply('no %s here.' % ievent.args[0])
         return
    else:
        user = ievent.args[0]
    # if bot gets targeted, switch target to caller
    if ievent.args[0].lower() == bot.nick.lower():
         userhost = ievent.ruserhost 
         user = ievent.nick
    # determine number of wires and pick random colors
    shuffle(wires)
    mywires = wires[0:randint(3,len(wires)-1)]
    counter = 18 + 2 * len(mywires) + randint(1,12)
    # determine time to mark instance
    instancetime = time()
    # plant bomb: (name to kick, which wires to choose from, which wire disarms, userhost)
    bomb.data = [user, mywires, mywires[randint(0,len(mywires)-1)], userhost, counter, [], instancetime]
    wires_pretty = ", ".join(map(str, mywires))
    ievent.reply('%s places a bomb in %s\'s pants, the timer reads %s seconds. You see the wires %s.' % (ievent.nick, user, counter, wires_pretty))
    # wait for timer to expire
    sleep(counter)
    
    # check if persist data still exists (no cut event) and kick if so.
    if bomb.data:
        # data from different instance, dont cut
        if not bomb.data[-1] == instancetime:
           return
        else: 
            #kick victim
            bot.sendraw('KICK %s %s :%s' % (ievent.channel, bomb.data[0], 'B000000M!'))
            #ievent.reply('user: %s, userhost: %s' % (bomb.data[0], bomb.data[3]))
            bomb.data = []

def cut(bot, ievent):
    # check if there is a timebomb running
    if bomb.data:
        # right userhost?
        if bomb.data[3] == ievent.ruserhost:
            # right wire?
            if ievent.args[0] == bomb.data[2]:
                bomb.data=[]
                ievent.reply('%s has defused the bomb.' % ievent.nick)
            elif ievent.args[0] in bomb.data[5]:
            	ievent.reply('you already cut that wire, moron')      
            elif ievent.args[0] not in bomb.data[1]:
                ievent.reply('you don\'t see the %s wire, now do you?' % ievent.args[0]) 
            else:
                chance = randint(1,100)
                if (chance < kickchance):
		    msgnr = randint(1,4) 
		    if msgnr == 1:
                	message = 'no idiot, it was %s... *BOOOOOOOOOOM!*' % bomb.data[2] 
		    if msgnr == 2:
                	message = 'snip...B000000000M!'
		    if msgnr == 3:
                        message = 'snip...kadeng kadeng, kadeng kadeng... *PLof*'
		    if msgnr == 4:
                        message = 'no, %sKABOOOOOOOM!..' % bomb.data[2][0:3]
                    bot.sendraw('KICK %s %s :%s' % (ievent.channel, bomb.data[0], message))
                    bomb.data=[]
		else:
		    msgnr = randint(4,5) 
		    if msgnr == 4:
                	message = 'the force compells you to choose differently..'
		    if msgnr == 5:
                        timetogo = bomb.data[4] - (time() - bomb.data[-1])
                	message = 'nothing happens, %d seconds to go!' % timetogo 
                        bomb.data[5].append(ievent.args[0])
                    ievent.reply(message)
                    return
            
cmnds.add('timebomb', timebomb, 'OPER', threaded=True)
aliasset('tb', 'timebomb')
cmnds.add('cut', cut, 'USER', threaded=True)
