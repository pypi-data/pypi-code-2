#-*- coding: utf-8 -*-
u"""
Controllers for the CMS backend and frontend applications.

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			July 2008
"""
from warnings import warn
from cocktail.controllers import context
from woost.controllers.application import CMS
from woost.controllers.module import Module
from woost.controllers.basecmscontroller import BaseCMSController
from woost.controllers.notifications import notify_user

