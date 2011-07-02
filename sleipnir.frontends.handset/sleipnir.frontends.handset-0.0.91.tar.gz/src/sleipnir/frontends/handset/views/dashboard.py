#!/usr/bin/env python
# -*- mode:python; tab-width: 2; coding: utf-8 -*-

"""
QWindow

Main Application Component Manager
"""

from __future__ import absolute_import

__author__  = "Carlos Martin <cmartin@liberalia.net>"
__license__ = "See LICENSE file for details"

# Import here any required modules

# QML required deps

__all__ = ['QDashBoard']

# Project requirements
from sleipnir.frontends.handset.component import QViewComponent
from sleipnir.frontends.handset.component import QViewPresenter
from sleipnir.frontends.handset.constants import QML

# local submodule requirements


#pylint: disable-msg=W0232,R0903
class QDashBoard(QViewPresenter):
    """Main QDashBoard Presenter"""


class DashBoardFactory(QViewComponent):
    """DashBoard Component"""

    item = "IDashBoard"

    #pylint: disable-msg=R0201
    def _create_component(self, window, source=None):
        source = QML(source or __file__, window.platform.name)
        return QViewComponent._create_component(self, window, source)

    def _create_presenter(self, item=None, facade=None):
        return QDashBoard(item, facade)
