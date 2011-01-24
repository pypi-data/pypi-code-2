#!/usr/bin/python

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

from __future__ import print_function, division
from future_builtins import *
import sys
import os
import re
import killableprocess
import datetime
import time
import yaml
import httplib
import sqlite3
import pprint
import codecs
import logging
import logging.handlers
import smtplib
import socket
import collections
import threading
import pickle
import json
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from mako.template import Template

from triggers import trigger_classes
from web import RjSrvHTTPRequestHandler, ThreadedHTTPServer

default_fmt = "%(asctime)s  %(name)-12s %(message)s"
logging.basicConfig(level=logging.INFO,
                    format=default_fmt,
                    stream=sys.stdout)

log = logging.getLogger("rj.server")
handler = logging.handlers.RotatingFileHandler("rjserver.log",
                                               maxBytes=1024*1024,
                                               backupCount=5)
formatter = logging.Formatter(default_fmt)
handler.setFormatter(formatter)
log.addHandler(handler)


def initiate_triggers(cfg):
    for pn, proj in cfg.get_projects():
        triggers = []
        for idx, trigger in enumerate(proj.pcfg['monitor']['triggers']):
            trigger_type = proj.get_val(trigger, 'type')
            if not trigger_type in trigger_classes:
                raise Exception("trigger %s is not supported" % trigger['type'])
            trigger = cfg.replace_variables_recur(proj.pcfg, trigger)
            t = trigger_classes[trigger_type](proj, trigger_type, trigger, idx)
            t.prepare()
            triggers.append(t)
        proj.pcfg['monitor']['triggers'] = triggers

class Job(object):
    STATE_INIT = "init"
    STATE_EXECUTING = "executing"
    STATE_COMPLETED = "completed"

    def __init__(self, proj, root, job_info, idx, build_id):
        self.proj = proj
        self.root = root
        self.job_info = job_info
        self.idx = idx
        self.state = Job.STATE_INIT
        self.build_id = build_id

        self._save_state()

    def _save_state(self):
        self.proj.save_job_state(self)

    def _pick_machine(self):
        if not 'machine' in self.job_info:
            self.machine = self.proj.cfg.machines.get_machine('any', 'localhost')
        else:
            machine = None
            for group in self.root['machines'].get_groups():
                if self.job_info['machine'] in self.root['machines'].get_machines(group):
                    machine = self.root['machines'].get_machine[self.job_info['machine']]
                    break
            if machine == None:
                machine = self.root['machines'].get_machine('any', 'localhost')
            self.machine = machine

    def _agent_send(self, uri, data):
        conn = httplib.HTTPConnection(self.machine['address'], self.machine['port'])
        conn.request("PUT", uri, data)
        try:
            resp = conn.getresponse()
        except Exception, e:
            log.exception(e)
        body = resp.read()
        conn.close()
        #log.info(body)
        #log.info(resp.status)
        # TODO: check status

    def _agent_recv(self, uri):
        conn = httplib.HTTPConnection(self.machine['address'], self.machine['port'])
        conn.request("GET", uri, headers={"Accept": "text/json"})
        try:
            resp = conn.getresponse()
        except Exception, e:
            log.exception(e)
        body = resp.read()
        conn.close()
        #log.info(">>>%s<<<" % body)
        #log.info(resp.status)
        # TODO: check status
        return body

    def start(self):
        self._pick_machine()
        log.info("%s: starting job '%s' on machine %s" % (self.proj.name, str(self.job_info), self.machine['address']))
        self._agent_send("/job", json.dumps(dict(self.job_info)))
        log.info("%s: job '%s' passed to machine %s" % (self.proj.name, str(self.job_info), self.machine['address']))
        self.state = Job.STATE_EXECUTING
        self._save_state()

    def update_state(self):
        body = self._agent_recv("/status")
        self.status = json.loads(body)
        log.info("%s: job '%s' is %s" % (self.proj.name, str(self.job_info), self.status['state']))
        if self.status['state'] == 'completed':
            self.state = Job.STATE_COMPLETED
            self.exitcode = self.status['exitcode']
            self.completion_status = self.status['completion_status']
            self._save_state()

            self.execlog = unicode(self._agent_recv("/job-log"), errors='ignore')
            #f = codecs.open(os.path.join(self.proj.bdir, "job-%d.txt" % self.idx), "wt", "utf-8")
            f = open(os.path.join(self.proj.bdir, "job-%d.txt" % self.idx), "wb")
            f.write(self.execlog)
            f.close()
            log.debug("%s\n%s\n%s" % ("v"*50, self.execlog, "^"*50))
        self._save_state()

def lock_db(method):
        def lock_run_unlock(self, *args, **kwargs):
            self.dblock.acquire()
            cursor = self.conn.cursor()
            try:
                result = method(self, cursor, *args, **kwargs)
            finally:
                cursor.close()
                self.dblock.release()
            return result
        return lock_run_unlock

class Project(object):
    def __init__(self, name, initial_label, interval, quiet_period, cfg):
        self.cfg = cfg
        self.name = name
        #self.pcfg = pcfg

        # setup database
        if not os.path.isdir(name):
            os.makedirs(name)
        self.dblock = threading.Lock()
        self.conn = sqlite3.connect('%s/build_line.db' % name, check_same_thread=False)
        crsr = self.conn.cursor()
        crsr.execute("CREATE TABLE IF NOT EXISTS project (field TEXT UNIQUE, value TEXT)") # stored fields: version
        crsr.execute("CREATE TABLE IF NOT EXISTS settings (field TEXT UNIQUE, value TEXT)")
        crsr.execute("""CREATE TABLE IF NOT EXISTS batches (id INTEGER PRIMARY KEY,
                                                            idx INTEGER NOT NULL UNIQUE,
                                                            batch TEXT NOT NULL,
                                                            machines_group TEXT)""")#,
                                                            #CONSTRAINT u UNIQUE (idx))""")
        crsr.execute("""CREATE TABLE IF NOT EXISTS builds (id INTEGER PRIMARY KEY,
                                                           version INTEGER NOT NULL,
                                                           label TEXT NOT NULL,
                                                           start_date TEXT NOT NULL,
                                                           end_date TEXT,
                                                           state TEXT NOT NULL,
                                                           triggers BLOB)""")
        #self.conn.commit()
        crsr.execute("""CREATE TABLE IF NOT EXISTS jobs (id INTEGER PRIMARY KEY,
                                                         idx INTEGER NOT NULL,
                                                         batch TEXT NOT NULL,
                                                         machines_group TEXT,
                                                         state TEXT NOT NULL,
                                                         completion_status TEXT,
                                                         exitcode INTEGER,
                                                         logfile TEXT,
                                                         build INTEGER, 
                                                         FOREIGN KEY(build) REFERENCES builds(id))""")
        crsr.execute("""CREATE TABLE IF NOT EXISTS triggers (id INTEGER PRIMARY KEY,
                                                             name TEXT UNIQUE,
                                                             type TEXT NOT NULL,
                                                             settings BLOB,
                                                             state BLOB)""")
        self.conn.commit()

        # load settings
        self.settings = {}
        crsr.execute("SELECT field, value FROM settings")
        for name, value in crsr.fetchall():
            self.settings[name] = value
                
        crsr.close()

        if interval != None:
            self.add_parameter('interval', interval)
        if quiet_period != None:
            self.add_parameter('quiet_period', quiet_period)

        # set default state
        self.paused = True

        # set initial project params from config
        self.version = 0
        if initial_label == None:
            initial_label = self.settings['initial_label']
        else:
            self.add_parameter('initial_label', initial_label)
        init_num = initial_label.split("_")[-1].split("-")[-1].split(".")[-1]
        self.label_prefix = initial_label[:-len(init_num)]
        self._set_version(int(init_num))

        # initiate runtime state
        self.last_build = None
        self._build_steps = []
        self.curr_build_id = None

        # synchronize state with database
        self._load_state()
        self._save_state()

        self._prepare_triggers()

    def _prepare_triggers(self):   
        crsr = self.conn.cursor()
        crsr.execute("SELECT name, type, settings FROM triggers")
        self.triggers_objs = []
        for name, trigger_type, settings in crsr.fetchall():
            settings = pickle.loads(str(settings))
        #for idx, trigger in enumerate(proj.pcfg['monitor']['triggers']):
            #trigger_type = proj.get_val(trigger, 'type')
            if not trigger_type in trigger_classes:
                raise Exception("trigger %s is not supported" % trigger['type'])
            #trigger = cfg.replace_variables_recur(proj.pcfg, trigger)
            t = trigger_classes[trigger_type](self, trigger_type, name, settings)
            t.prepare()
            self.triggers_objs.append(t)
        crsr.close()

    @lock_db
    def load_trigger_state(self, crsr, name):
        crsr.execute("SELECT state FROM triggers WHERE name=?", (name, ))
        state = crsr.fetchone()
        if state and state[0]:
            #log.info("load state %s", str(type(state[0])))
            state = pickle.loads(str(state[0]))
        else:
            state = {}
        return state

    @lock_db
    def save_trigger_state(self, crsr, name, state):
        crsr.execute("SELECT id FROM triggers WHERE name=?", (name, ))
        tid = crsr.fetchone()
        assert tid and tid[0]
        state = pickle.dumps(state)
        crsr.execute("UPDATE triggers SET state=? WHERE id=?", (state, tid[0]))
        self.conn.commit()

    @lock_db
    def get_builds(self, crsr):
        crsr.execute("SELECT id, version, label, start_date, end_date, state FROM builds ORDER BY version DESC")
        blds = []
        for build_id, version, label, start_date, end_date, state in crsr.fetchall():
            blds.append(dict(build_id=build_id,
                             version=version,
                             label=label,
                             start_date=start_date,
                             end_date=end_date,
                             state=state))
        return blds       

    @lock_db
    def get_build(self, crsr, build):
        crsr.execute("SELECT id, version, label, start_date, end_date, state FROM builds WHERE label = ?",
                     (build,))
        build_id, version, label, start_date, end_date, state = crsr.fetchone()
        return dict(build_id=build_id,
                    version=version,
                    label=label, 
                    start_date=start_date,
                    end_date=end_date,
                    state=state)

    @lock_db
    def get_build_changes(self, crsr, build):
        crsr.execute("SELECT id, triggers FROM builds WHERE label = ?",
                     (build,))
        build_id, triggers = crsr.fetchone()
        return dict(build_id=build_id,
                    triggers=pickle.loads(str(triggers)))

    @lock_db
    def get_build_tests(self, crsr, build):
        crsr.execute("SELECT id, version, label, start_date, end_date, state FROM builds WHERE label = ?",
                     (build,))
        build_id, version, label, start_date, end_date, state = crsr.fetchone()
        return dict(build_id=build_id,
                    version=version,
                    label=label, 
                    start_date=start_date,
                    end_date=end_date,
                    state=state)

    @lock_db
    def get_build_logs(self, crsr, build):
        crsr.execute("SELECT id, version, label, start_date, end_date, state FROM builds WHERE label = ?",
                     (build,))
        build_id, version, label, start_date, end_date, state = crsr.fetchone()
        return dict(build_id=build_id,
                    version=version,
                    label=label, 
                    start_date=start_date,
                    end_date=end_date,
                    state=state)

    @lock_db
    def add_parameter(self, crsr, name, value):
        crsr.execute("INSERT OR REPLACE INTO settings (field, value) VALUES (?,?)", (name, str(value)))
        self.conn.commit()
        self.settings[name] = str(value)

    def get_settings(self):
        settings = []
        for n, v in self.settings.iteritems():
            if n == "script":
                continue
            settings.append(dict(name=n, value=v))
        return settings
    
    @lock_db
    def set_settings(self, crsr, parameters):
        for p in parameters:
            crsr.execute("UPDATE settings SET value = ? WHERE name = ?", (str(p['value']), p['name']))
            self.conn.commit()
            self.settings[p['name']] = str(p['value'])

    @lock_db
    def get_triggers(self, crsr):
        triggers = []
        crsr.execute("SELECT name, type, settings FROM triggers")
        for name, type_, settings in crsr.fetchall():
            data = pickle.loads(str(settings))
            data['name'] = name
            data['type'] = type_
            triggers.append(data)
        return triggers

    @lock_db
    def add_trigger(self, crsr, name, type_, url, directory):
        settings = dict(url=url, directory=directory)
        settings = pickle.dumps(settings)
        crsr.execute("INSERT OR REPLACE INTO triggers (name, type, settings) VALUES (?,?,?)", (name, type_, settings))
        self.conn.commit()
            
    @lock_db
    def get_trigger(self, crsr, trigger):
        crsr.execute("SELECT name, type, settings FROM triggers WHERE name=?", (trigger,))
        name, type_, settings = crsr.fetchone()
        data = pickle.loads(str(settings))
        data['name'] = name
        data['type'] = type_
        return data

    @lock_db
    def modify_trigger(self, crsr, trigger, data):
        settings = dict(url=data['url'], directory=data['directory'])
        settings = pickle.dumps(settings)
        crsr.execute("UPDATE triggers SET name=?, type=?, settings=? WHERE name=?",
                     (data['name'], data['type'], settings, trigger,))
        self.conn.commit()

    @lock_db
    def get_script(self, crsr):
        crsr.execute("SELECT value FROM settings WHERE field='script'")
        script = crsr.fetchone()
        data = dict(script=script[0])
        return data

    @lock_db
    def set_script(self, crsr, data):
        script = data['script']
        crsr.execute("INSERT OR REPLACE INTO settings (field, value) VALUES ('script',?)", (script,))
        self.conn.commit()

        # TODO: split script into parallel batches (future feature); for now treat script as one batch
        crsr.execute("DELETE FROM batches")
        self.conn.commit()
        crsr.execute("INSERT INTO batches (idx, batch, machines_group) VALUES (0, ?, 'any')", (script,))
        self.conn.commit()

    @lock_db
    def modify_step(self, crsr, old_idx, data):
        idx = data['idx']
        type_ = data['type']
        command = data['command']
        if old_idx == idx:
            crsr.execute("UPDATE steps SET type=?, command=? WHERE idx=?", (type_, command, idx))
            self.conn.commit()
        else:
            idx1 = min(idx, old_idx)
            idx2 = max(idx, old_idx)
            if idx < old_idx: # move up
                dx = 1
                dir = "DESC"
            else: # move down
                dx = -1
                dir = "ASC"
            crsr.execute("UPDATE steps SET idx=?, type=?, command=?  WHERE idx=?", (-1, type_, command, old_idx))
            self.conn.commit()
            crsr.execute("SELECT idx, type, command FROM steps WHERE idx>=? AND idx<=? ORDER BY idx %s" % dir, (idx1, idx2))
            for s in crsr.fetchall():
                crsr.execute("UPDATE steps SET idx=? WHERE idx=?", (s[0]+dx, s[0]))
                self.conn.commit()
            crsr.execute("UPDATE steps SET idx=?  WHERE idx=?", (idx, -1))
            self.conn.commit()
            
        
    @lock_db
    def pause(self, crsr):
        if self.paused:
            return
        crsr.execute("INSERT OR REPLACE INTO project (field, value) VALUES ('paused',?)", (str(True),))
        self.conn.commit()
        self.paused = True
    
    @lock_db
    def resume(self, crsr):
        if not self.paused:
            return
        crsr.execute("INSERT OR REPLACE INTO project (field, value) VALUES ('paused',?)", (str(False),))
        self.conn.commit()
        self.paused = False
    
    def is_paused(self):
        return self.paused
    
    def get_state(self):
        data = dict(name=self.name,
                    paused=self.paused,
                    version=self.version,
                    label=self.label,
                    building=(len(self._build_steps) > 0))
        return data

    @lock_db
    def modify_state(self, crsr, state):
        if 'paused' in state:
            self.paused = bool(state['paused'])
            crsr.execute("INSERT OR REPLACE INTO project (field, value) VALUES ('paused',?)", (str(self.paused),))
            self.conn.commit()

    @lock_db
    def _save_state(self, crsr):
        crsr.execute("INSERT OR REPLACE INTO project (field, value) VALUES ('version',?)", (str(self.version),))
        self.conn.commit()
        crsr.execute("INSERT OR REPLACE INTO project (field, value) VALUES ('paused',?)", (str(self.paused),))
        self.conn.commit()

    @lock_db
    def _load_state(self, crsr):
        crsr.execute("SELECT value FROM project WHERE field='version'")
        ver = crsr.fetchone()
        crsr.execute("SELECT value FROM project WHERE field='paused'")
        paused = crsr.fetchone()
        if ver != None:
            self._set_version(int(ver[0]))
        if paused != None:
            self.paused = (paused == True)

        log.info("Loaded BL %s state: paused:%s, version:%s, label:%s" % (self.name, str(self.paused), self.version, self.label))

    @lock_db
    def save_job_state(self, crsr, job):
        if job.state != Job.STATE_COMPLETED:
            crsr.execute("INSERT OR REPLACE INTO jobs (build, idx, batch, state) VALUES (?,?,?,?)",
                         (job.build_id, job.idx, "cmd...", job.state))
        else:
            crsr.execute("INSERT OR REPLACE INTO jobs (build, idx, batch, state, completion_status, exitcode, logfile) VALUES (?,?,?,?,?,?,?)",
                         (job.build_id, job.idx, "cmd...", job.state, job.completion_status, job.exitcode, "logfilepath..."))
        self.conn.commit()

    def _get_batches(self):
        self.dblock.acquire()
        crsr = self.conn.cursor()
        batches = []
        try:            
            crsr.execute("SELECT idx, batch, machines_group FROM batches ORDER BY idx ASC")
            for b in crsr.fetchall():
                batches.append(dict(idx=b[0], batch=b[1], machines_group=b[2]))
        finally:
            crsr.close()
            self.dblock.release()
        return batches

    def get_val(self, branch, variable, default=None):
        log.debug(">>>> get_val br:  %s" % str(branch))
        log.debug(">>>> get_val var:  %s" % str(variable))
        if branch == None:
            return default
        if not variable in branch:
            return default

        extra_vars = dict(version=self.version)
        val = self.cfg.replace_variables_recur(self.pcfg, branch[variable], extra_vars)
        log.debug(">>>> get_val val:  %s" % str(val))

        if variable in ['interval', 'quiet-period']:
            if val.endswith("s"):
                val = int(val[:-1])
            elif val.endswith("m"):
                val = int(val[:-1]) * 60
            elif val.endswith("h"):
                val = int(val[:-1]) * 60 * 60
            else:
                raise Exception('unsupported time unit in value %s of %s' % (val, variable))

        return val

    def _set_version(self, version):
        self.version = version
        self.label = "%s%s" % (self.label_prefix, self.version)

    @lock_db
    def _create_build(self, crsr):
        triggers = [ t for o, t in self.triggers ]
        triggers = pickle.dumps(triggers)
        
        crsr.execute("INSERT INTO builds (version, label, start_date, state, triggers) VALUES (?,?,?,?,?)",
                                  (self.version, self.label, self.last_build, 'started', triggers))
        self.conn.commit()
        return crsr.lastrowid

    def _start_build(self):
        batches = self._get_batches()
        if len(batches) == 0:
            log.info("no batches to execute - skip building")
            return
        self.last_build = datetime.datetime.now()
        self._set_version(self.version + 1)
        log.info("%s: do build: %s" % (self.name, self.label))

        self.curr_build_id = self._create_build()

        self._save_state()
        self.bdir = os.path.join(self.name, self.label)
        if not os.path.exists(self.bdir):
            os.makedirs(self.bdir)
        for idx, job in enumerate(batches):
            #job2 = {}
            #for k in job.iterkeys():
            #    v = self.get_val(job, k)
            #    job2[k] = v

            #if not "directory" in job2:
            #    directory = self.get_val(self.pcfg['build'], 'directory')
            #    if directory != None:
            #        job2["directory"] = directory

            self._build_steps.append(Job(self, self.cfg, job, idx+1, self.curr_build_id))

        self._build_steps[0].start()

    def _check_running_build(self):
        log.info("%s: check status of build execution" % self.name)
        all_completed = True
        self.successful = True
        for i, job in enumerate(self._build_steps):
            if job.state == Job.STATE_EXECUTING:
                job.update_state()
            if job.state == Job.STATE_COMPLETED:
                if job.completion_status != "ok" and not ('ignore-error' in job.job_info and job.job_info['ignore-error'] == True):
                    log.info("%s: build failed" % self.name)
                    self.successful = False
                    all_completed = True
                    break
                if i + 2 > len(self._build_steps):
                    break
                next_job = self._build_steps[i+1]
                if next_job.state == Job.STATE_INIT:
                    next_job.start()
            else:
                all_completed = False

        if all_completed:
            self._complete_build()
            self._do_report()
            self._old_build_steps = self._build_steps
            self._build_steps = []

    @lock_db
    def _complete_build(self, crsr):
        if self.successful:
            state = "successful"
        else:
            state = "failed"
        crsr.execute("UPDATE builds SET state=? WHERE id=?",
                     (state, self.curr_build_id))
        self.conn.commit()

    def _render_report(self):
        if self.successful:
            subject = "%s Build Successful: %s" % (self.name.capitalize(), self.label)
        else:
            subject = "%s Build Failed: %s" % (self.name.capitalize(), self.label)
        context = {"project": self.name.capitalize(), 
                   "successful": self.successful, 
                   "date": datetime.datetime.now().strftime("%Y.%m.%d %H:%M"),
                   "label": self.label, 
                   "subject": subject,
                   "triggers": self.triggers,
                   "jobs": self._build_steps}

        base_dir = os.path.dirname(os.path.abspath(__file__))
        tpl = Template(filename=os.path.join(base_dir, "templates", "mail", "master.html"))
        html = tpl.render(**context)
        log.debug(html)
        f = open(os.path.join(self.bdir, "report.html"), "w")
        f.write(html)
        f.close()

        return subject, "", html

    def _build_email(self, subject, text, html, from_addr, to_addrs):
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = from_addr
        msg['To'] = ", ".join(to_addrs)

        msg.attach(MIMEText(text, 'plain'))
        msg.attach(MIMEText(html, 'html'))

        return msg.as_string()

    def _send_report(self, subject, text, html):
        report_cfg = self.pcfg['report']
        if not 'email' in report_cfg:
            return
        email_cfg = report_cfg['email']
        if 'email' in self.cfg.root:
            root_email_cfg = self.cfg.root['email']
        else:
            root_email_cfg = None

        # get dest email addresses
        to_addrs = self.get_val(email_cfg, 'to')
        if to_addrs == None:
            to_addrs = self.get_val(root_email_cfg, 'to')
        if to_addrs == None:
            raise Exception("missing to_addrs")
        if isinstance(to_addrs, basestring):
            to_addrs = [to_addrs]
        # TODO: include-authors

        from_addr = self.get_val(email_cfg, 'from')
        if from_addr == None:
            from_addr = self.get_val(root_email_cfg, 'from')
        if from_addr == None:
            from_addr = 'missing@example.com'

        subject_prefix = self.get_val(email_cfg, 'subject-prefix')
        if subject_prefix == None:
            subject_prefix = self.get_val(root_email_cfg, 'subject-prefix')
        if subject_prefix != None:
            subject = "%s %s" % (subject_prefix, subject)
        mail = self._build_email(subject, text, html, from_addr, to_addrs)

        # get credentials
        username = None
        password = None
        credentials = self.get_val(email_cfg, 'credentials')
        if credentials == None:
            credentials = self.get_val(root_email_cfg, 'credentials')
        if credentials != None:
            f = open(credentials)
            for line in f.readlines():
                field, val = line.split("=")
                field = field.strip()
                val = val.strip()
                if field == "username":
                    username = val
                if field == "password":
                    password = val

        # The actual mail send
        smtpaddr = self.get_val(email_cfg, 'smtp')
        if smtpaddr == None:
            smtpaddr = self.get_val(root_email_cfg, 'smtp')
        if smtpaddr == None:
            raise Exception("missing smtp address")
        server = smtplib.SMTP(smtpaddr)
        tls = self.get_val(email_cfg, 'tls')
        if tls == None:
            tls = self.get_val(root_email_cfg, 'tls')
        if tls:
            server.starttls()
        if username != None and password != None:
            server.login(username, password)

        server.sendmail(from_addr, to_addrs, mail)
        server.quit()

    def _do_report(self):
        subject, text, html = self._render_report()
        #self._send_report(subject, text, html)

    def _check_triggers(self):
        self.triggers = []
        fire = False
        log.info("%s: checking triggers" % self.name)
        for trigger in self.triggers_objs:
            changes = trigger.get_changes()
            if len(changes['changesets']) > 0:
                fire = True
            self.triggers.append((trigger, changes))
        return fire

    def _get_interval(self):
        interval = self.settings['interval'].strip()
        if interval.endswith("s"):
            interval = int(interval[:-1])
        elif interval.endswith("m"):
            interval = int(interval[:-1]) * 60
        elif interval.endswith("h"):
            interval = int(interval[:-1]) * 60 * 60
        elif interval.endswith("d"):
            interval = int(interval[:-1]) * 60 * 60 * 24
        else:
            raise ValueError("Interval is in bad format: %s" % interval)
        return interval        

    def check_build(self, force_build=False):
        # if build is being executed
        if len(self._build_steps) > 0:
            self._check_running_build()
            return

        # otherwise start build if needed
        if self.last_build and not force_build:
            log.info("%s: checking build" % self.name)
            now = datetime.datetime.now()
            dt = now - self.last_build
            dt_needed = datetime.timedelta(seconds=self._get_interval())
            if dt > dt_needed:
                if self._check_triggers():
                    self._start_build()
            else:
                log.info("%s: check build: nothing (%s < %s)" % (self.name, dt, dt_needed))
        else:
            if force_build:
                log.info("%s: manually forced build" % self.name)
            else:
                log.info("%s: forced build in first server run" % self.name)
            self._check_triggers()
            self._start_build()

class BuildLines(object):
    def __init__(self, connection, dblock, cfg):
        self.cfg = cfg
        self.build_lines = {}

        self.conn = connection
        self.dblock = dblock

        build_lines = []
        for d in os.listdir("."):
            if os.path.isdir(d) and os.path.exists(os.path.join(d, "build_line.db")):
                build_lines.append(d)

        for bl in build_lines:
            self.add_build_line(bl, None, None, None)

    def get_build_lines(self):
        return self.build_lines.keys()
    def get_build_line(self, name):
        return self.build_lines[name]
    def add_build_line(self, name, initial_label, interval, quiet_period):
        bl = Project(name, initial_label, interval, quiet_period, self.cfg)
        self.build_lines[name] = bl
    def get_builds(self, build_line):
        return self.build_lines[build_line].get_builds()
    def get_build(self, build_line, build):
        return self.build_lines[build_line].get_build(build)
    def get_build_changes(self, build_line, build):
        return self.build_lines[build_line].get_build_changes(build)
    def get_build_tests(self, build_line, build):
        return self.build_lines[build_line].get_build_tests(build)
    def get_build_logs(self, build_line, build):
        return self.build_lines[build_line].get_build_logs(build)
    def get_settings(self, build_line):
        return self.build_lines[build_line].get_settings()
    def add_parameter(self, build_line, name, value):
        self.build_lines[build_line].add_parameter(name, value)
    def set_settings(self, build_line, parameters):
        self.build_lines[build_line].set_settings(parameters)
    def get_script(self, build_line):
        return self.build_lines[build_line].get_script()
    def set_script(self, build_line, data):
        self.build_lines[build_line].set_script(data)
    def get_triggers(self, build_line):
        return self.build_lines[build_line].get_triggers()
    def add_trigger(self, build_line, name, type_, url, directory):
        self.build_lines[build_line].add_trigger(name, type_, url, directory)
    def get_trigger(self, build_line, trigger):
        return self.build_lines[build_line].get_trigger(trigger)
    def modify_trigger(self, build_line, trigger, data):
        self.build_lines[build_line].modify_trigger(trigger, data)
    def get_state(self, build_line):
        return self.build_lines[build_line].get_state()
    def modify_state(self, build_line, state):
        self.build_lines[build_line].modify_state(state)

class Config(object):
    def __init__(self):
        self.conn = sqlite3.connect('rj.db', check_same_thread=False)
        self.dblock = threading.Lock()
        log.info("Loading machines")
        self.machines = Machines(self.conn, self.dblock)
        log.info("Loading build lines")
        self.build_lines = BuildLines(self.conn, self.dblock, self)
        log.info("Config loaded")

    def _replace_variables2(self, root, branch):
        if isinstance(branch, basestring):
            for var in re.findall("\${(.*?)}", branch):
                if var in root:
                    val = root[var]
                    branch = branch.replace("${%s}" % var, val)
                else:
                    raise Exception("cannot find value for variable %s" % var)
        elif isinstance(branch, dict):
            for k, v in branch.iteritems():
                branch[k] = self._replace_variables(root, v)
        elif isinstance(branch, list):
            branch = [ self._replace_variables(root, v) for v in branch ]
        return branch

    def replace_variables_recur(self, pcfg, branch, extra_vars={}):
        if isinstance(branch, basestring):
            val = branch
            val = self.replace_variables(extra_vars, val)
            val = self.replace_variables(pcfg, val)
            val = self.replace_variables(self.root, val)
            return val
        elif isinstance(branch, dict):
            for k, v in branch.iteritems():
                branch[k] = self.replace_variables_recur(pcfg, v, extra_vars)
        elif isinstance(branch, list):
            branch = [ self.replace_variables_recur(pcfg, v, extra_vars) for v in branch ]
        elif isinstance(branch, bool):
            pass
        else:
            raise Exception("unrecognized node type %s" % str(type(branch)))
        return branch

    def replace_variables(self, branch, value):
        if not isinstance(value, basestring):
            return value
        #log.info("replace_variables", branch, value, type(value))
        for var_name in re.findall("\${(.*?)}", value):
            if not var_name in branch:
                continue
            val = branch[var_name]
            val = self.replace_variables(branch, val)
            if branch != self.root:
                val = self.replace_variables(self.root, val)
            val = self.replace_variables(branch, val)
            value = value.replace("${%s}" % var_name, str(val))
        return value


    def _load_project(self, name, fname):
        pcfg1 = yaml.load(open(fname))
        exts = pcfg1.get('extends', [])
        pcfg = {}
        for ext in exts:
            log.info(ext)
            e = yaml.load(open(ext))
            pcfg.update(e)
        pcfg.update(pcfg1)

        #pcfg = self._replace_variables(pcfg, pcfg)

        p = Project(name, self, pcfg)
        return p

    def load_config(self):
        cfg = yaml.load(open("config.rj"))
        #cfg2 = yaml.load(open(cfg['extends']))
        #cfg2.update(cfg)

        # process machines
        for name, machine in cfg['machines'].iteritems():
            # do ping
            pass
        if not 'any' in cfg['machines'] and not 'localhost' in cfg['machines']['any']:
            cfg['machines']['any'] = {'localhost': {'address': '127.0.0.1', 'port': 8081}}

        self.root = cfg

        # process projects
        projs = {}
        for pn, proj in cfg['projects'].iteritems():
            projs[pn] = self._load_project(pn, proj)
        cfg['projects-states'] = projs

class Machines(object):
    def __init__(self, connection, dblock):
        self.conn = connection
        self.dblock = dblock
        self.dblock.acquire()
        crsr = self.conn.cursor()
        try:
            crsr.execute("CREATE TABLE IF NOT EXISTS machines_groups (id INTEGER PRIMARY KEY, name TEXT UNIQUE)")
            self.conn.commit()
            crsr.execute("""CREATE TABLE IF NOT EXISTS machines (id INTEGER PRIMARY KEY,
                                                                 name TEXT NOT NULL UNIQUE,
                                                                 address TEXT NOT NULL,
                                                                 port INTEGER NOT NULL,
                                                                 mgroup INTEGER,
                                                                 FOREIGN KEY(mgroup) REFERENCES machines_groups(id))""")
            self.conn.commit()
    
            crsr.execute("SELECT id, name FROM machines_groups")
            self.groups = {}
            self.group_ids = {}
            for group in crsr.fetchall():
                self.groups[group[1]] = {}
                self.group_ids[group[1]] = group[0]
                
            crsr.execute("""SELECT machines.id, machines.name, machines.address, machines.port, machines_groups.name
                              FROM machines,machines_groups
                              WHERE machines.mgroup=machines_groups.id""")
            for machine in crsr.fetchall():
                self.groups[machine[4]][machine[1]] = {'id': machine[0], 'name': machine[1],
                                                       'address': machine[2], 'port': machine[3]}
                
        finally:
            crsr.close()
            self.dblock.release()
            
        if not 'any' in self.groups:
            self.add_group('any')
            self.add_machine('any', {'name': 'localhost', 'address': '127.0.0.1', 'port': 8081})
        
    def add_group(self, name):
        if not name in self.groups:
            self.dblock.acquire()
            crsr = self.conn.cursor()
            try:
                crsr.execute("INSERT INTO machines_groups (name) VALUES (?)", (name,))
                self.conn.commit()
                self.groups[name] = {}
                self.group_ids[name] = crsr.lastrowid
            finally:
                crsr.close()
                self.dblock.release()
        return self.group_ids[name]
    def remove_group(self, name):
        if name in self.groups:
            del self.groups[name]
    def rename_group(self, old_name, new_name):
        if old_name in self.groups and not new_name in self.groups:
            self.groups[new_name] = self.groups[old_name]
            del self.groups[old_name] 
    def get_groups(self):
        return self.groups.keys()
    def add_machine(self, group, machine):
        if group in self.groups and not machine['name'] in self.groups[group]:
            self.dblock.acquire()
            crsr = self.conn.cursor()
            try:
                crsr.execute("INSERT INTO machines (name, address, port, mgroup) VALUES (?,?,?,?)",
                                  (machine['name'], machine['address'], machine['port'], self.group_ids[group]))
                self.conn.commit()
            finally:
                crsr.close()
                self.dblock.release()
            self.groups[group][machine['name']] = machine
    def remove_machine(self, group, name):
        if group in self.groups and not name in self.groups[group]:
            del self.groups[group][name]
    def modify_machine(self, group, name, machine):
        if group in self.groups and name in self.groups[group]:
            self.dblock.acquire()
            crsr = self.conn.cursor()
            try:
                log.info("U"*30)
                crsr.execute("UPDATE machines SET name=?, address=?, port=? WHERE name=?",
                                  (machine['name'], machine['address'], machine['port'], name))
                self.conn.commit()
            finally:
                crsr.close()
                self.dblock.release()
            self.groups[group][name] = machine
    def get_machines(self, group):
        return self.groups[group].keys()
    def get_machine(self, group, machine):
        return self.groups[group][machine]

class Scheduler(object):
    def __init__(self, cfg):
        self.cfg = cfg
        self.forced_builds = {}
        self.cond = threading.Condition()
        
    def force_build(self, name):
        self.forced_builds[name] = True
        self.cond.acquire()
        self.cond.notify()
        self.cond.release()

    def run(self):
        while True:
            for name in self.cfg.build_lines.get_build_lines():
                bl = self.cfg.build_lines.get_build_line(name)
                if bl.is_paused():
                    log.info("%s: is paused" % name)
                    continue
                if name in self.forced_builds:
                    forced = self.forced_builds[name]
                    if forced:
                        log.info("%s: forced build" % name)
                else:
                    forced = False
                bl.check_build(forced)
                self.forced_builds[name] = False
            self.cond.acquire()
            self.cond.wait(5)
            self.cond.release()


def main():
    log.info("Starting RedJack server")

    log.info("Loading configuration")
    cfg = Config()
#    cfg.load_config()

#    initiate_triggers(cfg)

    # run localhost agent
    log.info("Starting local agent")
    localhost = cfg.machines.get_machine('any', 'localhost')
    bin_path = os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), "rjagent")
    cmd = "%s %s %d" % (bin_path, localhost['address'], localhost['port'])
    p = killableprocess.Popen(cmd, shell=True, stdout=killableprocess.PIPE, stderr=killableprocess.STDOUT)

    # check if agent is running
    time.sleep(1)
    p.poll()
    if p.returncode != None:
        txt = p.stdout.read()
        log.error("Problem occured during starting local agent:")
        log.error(txt)
        return 1

    # prepare http server on separate thread
    log.info("Starting internal HTTP server")
    ThreadedHTTPServer.allow_reuse_address = True
    #srv = ThreadedHTTPServer((cfg.root['address'], int(cfg.root['port'])), RjSrvHTTPRequestHandler)
    srv = ThreadedHTTPServer(("0.0.0.0", 8080), RjSrvHTTPRequestHandler)
    srv.cfg = cfg
    
    # prepare scheduler
    log.info("Starting scheduler")
    sched = Scheduler(cfg)
    srv.sched = sched

    # start http thread
    threading.Thread(target=srv.serve_forever).start()
    
    #try:
    #    while True:
    #        time.sleep(5)
    #except KeyboardInterrupt, e:
    #    sys.exit()

    # start scheduler
    try:
        sched.run()
    except KeyboardInterrupt, e:
        log.info("Received Ctrl-C. Quitting")
    except Exception, e:
        log.error("Received unexpected exception. Qutting.")
        log.exception(e)
    finally:
        srv.shutdown()
        p.kill()
        p.wait()
        log.info("Finished")
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
