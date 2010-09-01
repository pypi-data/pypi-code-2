import logging
import re
import os

from bn import absimport, AttributeDict
from urlconvert import RuleSet, extract_url_parts

log = logging.getLogger(__name__)

class App(object):
    def __init__(self, service_name, base_dir, module_path, options=None):
        if options:
            self.converter = toRecord(converters=options)
        if not self.rules:
            raise Exception('Expected some rules')
        self.ruleset = ruleset = RuleSet(self.rules)
        self.base_dir = base_dir
        self.module_path = module_path
        self._area_cache = {}
        self.service_name = service_name

    def dispatch(self, service, app, url_parts, resolveresource='resolveresource'):
        conversion = self.ruleset.match(url_parts=url_parts)
        if not conversion.successful:
            # Not for this URL.
            log.info(
                'Could not route %r to an action, no URL vars found',
                service.http.environ['PATH_INFO'],
            )
            return
        vars = conversion.result
        if not vars.get('area'):
            log.info(
                'Could not route %r to an action, no area specified',
                service.http.environ['PATH_INFO'],
            )
            return
        else:
            area_name = vars.get('area')
            if not os.path.exists(
                os.path.join(
                    self.base_dir,
                    app,
                    area_name, 
                    '__init__.py'
                )
            ) and not os.path.exists(
                os.path.join(
                    self.base_dir,
                    app,
                    area_name+'.py'
                )
            ):
                log.info(
                    'The Python module in %r for area %r in %r matched from %r '
                    'does not exist ',
                    self.base_dir, area_name, app,
                    service.http.environ['PATH_INFO'],
                )
                return
        # At this point we have our area. Let's get the left over path
        area = self._area_cache.get(area_name)
        if not area:
            log.info('Loading %r app %r area into cache', app, area_name)
            camel_area_name = ''.join([x.capitalize() for x in area_name.split('_')])
            area = getattr(absimport(self.module_path+'.%s'%area_name), '%sArea'%camel_area_name)
            area.service_name = self.service_name
            area.app_name = app
            area.log = log
            def url(s, **p):
                url_parts = extract_url_parts(service)
                url_parts['script'] = service[resolveresource].script
                result = self.ruleset.generate_url(p, url_parts)
                return result
            area.url = url
            self._area_cache[area_name] = area#(service)
        area = self._area_cache[area_name](service)
        area.vars = AttributeDict(vars)
        log.debug('Vars matched: %r', vars)
        if not vars.get('action'):
            log.info(
                'Could not route %r to an action, no action specified by '
                'matched rule',
                service.http.environ['PATH_INFO'],
            )
            return 
        else:
            action_name = 'on_action_'+vars['action']
            if not hasattr(area, action_name):
                log.info(
                    'No such action %r in area %r matched from %r ',
                    action_name,
                    area_name,
                    service.http.environ['PATH_INFO'],
                )
                return
            else: 
                action = getattr(area, action_name)
                result = action(service)
                if result is None:
                    if service.http.response.body:
                        log.info('No response from action but body present so not raising an error')
                    else: 
                        raise Exception('No response from action %r'%action_name)
                else:
                    service.http.response.body = result # [x for x in result]
                service.interrupt_flow(application_handled=True)

def appDispatch(module_path, resolveresource='resolveresource'):

    url_cache = {}
    app_cache = {}

    def appDispatch_constructor(service):
        name = service.name
        base_module = absimport(
            module_path,
        )
        base_dir = base_module.__path__[0]
        service.config[name] = AttributeDict()
        def start(service):
            handled = False
            request_url = service.http.environ['PATH_INFO']
            app_guess = request_url.split('/')[-1]
            if '.' in app_guess:
                # It isn't an app if it has an extension
                return
            app = url_cache.get(request_url)
            if app is None:
                if service[resolveresource].has_key('resource'):
                    app_path = os.path.join(service[resolveresource].resource, 'index.app')
                else: 
                    # No resource matched
                    log.info('No resource for app to be dermined from')
                    return
                if os.path.exists(app_path) and not os.path.isdir(app_path):
                    rest = None
                    fp = open(os.path.join(service[resolveresource].resource, 'index.app'), 'rb')
                    data = fp.readline()
                    if data.startswith('app'):
                        rest = fp.read()
                    fp.close()
                    if rest:
                        # This isn't an indicator
                        log.info('Content of %r not an app'%app_path)
                        return 
                    else:
                        # Let's cache the app object
                        url_cache[request_url] = app = data[3:].strip('= \n\t')
                        log.info('Loaded %r app name into cache', app)
                else:
                    log.info('Either app path %r doesn\'t exist or is a directory'%app_path)
                    return
            dispatch = app_cache.get(app)
            if dispatch is None:
                # Import the module
                # Import the module
                mod_path = module_path+'.%s'%app
                mod = __import__(mod_path)
                module = getattr(getattr(mod, 'app'), app)
                # Now get the application class
                app_cache[app] = dispatch = module.Application(name, base_dir, module_path+'.'+app)
                log.info('Loaded %r app object into cache', app)
            url_parts = extract_url_parts(service)
            url_parts['script'] = service[resolveresource].get('script', '')
            url_parts['path'] = service[resolveresource].path
            dispatch.dispatch(service, app, url_parts, resolveresource)
        return AttributeDict(start=start)
    return appDispatch_constructor


