# -*- coding: utf-8 -*-

import logging
#import multiprocessing

try:
    from logging.config import dictConfig
except ImportError:
    from agatsuma.third_party.dictconfig import dictConfig

class LoggerNotPresentInConfig(Exception):
    def __init__(self, name):
        self.__name = name

    def __str__(self):
        return "Logger '%s' not present in config" % self.__name

class log(object):
    __loggers = set()
    __cfg = None

    def __init__(self):
        class NothingToInstantiate(Exception):
            pass
        raise NothingToInstantiate()

    @staticmethod
    def initiate(cfg):
        log.__cfg = cfg
        dictConfig(cfg)

    @staticmethod
    def new_logger(logger_name):
        assert not logger_name in log.__loggers
        assert not hasattr(log, logger_name)

        loggersDict = log.__cfg['loggers']

        if not logger_name in loggersDict:
            raise LoggerNotPresentInConfig(logger_name)
        setattr(log, logger_name, logging.getLogger(logger_name))
