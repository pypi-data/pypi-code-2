# -*- coding: utf-8 -*-

# author: marc goetz

# import for time()
import time
# import for getLogger()
import logging
# import for urlencode()
import urllib

# import for object BrowserView
from Products.Five.browser import BrowserView

# import for cache_key
from plone.memoize import ram

# import for StringTypes
from types import StringTypes

# import of the armory-API, for getCharacter()
from armory_api import Armory

# import of the activity-API, for get_activity()
from activity_api import Activity

# initialising an armory-object
armory = Armory()

# initialising an activity-object
activity = Activity()

# initialising a standard-character-object
raider = armory.getCharacter(raiderName="Kutschurft", raiderServer="Azshara", raiderZone="EU", language="en")

# initialising a standard-activity-object
activities = activity.get_activity("Kutschurft","Azshara","EU", "en", 6)

# initialising the logger
logger = logging.getLogger("collective.wowcharacter")

# class WoWCharacter for CustomView
class WoWCharacter(BrowserView):

    def __init__(self, context, request):

        super(WoWCharacter, self).__init__(context, request)
        self.context = context
        self.request = request

        self.name = self.context.name
        self.realm = self.context.realm
        self.zone = self.context.zone

        self.data = self.make_char(self.name, self.realm, self.zone, request['LANGUAGE'][:2])

    def armory_error(self):

        if not self.data:
            return False
        else:
            return True

    def cache_key(fun, self, name, realm, zone, language):
        """ cache for 5 seconds """

        key = "_".join([name, realm, zone, str(time.time() // 5)])

        logger.debug("cache_key::key=%s" % key)

        return key

    def wow(self):

        return "WoW is awesome ^_^"

    def css_class(self):
        """ returns the css class depending on the faction """

        return self.context.faction

    def char_arena_teams(self):
        """ get the arena teams out of the data """

        data = self.data

        # if empty returns [{}, {}, ...., {}]
        # else returns a list of dictionaries
        # something like
        # [{'name': u'John is back', 'ranking': 15190, 'rating': 757, 'size': 2}]
        arena_teams = data.get("arena_teams")

        for slot in arena_teams:
            # returns something like "2v2: John is back, rated @ 757, ranked @ 15190"
            arena_team = str(slot.get("size")) + "v" + str(slot.get("size")) + ": " + slot.get("name") + ", rated @ " + str(slot.get("rating")) + ", ranked @ " + str(slot.get("ranking"))

            yield dict(arena_team = arena_team)

    def char_talents(self):
        """ get the talent-spec out of the data """

        data = self.data

        keys = "spec1 spec2 spec1icon spec2icon".split()
        talentspec = dict.fromkeys(keys)

        specicon_base_url = "http://eu.wowarmory.com/wow-icons/_images/43x43/"

        # if empty returns [0, 0, 0, 0, 0]
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

    def char_glyphs(self):

        data = self.data

        # if empty returns [{}, {}, ...., {}]
        # else returns a list of dictionaries
        # something like
        # [{'effect': u'Reduces the cooldown of Penance by 2 sec.',
        #   'name': u'Glyph of Penance',
        #   'type': u'major'}]
        glyphs = data.get("glyphs")

        # the glyphs are always for the currently active spec
        for slot in glyphs:
            # returns something like "major Glyph of Penance:<br> Reduces the cooldown of Penance by 2 sec."
            glyph =  slot.get("type") + " " + slot.get("name") + ":<br> " + slot.get("effect")

            #there can be 0 to 6 glyphs
            yield dict(glyph = glyph)

    def char_activity(self):
        """ get the recent activities of the caracter """

        # returns something like
        # ['Has now completed [Victories over the Lich King (Icecrown 10 player)] 4 times.',
        #  'Earned the achievement [Neck-Deep in Vile (10 player)].',
        #  'Has now completed [Sindragosa kills (Heroic Icecrown 10 player)] 2 times.',
        #  'Has now completed [Valithria Dreamwalker rescues (Heroic Icecrown 10 player)] 4 times.',
        #  'Has now completed [Blood Queen Lana'thel kills (Heroic Icecrown 10 player)] 6 times.']
        activities = activity.get_activity(self.name, self.realm, self.zone, self.request['LANGUAGE'][:2], 6)

        for slot in activities:

            yield dict(activity = slot)

    def char_activity_feed(self):

        image = "++resource++collective.wowcharacter.images/rss.png"
        # returns something like "http://eu.wowarmory.com/character-feed.atom?r=Azshara&cn=Kutschurft&locale=en_GB"
        url = "http://" + self.zone + ".wowarmory.com/character-feed.atom?r=" + self.realm + "&cn=" + self.name

        if self.request["LANGUAGE"][:2] == "de":
            url = url + "&locale=de_DE"
        if self.request["LANGUAGE"][:2] == "en":
            url = url + "&locale=en_GB"

        return dict(image = image,
                    url = url)

    def char_professions(self):
        """ get the professions out of the data """

        data = self.data

        keys = "profession1 profession2".split()

        profession = dict.fromkeys(keys)

        # if empty returns [{}, {}, ...., {}]
        # else returns a list of dictionaries
        # something like
        # [{'key': u'engineering', 'max': 450, 'name': u'Engineering', 'value': 450}]
        professions = data.get("professions")

        # there can be 0 to 2 professions per character
        # make sure there is at least 1 profession
        if professions[0] != {}:
            # returns something like "Engineering @ 450"
            profession["profession1"] = professions[0].get("name") + " @ " + str(professions[0].get("value"))
        else:
            profession["profession1"] = "N/A"
        if professions[1] != {}:
            profession["profession2"] = professions[1].get("name") + " @ " + str(professions[1].get("value"))
        else:
            profession["profession2"] = "N/A"

        return profession

    def char_secondary_professions(self):
        """ get the secondary professions out of the data """

        data = self.data

        # if empty returns [{}, {}, ...., {}]
        # else returns a list of dictionaries
        # something like
        # [{'name': u'Cooking', 'value': 300}]
        secondary_professions = data.get("secondary_professions")

        for slot in secondary_professions:
            # returns something like "Cooking @ 450"
            secondary_profession = slot.get("name") + " @ " + str(slot.get("value"))

            # there can be 0 to 4 secondary professions
            yield dict(secondary_profession = secondary_profession)

    def char_equip(self):
        """ get the equip out of the data (with icons + ids) """

        data = self.data

        # returns list of dictionaries
        equip = data.get("items")

        item_base_url_de = "http://de.wowhead.com/item="
        item_base_url_en = "http://www.wowhead.com/item="
        icon_base_url = "http://static.wowhead.com/images/wow/icons/large/"

        for slot in equip:
            if self.request["LANGUAGE"][:2] == "de":
                item_url = "".join([item_base_url_de, str(slot.get("id"))])
            if self.request["LANGUAGE"][:2] == "en":
                item_url = "".join([item_base_url_en, str(slot.get("id"))])


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
    def make_char(self, name, realm, zone, language):
        """ uses the armory-API  """

        logger.info("character data::name=%s, realm=%s, zone=%s" % (name, realm, zone))

        try:
            return armory.getCharacter(raiderName=name, raiderServer=realm, raiderZone=zone,language=language)
        except Exception, e:
            return dict()

# vim: set ft=python ts=4 sw=4 expandtab :
