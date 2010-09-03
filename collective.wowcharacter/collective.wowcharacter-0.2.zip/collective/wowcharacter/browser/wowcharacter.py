# -*- coding: utf-8 -*-

# author: marc goetz

# import for time()
import time
# import for getLogger()
import logging
# import for urlencode()
import urllib
# import for SocketError
from socket import error as SocketError

# import for object BrowserView
from Products.Five.browser import BrowserView

# import for cache_key
from plone.memoize import ram

# import for StringTypes
from types import StringTypes

# import of the armory-API, for getCharacter()
from armory_api import Armory

# initialising an armory-object
armory = Armory()

# initialising a standard-character-object
raider = armory.getCharacter(raiderName="Kutschurft",raiderServer="Azshara",raiderZone="EU")

# initialising the logger
logger = logging.getLogger("inquant.wow")

# class WoWCharacter for CustomView
class WoWCharacter(BrowserView):

    def __init__(self, context, request):

        super(WoWCharacter, self).__init__(context, request)
        self.context = context
        self.request = request

        name = self.context.name
        realm = self.context.realm
        zone = self.context.zone

        self.data = self.make_char(name, realm, zone)

    def cache_key(fun, self, name, realm, zone):
        """ cache for 5 seconds """

        key = "_".join([name, realm, zone, str(time.time() // 5)])

        logger.debug("cache_key::key=%s" % key)

        return key

    def wow(self):

        return "WoW is awesome ^_^"

    def css_class(self):
        """ returns the css class depending on the faction """

        return self.context.faction

    def char_talents(self):
        """ get the talent-spec out of the data """

        data = self.data

        keys = "spec1 spec2 spec1icon spec2icon".split()
        talentspec = dict.fromkeys(keys)

        specicon_base_url = "http://eu.wowarmory.com/wow-icons/_images/43x43/"

        # if empty, returns [0, 0, 0, 0, 0]
        # else returns something like [15, 56, 0, 'Enhancement', 'spell_nature_lightningshield']
        talents1 = data.get("talents1")
        talents2 = data.get("talents2")

        # returns something like 15/56/0
        score1 = "/".join([str(t) for t in talents1[0:3]])
        # returns something like Enhancement 15/56/0
        talentspec["spec1"] = " ".join([talents1[3], score1])
        # spec icons are always png's
        # returns something like spell_nature_lightningshield.png
        icon1 = ".".join([talents1[4], "png"])
        icon1_url = "".join([specicon_base_url, icon1])
        talentspec["spec1icon"] = icon1_url

        # make sure there is a second spec
        if type(talents2[3]) in StringTypes:
            score2 = "/".join([str(t) for t in talents2[0:3]])
            talentspec["spec2"] = " ".join([talents2[3], score2])
            icon2 = ".".join([talents2[4], "png"])
            icon2_url = "".join([specicon_base_url, icon2])
            talentspec["spec2icon"] = icon2_url
        else:
            talentspec["spec2"] = "N/A"
            talentspec["spec2icon"] = ""

        return talentspec

    def char_professions(self):
        """ get the professions out of the data """

        data = self.data

        keys = "profession1 profession2".split()

        profession = dict.fromkeys(keys)

        # returns list of dictionaries
        professions = data.get("professions")

        # there can be 0 or max. 2 professions per character
        if professions[0] != {}:
            profession["profession1"] = professions[0].get("name") + " @ " + str(professions[0].get("value")) + "/450"
        else:
            profession["profession1"] = "N/A"
        if professions[1] != {}:
            profession["profession2"] = professions[1].get("name") + " @ " + str(professions[1].get("value")) + "/450"
        else:
            profession["profession2"] = "N/A"

        return profession

    def char_equip(self):
        """ wow character equip ids+icons """

        data = self.data

        # returns list of dictionaries
        equip = data.get("items")

        item_base_url = "http://www.wowhead.com/item="
        icon_base_url = "http://static.wowhead.com/images/wow/icons/large/"

        for slot in equip:
            item_url = "".join([item_base_url, str(slot.get("id"))])

            # equip icons are always jpg's
            # returns something like inv_helmet_148.jpg
            icon = ".".join([slot.get("icon"), "jpg"])
            icon_url = "".join([icon_base_url, icon])

            # there is always just 1 enchant per item
            enchant = "".join(["ench=", str(slot.get("permanentenchant"))])
            # and always max. 3 gems
            gem = slot.get("gems")
            gems = ":".join(["".join(["gems=", str(gem[0])]), str(gem[1]), str(gem[2])])

            # returns something like ench=1234;gems=12345:12345:12345
            ench_gems = ";".join([enchant, gems])

            # there can be 0 to 19 items per character
            yield dict(item_url = item_url,
                       icon_url = icon_url,
                       ench_gems = ench_gems)

    def char_data(self):
        """ wow character data like name, realm, class, equip, professions etc. """

        data = self.data

        keys = "guild race class sex battlegroup prefix suffix name level lifetimehonorablekills points".split()

        out = dict()
        for key in keys:
            out[key] = data.get(key, "N/A")

        talents = self.char_talents()
        professions = self.char_professions()

        out.update(talents)
        out.update(professions)

        return out

    @ram.cache(cache_key)
    def make_char(self, name, realm, zone):
        """ uses the armory.py api """

        logger.info("make_char::name=%s, realm=%s, zone=%s" % (name, realm, zone))

        try:
            return armory.getCharacter(raiderName=name,raiderServer=realm,raiderZone=zone)
        except SocketError:
            return dict()

# vim: set ft=python ts=4 sw=4 expandtab :
