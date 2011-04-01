import os
import sys
import logging

from bn import AttributeDict, absimport, uniform_path
from pipestack.pipe import Pipe, DispatchMarble, Marble
from pipestack.app import PipeError
from urlconvert import extract_url_parts, RuleSet
from conversionkit import Field

log = logging.getLogger(__name__)

def validPath():
    def validPath_converter(conversion, state):
        if not conversion.value.startswith('/') and conversion.value.endswith('/'):
            conversion.error = 'Paths should start and end with a \'/\' character'
        else:
            conversion.result = conversion.value
    return validPath_converter

class BaseArea(object):
    pass

class URLMarble(DispatchMarble):
    def __init__(
        marble, 
        bag, 
        name, 
        config, 
        aliases=None, 
        default_aliases=None, 
        persistent_state=None, 
        flow_state=None
    ):
        if not hasattr(marble, 'urls'):
            raise Exception(
                '%r marble has no \'urls\' attribute specified'%(
                    marble.__class__.__name__,
                )
            )
        DispatchMarble.__init__(
            marble, 
            bag,
            name,
            config,
            aliases,
            default_aliases,
            persistent_state,
            flow_state,
        )
        marble.ruleset = RuleSet(marble.urls)
        marble.log = persistent_state['log']
        #marble.path = persistent_state['path']
        marble._area_cache = persistent_state['_area_cache']
        marble.dispatch()

    def url(marble, **p):
        try:
            marble.apps
        except PipeError:
            uses_apps = False
        else:
            uses_apps = True
        if 'pipe' in p and uses_apps:
            # Use the global version which will call this one
            return marble.apps.url(**p)
        else:
            conversion = marble.ruleset.generate_url(p, marble.url_parts)
            return conversion.result.url

    def redirect(marble, **p):
        conversion = marble.url(**p)
        marble.bag.http_response.status = '301 Redirect' 
        marble.bag.http_response.header_list.append(
            dict(
                name='Location', 
                value=str(conversion.result.url)
            )
        )
        marble.bag.http_response.body = ['Redirecting...']
        return 'Redirecting...'

    def dispatch(marble):
        try:
            marble.apps
        except PipeError:
            uses_apps = False
        else:
            uses_apps = True
        if uses_apps and not marble.apps.dispatch:
            # We just want the marble created for URL-generating purposes, not dispatched
            return 
        url_parts = extract_url_parts(marble.bag)
        log.info('Extracted URL Parts: %r', url_parts)
        if not url_parts['path'].startswith(marble.config.path[1:]):
            return
        else:
            # Modify script_name and path_info for this app 
            # (REMOVING and external SCRIPT_NAME)
            log.info(
                (
                    "Script parts - url_parts script: %r, "
                    "environ SCRIPT_NAME: %r, url_parts path: %r"
                ),
                url_parts['script'], 
                marble.environ.get('SCRIPT_NAME', ''), 
                marble.config.path,
            )
            url_parts['script'] = url_parts['script'][\
               len(marble.environ.get('SCRIPT_NAME', '')):]\
               + marble.config.path.strip('/')
            url_parts['path'] = url_parts['path'][len(marble.config.path)-1:]
        log.info('Modified URL Parts: %r', url_parts)
        conversion = marble.ruleset.match(url_parts=url_parts)
        if not conversion.successful:
            # Not for this URL.
            log.info(
                'Could not route %r to an action, no URL vars found',
                marble.environ['PATH_INFO'],
            )
            return
        res = conversion.result
        if res.extra and res.extra.has_key('handler'):
            handler = res.extra['handler']
            log.debug(
                'Using the handler %r specified as an extra arg in the URLs '
                'to process the request', 
                handler,
            )
            handler(marble.bag, match=res)
            marble.bag.interrupt_flow()
            return 
        vars = res.vars
        if not vars.get('area'):
            log.info(
                'Could not route %r to an action, no area specified',
                marble.environ['PATH_INFO'],
            )
            return
        else:
            area_name = vars.get('area')
            if area_name in ['action', 'area']:
                raise Exception(
                    'You cannot name an area %r, this is a reserved word'%(
                        area_name,
                    )
                )

        # At this point we have our area. Let's get the left over path
        area = marble._area_cache.get(area_name)
        if not area:
            app_dir = os.path.dirname(sys.modules[marble.__class__.__module__].__file__)
            if res.extra and res.extra.has_key('area_class'):
                v = vars.copy()
                v['camel_area'] = area_name.capitalize()
                area_class = res.extra['area_class']%v
            else:
                area_class = None
            if os.path.exists(
                os.path.join(
                    app_dir,
                    'area',
                    area_name+'.py'
                )
            ):
                if sys.modules[marble.__class__.__module__].__file__.split('/')[-1].split('.')[-2] == '__init__':
                    mod_path = marble.__class__.__module__+'.area.%s'
                else:
                    mod_path = ('.'.join(marble.__class__.__module__.split('.')[:-1]))+'.area.%s'
            elif os.path.exists(
                os.path.join(
                    app_dir,
                    area_name+'.py'
                )
            ):
                if sys.modules[marble.__class__.__module__].__file__.split('/')[-1].split('.')[-2] == '__init__':
                    mod_path = marble.__class__.__module__+'.%s'
                else:
                    mod_path = ('.'.join(marble.__class__.__module__.split('.')[:-1]))+'.%s'
            elif os.path.exists(
                os.path.join(
                    app_dir,
                    'area',
                    area_name,
                    'action.py'
                )
            ):
                if sys.modules[marble.__class__.__module__].__file__.split('/')[-1].split('.')[-2] == '__init__':
                    mod_path = marble.__class__.__module__+'.area.%s.action'
                else:
                    mod_path = ('.'.join(marble.__class__.__module__.split('.')[:-1]))+'area.%s.action'
            else:
                log.info(
                    'The Python module in %r for area %r matched from %r '
                    'does not exist ',
                    app_dir, area_name, 
                    marble.environ['PATH_INFO'],
                )
                return
            # We support two types of area: modules and classes. 
            if area_class:
                area = getattr(
                    absimport(mod_path%area_name),
                    area_class,
                )
                log.info(
                    'Loading %r app \'%s.%s\' area into cache', 
                    marble.name, 
                    area_name, 
                    area_class,
                )
                marble._area_cache[area_name] = area()
            else:
                mod_name = mod_path%area_name
                marble._area_cache[area_name] = absimport(mod_name)
                
        # Now set up the marble
        marble.vars = AttributeDict(vars)
        marble.url_parts = url_parts
        marble.area = area = marble._area_cache[area_name]
        log.debug('Vars matched: %r', vars)
        if not vars.get('action') and not vars.get('api'):
            log.info(
                'Could not route %r to an action or API call, no action or '
                'api specified by matched rule',
                marble.environ['PATH_INFO'],
            )
            return
        elif vars.get('action'):
            action_name = 'action_'+vars['action']
            if not hasattr(area, action_name):
                log.info(
                    'No such action %r in area %r matched from %r ',
                    action_name,
                    area_name,
                    marble.environ['PATH_INFO'],
                )
                return
            else: 
                action = getattr(area, action_name)
                result = action(marble)
                if result is None:
                    if marble.http_response.body:
                        log.info(
                            'No response from action but body present so '
                            'not raising an error'
                        )
                    else: 
                        raise Exception(
                            'No response from action %r'%action_name
                        )
                else:
                    if isinstance(result, (unicode, str)):
                        marble.http_response.body = [result]
                    else:
                        marble.http_response.body = result
                marble.bag.interrupt_flow()

class URLPipe(Pipe):
    """\
    An ``AppPipe`` is a specical type of marbles in that in addition to
    configuration and an optional marble, it also takes an ``App`` object.

    As well as being an ordinary marbles which is placed in the marblesline and
    dispatches to the ``App`` if the URL path matches the name of the app, an
    ``AppPipe`` can also be used outside of the marblesline. In this case an
    ``AppDispatch()`` marbles must be in the marblesline and it will dispatch to 
    the app based on the location of an ``index.app`` file in the static directory
    whose contents corresponds to the application name.
    """
    default_aliases = dict(
        resolve='resolve',
        static='static',
        environ='environ',
        http_response='http_response',
        apps='apps',
    )
    marble_class = URLMarble
    options = dict(
        path = Field(
            validPath(),
            missing_or_empty_error = 'Please specify %(name)s.path'
        )
    )

    def __init__(marble, bag, name, aliases=None, **pextras):
        Pipe.__init__(marble, bag, name, aliases, **pextras)
        marble.persistent_state=dict(
            _area_cache = {},
            log=log, 
        )

    def enter(self, bag):
        Pipe.enter(self, bag)

BaseApp = URLPipe
AppMarble = URLMarble

class URLDispatchPipe(Pipe):
    class marble_class(Marble):
        dispatch = True
        url_parts = None
        def url(self, **args):
            if not 'pipe' in args:
                raise Exception("Expected a 'pipe' argument to render()")
            elif args['pipe'] not in self.persistent_state['apps']:
                # You can't just enter the pipe because a dispatch marble will 
                # also dispatch so you'll probably get an infinte loop as the 
                # handler tries to generate URLs. Instead we set this variable
                # which the dispatch marble will check to see if it is 
                # supposed to dispatch or not.
                self.dispatch = False
                if not self.bag.has_key(args['pipe']):
                    self.bag.enter(args['pipe'])
                self.dispatch = True
                # We should be able to find its name, path and ruleset now
                name = self.bag[args['pipe']].name
                if name != args['pipe']:
                    raise Exception('What? The name of the pipe being loaded and the name asked for are different!')
                path = self.bag[args['pipe']].config.path
                ruleset = self.bag[args['pipe']].ruleset
                if name in self.persistent_state['apps']:
                    raise Exception('An app named %r is already registered with URLManager'%app_info.name)
                for k, v in self.persistent_state['apps'].items():
                    if v.path == path:
                        raise Exception('The path %r specified for %r had already been registered with URLManager by %r'%(path, name, k))
                # Since this shouldn't change, we cache it here
                self.persistent_state['apps'][args['pipe']] = AttributeDict(path=path, ruleset=ruleset)
            if not self.url_parts:
                self.url_parts = extract_url_parts(self.bag)
            ruleset = self.persistent_state['apps'][args['pipe']].ruleset
            del args['pipe']
            conversion = ruleset.generate_url(args, self.url_parts)
            return conversion.result.url
    default_aliases = dict(environ='environ') 
    def create(self, bag):
        self.persistent_state = {
            'plugins': bag.app.fetch_plugins(self.name, 'app'),
            'apps': {},
        }

