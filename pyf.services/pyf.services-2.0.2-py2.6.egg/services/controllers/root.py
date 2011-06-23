# -*- coding: utf-8 -*-
"""Main Controller"""

from tg import expose, flash, require, url, request, redirect
from pylons.i18n import ugettext as _, lazy_ugettext as l_
from repoze.what import predicates

from pyf.services.lib.base import BaseController
from pyf.services.model import DBSession, metadata, Tube
from pyf.services.controllers.error import ErrorController
from pyf.services import model

from pyf.services.controllers.descriptor import DescriptorController
from pyf.services.controllers.tube import TubeController
from pyf.services.controllers.tubelayer import TubeLayerController
from pyf.services.controllers.tubestorage import TubeStorageController
from pyf.services.controllers.dispatch import DispatchController
from pyf.services.controllers.events import EventTrackController
from pyf.services.controllers.tasks import TaskController
from pyf.services.controllers.user import (UserController, GroupController,
                                     PermissionController)

from tgext.admin import AdminController

import time

__all__ = ['RootController']


class RootController(BaseController):
    """
    The root controller for the pyf.services application.
    
    All the other controllers and WSGI applications should be mounted on this
    controller. For example::
    
        panel = ControlPanelController()
        another_app = AnotherWSGIApplication()
    
    Keep in mind that WSGI applications shouldn't be mounted directly: They
    must be wrapped around with :class:`tg.controllers.WSGIAppController`.
    
    """
    error = ErrorController()
    
    admin = AdminController(model, DBSession)
    
    tubes = TubeController(DBSession)
    tubelayers = TubeLayerController(DBSession)
    dispatchs = DispatchController(DBSession)
    descriptors = DescriptorController(DBSession)
    events = EventTrackController(DBSession)
    tasks = TaskController(DBSession)
    
    users = UserController(DBSession)
    groups = GroupController(DBSession)
    permissions = PermissionController(DBSession)

    storage = TubeStorageController(DBSession)

    @expose('pyf.services.templates.dashboard')
    def index(self):
        """Handle the front-page."""
        return dict(standalone_tubes=Tube.get_tubes(needs_source=False),
                    sourced_tubes=Tube.get_tubes(needs_source=True))

    @expose('pyf.services.templates.login')
    def login(self, came_from=url('/')):
        """Start the user login."""
        login_counter = request.environ['repoze.who.logins']
        if login_counter > 0:
            flash(_('Wrong credentials'), 'warning')
        return dict(page='login', login_counter=str(login_counter),
                    came_from=came_from)
    
    @expose()
    def post_login(self, came_from=url('/')):
        """
        Redirect the user to the initially requested page on successful
        authentication or redirect her back to the login page if login failed.
        """
        if not request.identity:
            login_counter = request.environ['repoze.who.logins'] + 1
            redirect(url('/login', came_from=came_from, __logins=login_counter))
        userid = request.identity['repoze.who.userid']
        flash(_('Welcome back, %s!') % userid)
        redirect(came_from)

    @expose()
    def post_logout(self, came_from=url('/')):
        """
        Redirect the user to the initially requested page on logout and say
        goodbye as well.
        
        """
        flash(_('We hope to see you soon!'))
        redirect(came_from)
        
    @expose("json")
    def plugins(self):
        from pyf.componentized.components import ResourceManager
        resource_manager = ResourceManager()
        plugins = resource_manager.get_plugins()
        
        modules = list()
        language = dict(languageName="ComPyf",
                        modules=modules)
        
        for plugin_type, plugin_list in plugins.iteritems():
            for plugin_name, plugin in plugin_list:
                modules.append(dict(name=plugin_name,
                                    inputs=((plugin_type != 'producers') and ["input"] or list()),
                                    outputs=((plugin_type != 'consumers') and ["output"] or list())))
        
        return language
