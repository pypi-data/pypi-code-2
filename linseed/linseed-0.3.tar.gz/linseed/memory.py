from . import parsing, read
from .util import pct, Quantity

class Memory(object):
    def __init__(self):
        self.info = read._read(
            '/proc/meminfo',
            parsing.paren_parse)

    total = property(
        lambda self: Quantity(int(self.info['MemTotal'][0]),
                              self.info['MemTotal'][1]))

    free = property(
        lambda self: Quantity(int(self.info['MemFree'][0]),
                              self.info['MemFree'][1]))

    used = property(
        lambda self: pct(float(self.total.value - self.free.value) / self.total.value),
        doc='Percent of memory being used')

    def display(self):
        return 'Mem: {0}%'.format(self.used)

    @staticmethod
    def name():
        return 'linseed_memory'

    @staticmethod
    def description():
        return 'Current memory utilization (%)'

class Swap(object):
    def __init__(self):
        self.info = read._read(
            '/proc/meminfo',
            parsing.paren_parse)

    total = property(
        lambda self: Quantity(int(self.info['SwapTotal'][0]),
                              self.info['SwapTotal'][1]))

    free = property(
        lambda self: Quantity(int(self.info['SwapFree'][0]),
                              self.info['SwapFree'][1]))

    used = property(
        lambda self: pct(float(self.total.value - self.free.value) / self.total.value),
        doc='Percent of swap being used')

    def display(self):
        return 'Swap: {0}%'.format(self.used)

    @staticmethod
    def name():
        return 'linseed_swap'

    @staticmethod
    def description():
        return 'Current swap usage (%)'
