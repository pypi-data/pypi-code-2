# -*- coding: utf-8 -*-
import datetime
import multiprocessing
import threading

#from agatsuma import log, Spell, Implementations

from agatsuma.interfaces import AbstractSpell

from settings_meta import SettingsMeta
from loggers import log

def fix_string_type(obj, expected_type):
    str_types = [unicode, str]
    if type(obj) in str_types and expected_type in str_types:
        return expected_type(obj)
    else:
        return obj

class Settings(object):
    __metaclass__ = SettingsMeta
    settings = {}

    @staticmethod
    def load_cfg_data(config_data, descriptors):
        Settings.process_settings(config_data, descriptors)

    @staticmethod
    def process_settings(settings, descriptors):
        settings = Settings.provider.load(settings)
        problems = []
        newsettings = {}
        rosettings = {}
        types = {}
        comments = {}
        actual = 0
        rocount = 0
        for group, name, ro, stype, comment in descriptors.values():
            if not group in settings:
                problems.append("Group '%s' (%s) not found in settings" %
                                (group, comment))
                continue
            groupDict = settings[group]
            if not name in groupDict:
                problems.append("Setting '%s' (%s) not found in group '%s'" %
                                (name, comment, group))
                continue
            value = fix_string_type(groupDict[name], stype)

            rstype = type(value)
            fullname = '%s.%s' % (group, name)
            if rstype != stype:
                problems.append("Setting '%s' (%s) has incorrect type '%s' instead of '%s'" %
                                (fullname, comment, str(rstype), str(stype)))
                continue

            if not group in newsettings:
                newsettings[group] = {}
                types[group] = {}
                comments[group] = {}
                rosettings[group] = []
            newsettings[group][name] = value
            types[group][name] = stype
            comments[group][name] = comment
            if ro:
                rosettings[group].append(name)
                rocount += 1
            actual += 1
        if problems:
            log.settings.error('\n'.join(problems))
            raise Exception("Can't load settings")
        # TODO: XXX: actual == total?
        log.settings.info('%d settings found in config, %d are actual (%d read-only)' % (len(descriptors), actual, rocount))
        Settings.readonly_settings = rosettings
        Settings.types = types
        Settings.comments = comments
        Settings.descriptors = descriptors
        Settings.set_config_data(newsettings)


    @staticmethod
    def set_config_data(settings, **kwargs):
        from agatsuma.core import Core
        process = multiprocessing.current_process()
        thread = threading.currentThread()
        log.settings.info("Installing new config data in process '%s' with PID %d using thread '%s'" %
                      (str(process.name), process.pid, thread.getName()))
        timestamp = datetime.datetime.now()
        try:
            Settings.config_lock.acquire()
            Settings.settings.update(settings)
        finally:
            Settings.config_lock.release()
        if Settings.core.debug > 0:
            log.settings.debug("Updated config: %s" % str(Settings.settings))
        Settings.configData = {"data": settings,
                               "update" : timestamp,
                              }
        spells = Core.instance.spellbook.implementations_of(AbstractSpell)
        for spell in spells:
            spell.post_config_update(**kwargs)

    @staticmethod
    def update_callback():
        Settings.set_config_data(Settings.settings)

