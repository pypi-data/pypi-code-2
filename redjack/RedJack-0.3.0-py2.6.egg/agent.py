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

import socket
import os
import os.path
import threading
import random
import time
import Queue
import imp
import inspect
import zipimport
import sys
import platform
import subprocess
import logging
import logging.handlers
import signal
import traceback
import select
import json
import platform
#import fcntl
import BaseHTTPServer

default_fmt = "%(asctime)s  %(name)-12s %(message)s"
logging.basicConfig(level=logging.INFO,
                    format=default_fmt,
                    stream=sys.stdout)

log = logging.getLogger("rj.agent")
log.setLevel(logging.INFO)
handler = logging.handlers.RotatingFileHandler("rjagent-%s.log" % socket.gethostname(),
                                               maxBytes=1024*1024,
                                               backupCount=5)
formatter = logging.Formatter(default_fmt)
handler.setFormatter(formatter)
log.addHandler(handler)


def is_linux():
    return platform.system() == "Linux"

class RjHTTPRequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/":
            if "text/html" in self.headers['Accept']:
                body = "<h3>RedJack Agent on %s</h3>" % socket.gethostname()
                body += "Last job status: <a href='/status'>link</a><br/>"
                body += "Last job log: <a href='/job-log'>link</a>"
                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.send_header("Content-length", str(len(body)))
        elif self.path == '/status':
            status = self.server.agent.get_job_status()
            self.send_response(200)
            if "text/html" in self.headers['Accept']:
                body = "<h3>RedJack Agent on %s</h3>" % socket.gethostname()
                body += "Last job: %s<br/>" % str(self.server.agent.current_job)
                body += "Last job state: %s<br/>" % status['state']
                body += "Last job exitcode: %s<br/>" % str(status['exitcode'])
                body += "Last job completion status: %s<br/>" % str(status['completion_status'])
                body += "Last job log: <a href='/job-log'>link</a>"
                self.send_header("Content-type", "text/html")
            else:
                status["jobLogUri"] = "/job-log"
                status["newJobUri"] = "/job"
                body = json.dumps(status)
                self.send_header("Content-type", "text/json")
            self.send_header("Content-length", str(len(body)))
        elif self.path == '/job-log':
            body = self.server.agent.get_job_log()
            self.send_response(200)
            self.send_header("Content-type", "text/plain")
            self.send_header("Content-length", str(len(body)))
        else:
            self.send_error(404)
            # shut down the connection
            self.wfile.flush()
            self.connection.shutdown(1)
            return

        self.end_headers()
        self.wfile.write(body)

        # shut down the connection
        self.wfile.flush()
        self.connection.shutdown(1)


    def do_PUT(self):
        if self.path != "/job":
            log.info("wrong path")
            self.send_error(400)
            return
        size = int(self.headers['Content-Length'])
        body = self.rfile.read(size)
        log.debug("do put %s" % body)

        try:
            data = json.loads(body)
            self.server.agent.start_job(data) # TODO: check returned status
            log.debug("do put completed")
        except:
            self.send_error(400)
            return

        self.send_response(200)
        #self.send_header("Content-type", "text/xml")
        #self.send_header("Content-length", str(len(response)))
        #self.end_headers()

        # shut down the connection
        self.wfile.flush()
        self.connection.shutdown(1)

class Capabilities:
    def __init__(self):
        self.caps = {}
        caps = self.caps
        caps['arch'] = platform.architecture()[0]
        caps['system'] = platform.system()
        caps['libc'] = "-".join(platform.libc_ver())
        caps['machine'] = platform.machine()
        caps['node'] = platform.node()
        caps['platform'] = platform.platform()
        caps['processor'] = platform.processor()
        #caps['python_build'] = platform.python_build()
        #caps['python_compiler'] = platform.python_compiler()
        caps['system_release'] = platform.release()
        caps['system_version'] = platform.version()

        if caps['system'] == "Linux":
            caps['linux_dist'] = "-".join(platform.dist())
            for key in ["USER", "GROUP", "HOME", "PATH", "LANG", "OSTYPE", "PYTHONPATH", "HOST", "MACHTYPE"]:
                if os.environ.has_key(key):
                    caps[key] = os.environ[key]
        elif caps['system'] == "Windows":
            caps['win32_ver'] = "-".join(platform.win32_ver())
            for key in ["USERNAME", "USERDOMAIN", "HOMEPATH", "PATH", "COMPUTERNAME", "OS"]:
                caps[key] = os.environ[key]
        elif caps['system'] == "Mac":
            caps['mac_ver'] = platform.mac_ver()

        self._check_prog("python", "python -V", lambda t: t.split()[1])
        self._check_prog("java", "java -version", lambda t: t.split()[2].strip("\""))
        self._check_prog("perl", "perl -v", lambda t: t.split()[3][1:])
        self._check_prog("gcc", "gcc -dumpversion", lambda t: t)

        log.info("Agent capabilities:")
        for key, val in caps.iteritems():
            log.info("\t%s: %s" % (key, str(val)))

    def _popen(self, cmd):
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        err = p.wait()
        txt = ""
        if err == 0:
            txt = p.stdout.read().strip()
        return err, txt

    def _check_prog(self, prog, cmd, func):
        err, txt = self._popen(cmd)
        if err == 0:
            self.caps[prog] = func(txt)

    def get(self):
        return self.caps

class Agent(object):
    def __init__(self, ip_address, port):
        log.info("starting agent")
        self.ip_address = ip_address
        self.port = port

        self.job_runner = None
        self.finish = False
        self.current_job = None

        try:
            signal.signal(signal.SIGINT, self.__keyboard_interrupt_handler)
        except:
            pass

        #self.caps = Capabilities()
        self._setup_http_server()

        self._restart()
        self.restart = False

    def run(self):
        log.info("agent started serving on %s:%d" % (self.ip_address, self.port))
        # Run the server's main loop
        while not self.finish:
            try:
                iwtd, owtd, ewtd = select.select([self.server.socket], [], [], 5)
            except select.error, e:
                if e[0] == 4: # Interrupted system call, in bg Ctrl-C handler is called and finish flags is set
                    continue
            except:
                log.exception("Exception in select")
                continue
            if iwtd:
                self.server.handle_request()
            if self.restart:
                self.restart = False
                self._restart()

    def _setup_http_server(self):
        # Create server
        BaseHTTPServer.HTTPServer.allow_reuse_address = True
        self.server = BaseHTTPServer.HTTPServer((self.ip_address, self.port), RjHTTPRequestHandler)
        #self.server.socket.settimeout(5) # non-blocking does not work in Windows - requires more work
        self.server.agent = self

    def _restart(self):
        self.queue = Queue.Queue()
        self.job_runner = JobRunner(self.queue, self)

    def __keyboard_interrupt_handler(self, signum, frame):
        #log.info('Signal handler called with signal', signum)
        log.info("manual stop")
        self._quit()

    def _validate_job(self, job):
        commands = ["exec"]
        found = False
        for cmd in commands:
            if cmd in job:
                found = True
                break
        if not found:
            status = "unsupported command"
            log.info("job validating: %s" % status)
            return status
        else:
            log.debug("job validating: ok")
            return None

    def start_job(self, job):
        log.info("start job %s" % str(job))
        #status = self._validate_job(job)
        #if status:
        #    return status
        self.current_job = job
        self.queue.put(job)
        return None

    def get_job_status(self):
        log.info("get job status")
        result = self.job_runner.read_status()
        log.info("\t%s" % str(result))
        return result

    def get_job_log(self):
        log.info("get job log")
        return self.job_runner.read_log()

    def _quit(self):
        log.info("finish in 5 secs")
        self.server.server_close()
        if self.job_runner:
            self.job_runner.finish = True
        self.finish = True

#     def sepuku(self):
#         log.info("sepuku")
#         while not self.queue.empty():
#             time.sleep(5)
#         self._quit()
#         return True


class JobRunner(threading.Thread):
    def __init__(self, queue, agent):
        threading.Thread.__init__(self)
        self.finish = False
        self.queue = queue
        self.agent = agent
        self.start()
        self.status = ("waiting", 0, "")

    def run(self):
        while not self.finish:
            try:
                job = self.queue.get(True, 5)
            except Queue.Empty:
                continue
            try:
                self._handle_job(job)
            except Exception, e:
                log.exception(e)
                log.error("connection to server broken - try to reconnect")
                self.agent.restart = True
                break
            except:
                log.exception("unexpected exception occured")
                self.agent._quit()
                break

    def _handle_job(self, job):
        log.info("doing the job")
        self.status = ("starting", 0, "", "")
        if "batch" in job:
            if is_linux():
                batch_path = "job.sh"
            else:
                batch_path = "job.bat"
            batch_path = os.path.join(os.getcwd(), batch_path)
            b = open(batch_path, "w")
            if is_linux():
                b.write("#!/bin/bash\n")
            b.write(job["batch"])
            b.close()
            os.chmod(batch_path, 0700)
            if "directory" in job:
                directory = job["directory"]
            else:
                directory = os.getcwd()
            job_output_path = "job_output.txt"
            job_output = open(job_output_path, "w")
            try:
                p = subprocess.Popen(batch_path, shell=True, cwd=directory, stdout=job_output, stderr=subprocess.STDOUT)
            except Exception, e:
                self.status = ("completed", 0, "exception", str(e))
                return
            self.status = ("started", 0, "", "")
            execlog = ""
            p.poll()
            while p.returncode == None:
                time.sleep(2)
                try:
                    #execlog += p.stdout.read()
                    self.status = ("started", 0, "", execlog)
                except IOError:
                    pass
                p.poll()
            exitcode = p.wait()
            job_output.close()
            if exitcode == 0:
                completion_status = "ok"
            else:
                completion_status = "failed"
            job_output = open(job_output_path, "r")
            execlog = job_output.read()
            job_output.close()
            self.status = ("completed", exitcode, completion_status, execlog)
            log.info("job completed")
            log.info(self.status)

    def read_status(self):
        status = dict(state=self.status[0],
                      exitcode=self.status[1],
                      completion_status=self.status[2])
        return status

    def read_log(self):
        return self.status[-1]

def main():
    a = Agent(sys.argv[1], int(sys.argv[2]))
    a.run()


if __name__ == '__main__':
    main()
