import os
import sys
import logging

from bn import AttributeDict, absimport, uniform_path
from pipestack.pipe import MarblePipe, Marble
from urlconvert import extract_url_parts, RuleSet

log = logging.getLogger()

names = AttributeDict(
    resolve='resolve',
    static='static',
)

class AppMarble(Marble):

    def on_set_persistent_state(self, state):
        self.names = state['names']
        self.log = state['log']
        self.ruleset = state['ruleset']
        self.path = state['path']

    def on_set_flow_state(self, state):
        self.vars = AttributeDict(state['vars'])
        self.url_parts = state['url_parts']
        self.area = state['area']

    def url(self, **p):
        conversion = self.ruleset.generate_url(p, self.url_parts)
        return conversion.result.url

class BaseApp(MarblePipe):
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

    marble_class = AppMarble
    options = dict()
    persistent_state = None

    def __init__(
        self, 
        bag, 
        name,
        aliases=None,
        mount_at='auto', 
        urls=None, 
        names=names,
    ):
        self.names = names
        MarblePipe.__init__(self, bag, name, aliases)
        if urls:
            self.urls = urls
        self.ruleset = RuleSet(self.urls)
        self.mount_at = mount_at
        if mount_at != 'auto':
            if mount_at.startswith('/') and mount_at.endswith('/'):
                self.path = mount_at
            else:
                raise Exception(
                    "The 'mount_at' argument should start and end with a "
                    "'/' character"
                )
        else:
            self.path = None
        self._area_cache = {}
        self.persistent_state = dict(
            log=log, 
            ruleset=self.ruleset, 
            names=names,
            path=self.path,
        )
    
    def enter(self, bag):
        if self.mount_at == 'auto' and not \
           bag[self.names.resolve].has_key('app'):
            # The app wasn't resolved so we can skip this pipe
            return 
        if not self.path and self.mount_at == 'auto':
            if bag[self.names.resolve].has_key('app'):
                app_path = os.path.join(
                    bag[self.names.resolve].app, 
                    'index.app',
                )
                if os.path.exists(app_path) and not os.path.isdir(app_path):
                    fp = open(app_path, 'r')
                    data = fp.read()
                    fp.close()
                    if data[:4] == 'app=' and \
                       data[4:].strip(' \n\r\t') == self.name:
                        resource = uniform_path(bag[self.names.resolve].app)
                        site_root = uniform_path(
                            bag.app.config[self.names.resolve].site_root
                        )
                        self.path = resource[len(site_root):]+'/'
        url_parts = extract_url_parts(bag)
        log.info('Extracted URL Parts: %r', url_parts)
        if not self.path or not url_parts['path'].startswith(self.path[1:]):
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
                bag.http.environ.get('SCRIPT_NAME', ''), 
                self.path,
            )
            url_parts['script'] = url_parts['script'][\
               len(bag.http.environ.get('SCRIPT_NAME', '')):]\
               + self.path.strip('/')
            url_parts['path'] = url_parts['path'][len(self.path)-1:]
        log.info('Modified URL Parts: %r', url_parts)
        conversion = self.ruleset.match(url_parts=url_parts)
        if not conversion.successful:
            # Not for this URL.
            log.info(
                'Could not route %r to an action, no URL vars found',
                bag.http.environ['PATH_INFO'],
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
            handler(bag, match=res)
            bag.interrupt_flow(application_handled=True)
            return 
        vars = res.vars
        if not vars.get('area'):
            log.info(
                'Could not route %r to an action, no area specified',
                bag.http.environ['PATH_INFO'],
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
        area = self._area_cache.get(area_name)
        if not area:
            app_dir = os.path.dirname(sys.modules[self.__class__.__module__].__file__)
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
                if sys.modules[self.__class__.__module__].__file__.split('/')[-1].split('.')[-2] == '__init__':
                    mod_path = self.__class__.__module__+'.area.%s'
                else:
                    mod_path = ('.'.join(self.__class__.__module__.split('.')[:-1]))+'.area.%s'
            elif os.path.exists(
                os.path.join(
                    app_dir,
                    area_name+'.py'
                )
            ):
                if sys.modules[self.__class__.__module__].__file__.split('/')[-1].split('.')[-2] == '__init__':
                    mod_path = self.__class__.__module__+'.%s'
                else:
                    mod_path = ('.'.join(self.__class__.__module__.split('.')[:-1]))+'.%s'
            elif os.path.exists(
                os.path.join(
                    app_dir,
                    'area',
                    area_name,
                    'action.py'
                )
            ):
                if sys.modules[self.__class__.__module__].__file__.split('/')[-1].split('.')[-2] == '__init__':
                    mod_path = self.__class__.__module__+'.area.%s.action'
                else:
                    mod_path = ('.'.join(self.__class__.__module__.split('.')[:-1]))+'area.%s.action'
            else:
                log.info(
                    'The Python module in %r for area %r matched from %r '
                    'does not exist ',
                    app_dir, area_name, 
                    bag.http.environ['PATH_INFO'],
                )
                return
            # We support two types of area: modules and classes. 
            if area_class:
                area = getattr(
                    absimport(mod_path%area_name),
                    area_class,
                )
                log.info('Loading %r app \'%s.%s\' area into cache', self.name, area_name, area_class)
                self._area_cache[area_name] = area()
            else:
                mod_name = mod_path%area_name
                self._area_cache[area_name] = absimport(mod_name)
                
        # Now set up the marble
        area = self._area_cache[area_name]
        marble = bag[self.name] = self.marble_class(
            bag,
            self.name,
            bag.app.config[self.name],
            persistent_state=self.persistent_state,
            flow_state=dict(vars=vars, url_parts=url_parts, area=area), 
            aliases=self.aliases,
        )
        vars = bag[self.name].vars 
        log.debug('Vars matched: %r', vars)
        if not vars.get('action') and not vars.get('api'):
            log.info(
                'Could not route %r to an action or API call, no action or '
                'api specified by matched rule',
                bag.http.environ['PATH_INFO'],
            )
            return
        elif vars.get('action'):
            action_name = 'action_'+vars['action']
            if not hasattr(area, action_name):
                log.info(
                    'No such action %r in area %r matched from %r ',
                    action_name,
                    area_name,
                    bag.http.environ['PATH_INFO'],
                )
                return
            else: 
                action = getattr(area, action_name)
                result = action(marble)
                if result is None:
                    if bag.http.response.body:
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
                        bag.http.response.body = [result]
                    else:
                        bag.http.response.body = result
                bag.interrupt_flow(application_handled=True)

class BaseArea(object):
    pass

