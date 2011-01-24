# Copyright (C) 2010-2011 Michal Nowikowski <godfryd@gmail.com>
# All rights reserved.
#
# Permission  is  hereby granted,  free  of charge,  to  any person
# obtaining a  copy of  this software  and associated documentation
# files  (the  "Software"),  to   deal  in  the  Software   without
# restriction,  including  without limitation  the  rights to  use,
# copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies  of  the  Software,  and to  permit  persons  to  whom the
# Software  is  furnished  to  do  so,  subject  to  the  following
# conditions:
#
# The above copyright  notice and this  permission notice shall  be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS  IS", WITHOUT WARRANTY OF ANY  KIND,
# EXPRESS OR IMPLIED, INCLUDING  BUT NOT LIMITED TO  THE WARRANTIES
# OF  MERCHANTABILITY,  FITNESS   FOR  A  PARTICULAR   PURPOSE  AND
# NONINFRINGEMENT.  IN  NO  EVENT SHALL  THE  AUTHORS  OR COPYRIGHT
# HOLDERS  BE LIABLE  FOR ANY  CLAIM, DAMAGES  OR OTHER  LIABILITY,
# WHETHER  IN AN  ACTION OF  CONTRACT, TORT  OR OTHERWISE,  ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.

import os
import re
import logging
import socket
import BaseHTTPServer
from SocketServer import ThreadingMixIn
import json
from mako.template import Template
from mako.lookup import TemplateLookup

base_dir = os.path.dirname(os.path.abspath(__file__))
templates_dir = os.path.join(base_dir, "templates")
template_lookup = TemplateLookup(directories=["/"])

log = logging.getLogger("rj.server")

class ThreadedHTTPServer(ThreadingMixIn, BaseHTTPServer.HTTPServer):
    """Handle requests in a separate thread."""

class Http404NotFoundError(Exception): pass

class RjSrvHTTPRequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        self.mapping = [
            ("/rest", "rest_root"),
            ("/rest/machines_groups", "rest_machines_groups"),
            ("/rest/machines_groups/([^/]+)", "rest_machines_group"),
            ("/rest/machines_groups/([^/]+)/machines", "rest_machines"),
            ("/rest/machines_groups/([^/]+)/machines/([^/]+)", "rest_machine"),
            ("/rest/build_lines", "rest_build_lines"),
            ("/rest/build_lines/([^/]+)", "rest_build_line"),
            ("/rest/build_lines/([^/]+)/builds", "rest_builds"),
            ("/rest/build_lines/([^/]+)/builds/([^/]+)", "rest_build"),
            ("/rest/build_lines/([^/]+)/builds/([^/]+)/changes", "rest_changes"),
            ("/rest/build_lines/([^/]+)/builds/([^/]+)/tests", "rest_tests"),
            ("/rest/build_lines/([^/]+)/builds/([^/]+)/logs", "rest_logs"),
            ("/rest/build_lines/([^/]+)/config/settings", "rest_cfg_settings"),
            ("/rest/build_lines/([^/]+)/config/triggers", "rest_cfg_triggers"),
            ("/rest/build_lines/([^/]+)/config/triggers/([^/]+)", "rest_cfg_trigger"),
            ("/rest/build_lines/([^/]+)/config/script", "rest_cfg_script"),
            ("/static/(.+)", "static"),
            ("/settings", "settings"),
            ("/settings/general", "settings_general"),
            ("/settings/email", "settings_email"),
            ("/settings/variables", "settings_variables"),
            ("/machines_groups", "machines_groups"),
            ("/machines_groups/([^/]+)", "machines_group"),
            ("/machines_groups/([^/]+)/machines", "machines"),
            ("/machines_groups/([^/]+)/machines/([^/]+)", "machine"),
            ("/build_lines", "build_lines"),
            ("/build_lines/([^/]+)", "build_line"),
            ("/build_lines/([^/]+)/builds", "builds"),
            ("/build_lines/([^/]+)/builds/([^/]+)", "build"),
            ("/build_lines/([^/]+)/builds/([^/]+)/changes", "changes"),
            ("/build_lines/([^/]+)/builds/([^/]+)/tests", "tests"),
            ("/build_lines/([^/]+)/builds/([^/]+)/logs", "logs"),
            ("/build_lines/([^/]+)/config", "config"),
            ("/build_lines/([^/]+)/config/settings", "cfg_settings"),
            ("/build_lines/([^/]+)/config/triggers", "cfg_triggers"),
            ("/build_lines/([^/]+)/config/triggers/([^/]+)", "cfg_trigger"),
            ("/build_lines/([^/]+)/config/script", "cfg_script"),
            ("/build_lines/([^/]+)/config/reporting", "cfg_reporting"),
            ("/", "root")]
        BaseHTTPServer.BaseHTTPRequestHandler.__init__(self, *args, **kwargs)

    def _map_url(self, method):
        for ptrn, handler_name in self.mapping:
            m = re.match("^%s$" % ptrn, self.path)
            if m != None:
                try:
                    handler = getattr(self, "%s_%s" % (method, handler_name))
                    body, mime = handler(*m.groups())
                    return body, True, mime
                except Http404NotFoundError:
                    return "", False, "text/html"
        return "", False, "text/html"

    def get_rest_root(self):
        body = ""
        if "text/html" in self.headers['Accept']:
            body += "<h3>RedJack Server on %s</h3>" % socket.gethostname()
            body += "<p><a href='/rest/machines_groups'>Machines Groups</a></p>"
            body += "<p><a href='/rest/projects'>Projects</a></p>"
        else:
            data = dict(machines_groups_uri="/rest/machines_groups",
                        projects_uri="/rest/projects")
            body = json.dumps(data)
        return body, "text/html"

    def get_rest_machines_groups(self):
        body = ""
        if "text/html" in self.headers['Accept']:
            body += "<h3>RedJack Server on %s</h3>" % socket.gethostname()
            body += "<h4>Machines groups</h4>"
            for mg_name, mg in self.server.cfg.machines.iteritems():
                body += "<p><a href='/rest/machines_groups/%s'>%s</a><br/>" % (mg_name, mg_name)
                body += "<table>"
                for m_name, m in mg.iteritems():
                    body += "<tr><td>Name</td><td><a href='/rest/machines_groups/%s/machines/%s'>%s</a></td></tr>" % (mg_name, m_name, m_name)
                    body += "<tr><td>IP Address</td><td>%s</td></tr>" % m['address']
                    body += "<tr><td>Port</td><td>%d</td></tr>" % m['port']
                body += "<table></p>"
        else:
            data = []
            for mg_name in self.server.cfg.machines.get_groups():
                machines = []
                for m_name in self.server.cfg.machines.get_machines(mg_name):
                    m = self.server.cfg.machines.get_machine(mg_name, m_name)
                    machine = dict(uri="/rest/machines_groups/%s/machines/%s" % (mg_name, m_name),
                                   name=m_name,
                                   address=m['address'],
                                   port=m['port'])
                    machines.append(machine)
                group = dict(uri="/rest/machines_groups/%s" % mg_name,
                             name=mg_name,
                             machines=machines)
                data.append(group)
            body = json.dumps(data)
        log.info("BODY: " + body)
        return body, "text/html"

    def post_rest_machines_groups(self):
        size = int(self.headers["content-length"])
        data = self.rfile.read(size)
        log.info("received: " + data)
        data = json.loads(data)
        name = data['name']
        self.server.cfg.machines.add_group(name)
        return "1", "text/html"

    def get_rest_machines_group(self, name):
        group = None
        log.info("get_rest_machines_group")
        for mg_name in self.server.cfg.machines.get_groups():
            if mg_name == name:
                group = mg_name
                break
        if group == None:
            raise Http404NotFoundError()

        body = ""
        if "text/html" in self.headers['Accept']:
            body += "<h3>RedJack Server on %s</h3>" % socket.gethostname()
            body += "<h4>Machines group %s</h4>" % name
            body += "<table>"
            for m_name in self.server.cfg.machines.get_machines(group):
                m = self.server.cfg.machines.get_machine(group, m_name)
                body += "<tr><td>Name</td><td><a href='/rest/machines_groups/%s/machines/%s'>%s</a></td></tr>" % (name, m_name, m_name)
                body += "<tr><td>IP Address</td><td>%s</td></tr>" % m['address']
                body += "<tr><td>Port</td><td>%d</td></tr>" % m['port']
            body += "<table>"
        else:
            machines = []
            for m_name in self.server.cfg.machines.get_machines(group):
                m = self.server.cfg.machines.get_machine(group, m_name)
                machine = dict(uri="/rest/machines_groups/%s/machines/%s" % (name, m_name),
                               name=m_name,
                               address=m['address'],
                               port=m['port'])
                machines.append(machine)
            data = dict(uri="/rest/machines_groups/%s" % name,
                         name=mg_name,
                         machines=machines)
            body = json.dumps(data)
        log.info("BODY: " + body)
        return body, "text/html"

    def post_rest_machines(self, group):
        size = int(self.headers["content-length"])
        data = self.rfile.read(size)
        log.info("received: " + data)
        data = json.loads(data)
        name = data['name']
        address = data['address']
        port = data['port']
        self.server.cfg.machines.add_machine(group, dict(name=name, address=address, port=port, group=group))
        return "1", "text/html"

    def get_rest_machine(self, group_name, name):
        machine = None
        for mg_name in self.server.cfg.machines.get_groups():
            if mg_name == group_name:
                for m_name in self.server.cfg.machines.get_machines(mg_name):
                    if m_name == name:
                        machine = self.server.cfg.machines.get_machine(mg_name, m_name)
                        break
        if machine == None:
            raise Http404NotFoundError()

        body = ""
        if "text/html" in self.headers['Accept']:
            body += "<h3>RedJack Server on %s</h3>" % socket.gethostname()
            body += "<h4>Machine %s</h4>" % name
            body += "<table>"
            body += "<tr><td>Name</td><td><a href='/rest/machines_groups/%s/machines/%s'>%s</a></td></tr>" % (group_name, name, name)
            body += "<tr><td>IP Address</td><td>%s</td></tr>" % machine['address']
            body += "<tr><td>Port</td><td>%d</td></tr>" % machine['port']
            body += "<table>"
        else:
            data = dict(uri="/rest/machines_groups/%s/machines/%s" % (group_name, m_name),
                        name=name,
                        group_uri="/rest/machines_groups/%s" % group_name,
                        group_name=group_name,
                        address=machine['address'],
                        port=machine['port'])
            body = json.dumps(data)
        return body, "text/html"

    def put_rest_machine(self, group, machine):
        size = int(self.headers["content-length"])
        data = self.rfile.read(size)
        log.info("received: " + data)
        data = json.loads(data)
        name = data['name']
        address = data['address']
        port = data['port']
        self.server.cfg.machines.modify_machine(group, machine, dict(name=name, address=address, port=port, group=group))
        return "1", "text/html"

    def get_rest_build_lines(self):
        body = ""
        if "text/html" in self.headers['Accept']:
            body = "<h3>RedJack Server on %s</h3>" % socket.gethostname()
            body += "<h4>Buil Lines</h4>"
            for bl_name in self.server.cfg.build_lines.get_build_lines():
                body += "<a href='/rest/build_lines/%s'>%s</a><br/>" % (bl_name, bl_name)
        else:
            data = []
            for bl_name in self.server.cfg.build_lines.get_build_lines():
                data.append(dict(uri="/rest/build_lines/%s" % bl_name,
                                 name=bl_name))
            body = json.dumps(data)
        return body, "text/html"

    def post_rest_build_lines(self):
        size = int(self.headers["content-length"])
        data = self.rfile.read(size)
        log.info("received: " + data)
        data = json.loads(data)
        name = data['name']
        initial_label = data['initial_label']
        interval = data['interval']
        quiet_period = data['quiet_period']
        self.server.cfg.build_lines.add_build_line(name, initial_label, interval, quiet_period)
        return "1", "text/html"

    def get_rest_build_line(self, name):
        bl = self.server.cfg.build_lines.get_state(name)
        if bl == None:
            raise Http404NotFoundError()

        body = ""
        if "text/html" in self.headers['Accept']:
            body = "<h3>RedJack Server on %s</h3>" % socket.gethostname()
            body += "<h4>Project %s</h4>" % name
            body += "Version: %d<br/>" % project.version
            body += "Label: %s<br/>" % project.label
            body += "Last build: %s<br/>" % (str(project.last_build) if project.last_build != None else "")
        else:
            #data = dict(uri="/rest/build_lines/%s" % name,
            #            name=name,
            #            version=.version,
            #            label=project.label,
            #            last_build=str(project.last_build) if project.last_build != None else "")
            data = bl
            body = json.dumps(data)
        return body, "text/html"

    def put_rest_build_line(self, build_line):
        size = int(self.headers["content-length"])
        data = self.rfile.read(size)
        log.info("received: " + data)
        state = json.loads(data)
        if 'paused' in state:
            self.server.cfg.build_lines.modify_state(build_line, state)
        if 'building' in state:
            self.server.sched.force_build(build_line)
        return "1", "text/html"

    def get_rest_builds(self, build_line):
        body = ""
        if "text/html" in self.headers['Accept']:
            pass
        else:
            data = self.server.cfg.build_lines.get_builds(build_line)
            body = json.dumps(data)
        return body, "text/html"

    def get_rest_build(self, build_line, build):
        body = ""
        if "text/html" in self.headers['Accept']:
            pass
        else:
            data = self.server.cfg.build_lines.get_build(build_line, build)
            body = json.dumps(data)
        return body, "text/html"

    def get_rest_changes(self, build_line, build):
        body = ""
        if "text/html" in self.headers['Accept']:
            pass
        else:
            data = self.server.cfg.build_lines.get_build_changes(build_line, build)
            body = json.dumps(data)
        return body, "text/html"

    def get_rest_tests(self, build_line, build):
        body = ""
        if "text/html" in self.headers['Accept']:
            pass
        else:
            data = self.server.cfg.build_lines.get_build_tests(build_line, build)
            body = json.dumps(data)
        return body, "text/html"

    def get_rest_logs(self, build_line, build):
        body = ""
        if "text/html" in self.headers['Accept']:
            pass
        else:
            data = self.server.cfg.build_lines.get_build_logs(build_line, build)
            body = json.dumps(data)
        return body, "text/html"

    def get_rest_cfg_settings(self, build_line):
        body = ""
        if "text/html" in self.headers['Accept']:
            pass
        else:
            data = self.server.cfg.build_lines.get_settings(build_line)
            body = json.dumps(data)
        return body, "text/html"

    def post_rest_cfg_settings(self, build_line):
        size = int(self.headers["content-length"])
        data = self.rfile.read(size)
        log.info("received: " + data)
        data = json.loads(data)
        name = data['name']
        value = data['value']
        log.info("setting %s %s" % (name, value))
        self.server.cfg.build_lines.add_parameter(build_line, name, value)
        return "1", "text/html"

    def put_rest_cfg_settings(self, build_line):
        size = int(self.headers["content-length"])
        data = self.rfile.read(size)
        log.info("received: " + data)
        data = json.loads(data)
        self.server.cfg.build_lines.set_settings(build_line, data)
        return "1", "text/html"

    def get_rest_cfg_script(self, build_line):
        body = ""
        if "text/html" in self.headers['Accept']:
            pass
        else:
            data = self.server.cfg.build_lines.get_script(build_line)
            body = json.dumps(data)
        return body, "text/html"

    def put_rest_cfg_script(self, build_line):
        size = int(self.headers["content-length"])
        data = self.rfile.read(size)
        log.info("received: " + data)
        data = json.loads(data)
        self.server.cfg.build_lines.set_script(build_line, data)
        return "1", "text/html"

    def get_rest_cfg_triggers(self, build_line):
        body = ""
        if "text/html" in self.headers['Accept']:
            pass
        else:
            data = self.server.cfg.build_lines.get_triggers(build_line)
            body = json.dumps(data)
        return body, "text/html"

    def post_rest_cfg_triggers(self, build_line):
        size = int(self.headers["content-length"])
        data = self.rfile.read(size)
        log.info("received: " + data)
        data = json.loads(data)
        name = data['name']
        type_ = data['type']
        url = data['url']
        directory = data['directory']
        self.server.cfg.build_lines.add_trigger(build_line, name, type_, url, directory)
        return "1", "text/html"

    def get_rest_cfg_trigger(self, build_line, trigger):
        body = ""
        if "text/html" in self.headers['Accept']:
            pass
        else:
            data = self.server.cfg.build_lines.get_trigger(build_line, trigger)
            body = json.dumps(data)
        return body, "text/html"

    def put_rest_cfg_trigger(self, build_line, trigger):
        size = int(self.headers["content-length"])
        data = self.rfile.read(size)
        log.info("received: " + data)
        data = json.loads(data)
        self.server.cfg.build_lines.modify_trigger(build_line, trigger, data)
        return "1", "text/html"

    def _prepare_breadcrumbs(self):
        crumbs = []
        link = ""
        for part in self.path.split("/"):
            if link == "/" and part == "":
                continue
            if part == "":
                crumb = "Home"
            else:
                crumb = " ".join([ p.capitalize() for p in part.split('_') ])
            if link == "/":
                link += part
            else:
                link += "/" + part
            crumbs.append((crumb, link))
        return crumbs

    def _handle_page(self, template_file, title, menu, action_menu=[], local_ctx={}):
        tpl = Template(filename=os.path.join(templates_dir, template_file), lookup=template_lookup)
        breadcrumbs = self._prepare_breadcrumbs()
        context = dict(title=title, breadcrumbs=breadcrumbs, menu=menu, action_menu=action_menu)
        context.update(local_ctx)
        body = tpl.render(**context)
        return body, "text/html"
        
    def get_root(self):
        menu = [('BUILD LINES', '/build_lines'), ('SETTINGS', '/settings'),
                ('MACHINES GROUPS', '/machines_groups')]
        return self._handle_page("main.html", "Home", menu)
    def get_settings(self):
        menu = [('GENERAL', '/settings/general'), ('EMAIL', '/settings/email'),
                ('VARIABLES', '/settings/variables')]
        return self._handle_page("main.html", "Settings", menu)
    def get_settings_general(self):
        menu = []
        return self._handle_page("main.html", "General settings", menu)
    def get_settings_email(self):
        menu = []
        return self._handle_page("main.html", "E-mail settings", menu)
    def get_settings_variables(self):
        menu = []
        return self._handle_page("main.html", "Common variables", menu)
    def get_machines_groups(self):
        action_menu = [('ADD GROUP', 'add_group')]
        return self._handle_page("machines_groups.html", "Machines' groups", [], action_menu)
    def get_machines_group(self, group):
        action_menu = [('ADD MACHINE', 'add_machine')]
        return self._handle_page("machines_group.html", "Machines' group: "+group,
                                 [], action_menu)
    def get_machines(self, group):
        menu = []
        return self._handle_page("main.html", "Machines from %s group" % group, menu)
    def get_machine(self, group, machine):
        return self._handle_page("machine.html", "Machine: "+machine, [], [('MODIFY MACHINE', 'modify_machine')])
    def get_build_lines(self):
        return self._handle_page("build_lines.html", "Build lines", [], [('ADD BUILD LINE', 'add_build_line')])
    def get_build_line(self, name):
        menu = [('BUILDS', '/build_lines/%s/builds' % name),
                ('CONFIGURATION', '/build_lines/%s/config' % name)]
        action_menu =[('FORCE BUILD', 'force_build'), ('PAUSE', 'pause'), ('RESUME', 'resume')]
        return self._handle_page("build_line.html", "Build line: "+name, menu, action_menu)
    def get_builds(self, name):
        menu = []
        return self._handle_page("builds.html", "Builds in "+name, menu)
    def get_build(self, build_line, build):
        menu = [('CHANGES', '/build_lines/%s/builds/%s/changes' % (build_line, build)),
                ('TESTS', '/build_lines/%s/builds/%s/tests' % (build_line, build)),
                ('LOGS', '/build_lines/%s/builds/%s/logs' % (build_line, build))]
        title = "Build <span class='page-title-emph'>%s</span> in <span class='page-title-emph'>%s</span>" % (build, build_line)
        return self._handle_page("build.html", title, menu)
    def get_changes(self, build_line, build):
        menu = []
        title = "Build <span class='page-title-emph'>%s</span> changes in <span class='page-title-emph'>%s</span>" % (build, build_line)
        return self._handle_page("changes.html", title, menu)
    def get_tests(self, build_line, build):
        menu = []
        title = "Build <span class='page-title-emph'>%s</span> tests in <span class='page-title-emph'>%s</span>" % (build, build_line)
        return self._handle_page("tests.html", title, menu)
    def get_logs(self, build_line, build):
        menu = []
        title = "Build logs <span class='page-title-emph'>%s</span> in <span class='page-title-emph'>%s</span>" % (build, build_line)
        return self._handle_page("logs.html", title, menu)
    def get_config(self, name):
        menu = [('SETTINGS', '/build_lines/%s/config/settings' % name),
                ('TRIGGERS', '/build_lines/%s/config/triggers' % name),
                ('SCRIPT', '/build_lines/%s/config/script' % name),
                ('REPORTING', '/build_lines/%s/config/reporting' % name)]
        return self._handle_page("main.html", "Config of "+name, menu)
    def get_cfg_script(self, name):
        return self._handle_page("script.html", "Build script for "+name, [])
    def get_cfg_triggers(self, name):
        return self._handle_page("triggers.html", "Triggers of "+name, [], [('ADD TRIGGER', 'add_trigger')])
    def get_cfg_trigger(self, build_line, trigger):
        return self._handle_page("trigger.html", "Trigger %s of %s" % (trigger, build_line), [])
    def get_cfg_reporting(self, name):
        menu = []
        return self._handle_page("main.html", "Reporting of %s" % (name), menu)
    def get_cfg_settings(self, name):
        return self._handle_page("cfg_settings.html", "Settings of %s" % (name), [], [('ADD PARAMETER', 'add_parameter')])

    def get_static(self, fname):
        log.debug("handle root "+fname)
        fpath = os.path.join("redjack", fname)
        if fname.endswith(".png") or fname.endswith(".ttf") or fname.endswith(".otf"):
            mode = "rb"
        else:
            mode = "r"
        f = open(fpath, mode)
        body = f.read()
        f.close()
        if fname.endswith(".png"):
            #log.info("img %s %d" % (fpath, len(body)))
            mime = "image/png"
        elif fname.endswith(".ttf"):
            mime = "font/ttf"
        elif fname.endswith(".otf"):
            mime = "font/opentype"
        elif fname.endswith(".js"):
            mime = "text/javascript"
        else:
            mime = "text/html"
        return body, mime

    def _do_request(self, method):
        #log.info("do " + method)
        body, found, mime = self._map_url(method)
        if not found and "text/html" in self.headers['Accept']:
            body = "<h3>RedJack Server on %s</h3>Page not found<br/><a href='/rest'>REST API</a>" % socket.gethostname()
            self.send_response(404)
        else:
            self.send_response(200)
        self.send_header("Content-type", mime)
        self.send_header("Content-length", str(len(body)))

        self.end_headers()
        self.wfile.write(body)

        # shut down the connection
        self.wfile.flush()
        self.connection.shutdown(1)

    def do_GET(self):
        self._do_request("get")

    def do_POST(self):
        self._do_request("post")

    def do_PUT(self):
        self._do_request("put")
