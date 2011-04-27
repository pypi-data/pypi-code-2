from PyQt4.QtGui import *
from PyQt4.QtCore import *
from winterstone.base import WinterPlugin


class UIConfig(WinterPlugin):
    def activate(self):
        self.api.toolBar.setIconSize(
            QSize(self.config.options.tbicon_size, self.config.options.tbicon_size))
        self.api.toolBar.setMovable(self.config.options.tb_movable)
        self.api.ex('resize')(self.config.options.width, self.config.options.height)

        self.api.info('%s: start' % self.name)
        return WinterPlugin.activate(self)

    def deactivate(self):
        self.api.info('%s: stop' % self.name)
        return WinterPlugin.deactivate(self)