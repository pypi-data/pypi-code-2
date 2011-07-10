import os, sys, urllib, re, logging
from google.appengine.dist import use_library
use_library('django', '1.2')

from google.appengine.ext import webapp
from gae.sessions import SessionMiddleware
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.appstats import recording
from google.appengine.ext import db
from django.conf import settings as django_settings
from gae.sessions import get_current_session
from gae.config import get_config
from gae.tools import applications, prepare_url_vars
from gae import template
from user import get_current_user


class Environment:
    session = None
    SESSION = None
    user = None

    def __init__(self):
        self.user = get_current_user()
        self.session = get_current_session()
        self.SESSION = self.session

    def get(self, key_name=None):
        '''Return GET parameters'''
        pass

    def post(self, key_name=None):
        '''Return POST parameters'''
        pass

    GET = get
    POST = post

    def error(self):
        '''Save error message'''
        pass

    def redirect(self, to_page, permanent=False):
        '''Redirect user to given page'''
        pass

    def previous_page(self):
        '''Return previous page address'''
        pass

    def render(self, template_name, variables={}):
        '''Return current logged-in user'''
        pass


class App:
    _project_dir = None
    _framework_dir = None

    def get_project_dir(self):
        return self._project_dir

    def set_project_dir(self, dir):
        if self._project_dir is not None:
            raise Exception, "You can't redefine project directory"
        self._project_dir = dir

    project_dir = property(get_project_dir, set_project_dir)

    def get_framework_dir(self):
        return self._framework_dir

    def set_framework_dir(self, dir):
        if self._framework_dir is not None:
            raise Exception, "You can't redefine framework directory"
        self._framework_dir = dir

    framework_dir = property(get_framework_dir, set_framework_dir)

    @staticmethod
    def load_models(apps_list):
        '''Load all models and store in GAE db module'''
        # load only once
        if "was_load" in db._kind_map:
            return
        db._kind_map["was_load"] = True
        # get list of all models in each application
        for app_name in apps_list:
            try:
                app_models = __import__("%s.models" % app_name, {}, {}, ["models"])
            except ImportError, e:
                logging.warning("File '%s/models.py' not load. %s" % (app_name, e))
                continue
            models = [getattr(app_models, model_name) for model_name in dir(app_models) if not model_name.startswith("_") and model_name[0].isupper()]
            for model in models:
                db._kind_map[model.kind()] = model

    @staticmethod
    def init_apps():
        '''
        Load and initialize all available applications
        '''
        # TODO: load models only for used applications (based on urls mapping)
        App.load_models(applications())

class RequestHandler(webapp.RequestHandler):
    app_name = None
    debug = False
    urls = []
    status_code = None
    user = None

    def __init__(self):
        global instance
        instance = self

    def _traceback_info(self):
        """
        Print the usual traceback information, followed by a listing of all the
        local variables in each frame.
        """
        tb = sys.exc_info()[2]
        while 1:
            if not tb.tb_next: break
            tb = tb.tb_next
        stack = []
        f = tb.tb_frame
        while f:
            stack.append(f)
            f = f.f_back
        frames = []
        for frame in stack:
            vars = []
            for key, value in frame.f_locals.items():
                if key.startswith("__"): continue # not show special variables
                #We have to be careful not to cause a new error in our error
                #printer! Calling str() on an unknown object could cause an
                #error we don't want.
                try:
                    var_repr = repr(value)
                    var_value = unicode(value)
                    vars.append((key, var_repr, var_value if value != var_value and var_value != var_repr else None))
                except:
                    pass
            frame_info = {"func": frame.f_code.co_name, "file": frame.f_code.co_filename, "line": frame.f_lineno}
            frames.append((frame_info, vars))
        return frames

    def load_app(self, app_name='index', app_view='index', params={}):
        '''
        Load application
        '''
        self.app_name = app_name
        # check view
        try:
            module = __import__("%s.controllers" % self.app_name, {}, {}, ["controllers"])
            # get action handler
            app_action = getattr(module, app_view)
            # run action
            return app_action(self, **params)
        except ImportError, e:
            logging.error("Not found '%s.controllers'. %s" % (self.app_name, e))
            self.error(404)
        except AttributeError, e:
            logging.error("Not found '%s.controllers.%s'. %s" % (self.app_name, app_view, e))
            self.error(404)
        except Exception, e:
            logging.warning("Request handler '%s.%s' complete request with errors: %s" % (self.app_name, app_view, e))
            # show 500 page if error not specified
            if self.status_code is None:
                self.error(500)
        # show error page for user
        if not self.debug:
            if self.status_code is not None and int(self.status_code) != 200:
                return self.render("site/%s" % self.status_code)
            return None
        # show detailed error traceback
        try:
            errors = {"request": self.request,
                      "error": "%s: %s" % (sys.exc_info()[0].__name__, sys.exc_info()[1]),
                      "status_code": self.status_code,
                      "traceback": self._traceback_info()}
            # render page with status code on errors
            return self.render("site/debug", errors)
        except TypeError, e:
            logging.warning("Template '%s' not found" % e)
        except (TypeError, Exception), e:
            logging.warning(e)
        # print raw traceback (without insert to 500 template)
        errors_html = ""
        for error_name, error_details in errors.items():
            if type(error_details) in (tuple, dict, list):
                errors = []
                for frame, vars in error_details:
                    errors.append("%s\n%s" % (
                                  "%s (line %s) in %s" % (frame['func'], frame['line'], frame['file']),
                                  "\n".join(["  %s = %s" % (var_name, var_repr) for var_name, var_repr, var_value in vars])))
                error_details = "\n".join(errors)
            errors_html += "<div class='%(error_name)s'>"\
                "<h2>%(error_name)s</h2>"\
                "<pre>%(error_details)s</pre>"\
                "</div>" % {
                    "error_name": error_name.title(),
                    "error_details": error_details}
        # return error page
        return "<html><body>%s</html></body>" % errors_html

    def get(self):
        # set session handler
        self.session = get_current_session()
        # load template tags and set global template directory
        if not django_settings.TEMPLATE_DIRS:
            django_settings.TEMPLATE_DIRS = (os.path.join(App.project_dir, 'templates'), )
            # use patched and new template tags
            template.register_template_library('gae.tags')
            # register template tags for each  application
            for app_name in applications():
                try:
                    mod = __import__("%s.tags" % app_name, globals(), {}, app_name)
                    template.django.template.libraries[app_name] = mod.register
                except ImportError, e:
                    pass
        # load urls map (only once)
        if not RequestHandler.urls:
            # load global urls mapping
            for rule in get_config('site.urls', []):
                if "url" not in rule:
                    raise Exception, "Not defined 'url' option in the global urls mapping"
                # specified request handler
                if "run" in rule:
                    rule['url'] = self._prepare_url(rule['url'])
                    RequestHandler.urls.append(rule)
                # urls mapping to specified application
                elif "map" in rule:
                    app_name = rule["map"]
                    for app_rule in get_config('%s.urls' % app_name, {}):
                        if "url" not in app_rule:
                            raise Exception, "Not defined 'url' option in the urls mapping for application '%s'" % app_name
                        if "run" not in app_rule:
                            raise Exception, "Not defined 'run' option in the urls mapping for application '%s'" % app_name
                        app_rule['url'] = self._prepare_url(app_rule['url'], rule['url'])
                        app_rule['run'] = "%s.%s" % (app_name, app_rule['run'])
                        RequestHandler.urls.append(app_rule)
                # not specified "run" and "map" options
                else:
                    raise Exception, "You need to specify 'run' or 'map' option for each url in project configuration in 'urls' section"
            # compile regular expressions for use in all next requests
            try:
                for rule in RequestHandler.urls:
                    rule['_url'] = re.compile("%s" % rule['url'])
            except Exception, err:
                logging.error("You have an error with urls mapping in regular expression %r - %s" % (rule['url'], err))
                # delete urls because we have errors in urls
                RequestHandler.urls = []
        # search url address
        url_address = self.request.path.strip('/') + "/"
        url_address = urllib.unquote(url_address).decode("utf-8")
        url_params = None
        for rule in RequestHandler.urls:
            url_match = re.match(rule['_url'], url_address)
            # if url found
            if url_match is not None:
                url_params = 'arg' in rule and rule['arg'] or {}
                # add matched parameters from url string
                url_params.update(url_match.groupdict())
                break
        if url_params is None:
            logging.info("Url '%s' not found" % url_address)
            self.error(404)
        elif 'run' not in rule:
            logging.error("Not defined property 'run' in 'urls' section in configuration file")
            self.error(404)
        else:
            # decode url string parameters
            for name, value in url_params.items():
                url_params[name] = urllib.unquote(value)
                if type(url_params[name]) is not unicode: # encode url parameters
                    url_params[name] = url_params[name].decode("utf-8")
            # set user to global scope
            self.user = get_current_user()
            # run application handler
            (app_name, app_view) = rule['run'].split('.', 1)
            result = self.load_app(app_name, app_view, url_params)
            # send content to user
            self.response.out.write(result)

    def post(self):
        self.get()

    def render(self, path, values={}):
        # add file extension
        path += '.html'
        # set predefined values to template
        values['app'] = self.app_name
        values['user'] = self.user
        # load template from global templates
        return template.render(path, values, self.debug)

    def back_url(self):
        '''Return link to previous page'''
        # passed "back_url" - link to previous page
        if self.request.get('back_url'):
            return self.request.get('back_url')
        # link to previous page
        elif 'HTTP_REFERER' in os.environ and os.environ['HTTP_REFERER'].startswith("http://%s/" % self.request.host):
            return re.split('^https?://[^/]+', os.environ['HTTP_REFERER'])[1]
        # current page
        return self.request.path
    
    def error(self, code):
        # human-readable shortcuts
        if code in ["not found", "page not found"]:
            code = 404
        elif code in ["access denied", "no access", "login required"]:
            code = 403
        super(RequestHandler, self).error(code)
        self.status_code = code
    
    def redirect(self, uri, permanent=False):
        # human-readable shortcuts
        if uri in ["go back", "back"]:
            uri = self.back_url()
        elif uri in ["reload", "reload page", "refresh", "refresh page"]:
            uri = self.request.path
        uri = uri.encode("utf-8")
        super(RequestHandler, self).redirect(uri, permanent)

    def _prepare_url(self, url, url_prefix=""):
        '''Return url rule to use in regular expressions module'''
        # compatibility for use empty string in url (without manually setting empty string as "")
        if url is None: url = ""
        if url_prefix is None: url_prefix = ""
        # delete trailing spaces
        url = url.strip('/')
        url_prefix = url_prefix.strip('/')
        # replace ":var_name" to regular expression rule
        url = prepare_url_vars(url, "(?P<\\1>[^/]+)")
        url_prefix = prepare_url_vars(url_prefix, "(?P<\\1>[^/]+)")
        # delete spaces after join url with prefix, if url or prefix is empty
        return "^%s/?$" % "/".join([url_prefix, url]).strip('/')

# to be redefined to application instance after first run
instance = RequestHandler

def inst():
    global instance
    return instance

def run(project_dir):
    # set application global configuration
    App.project_dir = project_dir
    App.framework_dir = os.path.dirname(__file__)
    App.init_apps()
    # auto detect environment (development or production)
    debug = os.environ['SERVER_SOFTWARE'].startswith('Development')
    RequestHandler.debug = debug
    COOKIE_KEY = 'my_private_key_used_for_this_site_%s' % os.environ['APPLICATION_ID']
    app = webapp.WSGIApplication([('/.*', RequestHandler)], debug=debug)
    app = SessionMiddleware(app, cookie_key=COOKIE_KEY, cookie_only_threshold=0)
    app = recording.appstats_wsgi_middleware(app)
    run_wsgi_app(app)
