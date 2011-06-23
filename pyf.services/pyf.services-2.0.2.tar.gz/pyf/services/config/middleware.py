# -*- coding: utf-8 -*-
"""WSGI middleware initialization for the pyf.services application."""

from pyf.services.config.app_cfg import base_config
from pyf.services.config.environment import load_environment
from paste.deploy.converters import asbool

__all__ = ['make_app']

# Use base_config to setup the necessary PasteDeploy application factory. 
# make_base_app will wrap the TG2 app with all the middleware it needs. 
make_base_app = base_config.setup_tg_wsgi_app(load_environment)

def make_app_hooks(global_conf, full_stack=True, **app_conf):
    from pyf.services.versionning import get_repository
    get_repository()

    if asbool(app_conf.get('scheduling.on', True)):
        from tgscheduler import scheduler
        scheduler.start_scheduler()

        from pyf.services.core.tasks import schedule_tasks
        schedule_tasks()

    if not app_conf.get('tempdir') is None:
        from pyf.services.core import env
        env.init_tempdir(app_conf.get('tempdir'))

    if asbool(app_conf.get('station.on', False)):
        from pyf.services.core import station
        station.init_station()
    
    if asbool(app_conf.get('mail.on', True)):
        from turbomail.adapters import tm_pylons
        tm_pylons.start_extension()

def make_app(global_conf, full_stack=True, **app_conf):
    """
    Set pyf.services up with the settings found in the PasteDeploy configuration
    file used.
    
    :param global_conf: The global settings for pyf.services (those
        defined under the ``[DEFAULT]`` section).
    :type global_conf: dict
    :param full_stack: Should the whole TG2 stack be set up?
    :type full_stack: str or bool
    :return: The pyf.services application with all the relevant middleware
        loaded.
    
    This is the PasteDeploy factory for the pyf.services application.
    
    ``app_conf`` contains all the application-specific settings (those defined
    under ``[app:main]``.
    
   
    """
    app = make_base_app(global_conf, full_stack=full_stack, **app_conf)
    # We call the hooks
    make_app_hooks(global_conf, full_stack=full_stack, **app_conf)
    
    # Wrap your base TurboGears 2 application with custom middleware here
    
    return app
