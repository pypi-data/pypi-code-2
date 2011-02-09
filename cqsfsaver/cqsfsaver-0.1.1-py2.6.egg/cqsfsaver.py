#!/usr/bin/env python
#-*- coding:utf-8 -*-

#-*- coding:utf-8 -*-

import sys
import os
import re
import cgi
import BaseHTTPServer
import logging
import simplejson as json
import Tkinter, tkFileDialog, tkMessageBox

PATH_PATTERN = re.compile('^/\?key=(\w+)$', re.U)
PORTS_RANGE = range(30778,31336)

CSS_URL_POST = 'css_url'
CSS_TEXT_POST = 'css_text'
SAVE_TYPE = 'type'

SERVER_DIR = os.path.join(os.environ['HOME'], '.cqsfsaver')
if not os.path.exists(SERVER_DIR): os.mkdir(SERVER_DIR)
PID_FILENAME = os.path.join(SERVER_DIR, 'running.pid')

### Creating logs dir and setup logging
LOGS_DIR = os.path.join(SERVER_DIR, 'logs')
LOG_FILENAME = os.path.join(LOGS_DIR, 'server.log')
if not os.path.exists(LOG_FILENAME):
    os.mkdir(LOGS_DIR)
    open(LOG_FILENAME, "a")
logging.basicConfig(filename=LOG_FILENAME,level=logging.NOTSET, format = '%(levelname)s\t%(asctime)s - %(message)s')
#sys.stdout = open(os.devnull, 'w')
#sys.stderr = open(os.devnull, 'w')

### Creating congigs dir and writing main config
CONFIGS_DIR = os.path.join(SERVER_DIR, 'configs')
CONFIG_FILENAME = os.path.join(CONFIGS_DIR, 'main.json')
if not os.path.exists(CONFIG_FILENAME):
    CONFIG = {'porttrystart': 30778, 'porttryend': 31336}
    os.mkdir(CONFIGS_DIR)
    c = open(CONFIG_FILENAME, 'w')
    c.write(json.dumps(CONFIG))
    c.close()
else:
    c = open(CONFIG_FILENAME, 'r')
    CONFIG = json.load(c)
    c.close()




class Httpd():

    def __init__(self):
        self.PORTS_LIST = iter(range(CONFIG['porttrystart'], CONFIG['porttryend']))

    def running(self):
        if os.path.exists(PID_FILENAME): return True
        else: return False

    def write_pid(self):
        pid_file = open(PID_FILENAME, 'w')
        pid_file.write(str(os.getpid()))
        pid_file.close()

    def get_pid(self):
        pid_file = open(PID_FILENAME, 'r')
        pid = int(pid_file.read())
        return pid

    def start(self):
        global server_port
        self.write_pid()
        try:
            try:
                server_port = self.PORTS_LIST.next()
            except StopIteration:
                logging.critical('All ports in port range is unavailable')
                self.stop()
            server = BaseHTTPServer.HTTPServer(('127.0.0.1', server_port), HttpHandler)
            logging.info('Started server at port '+str(server_port))
            try:
                server.serve_forever()
            except:
                logging.info('Stopped server')
                self.stop()
        except IOError:
            logging.warning('Port '+str(server_port)+' in use, trying '+str(server_port+1))
            try:
                self.start()
            except KeyboardInterrupt:
                logging.info('Stopped server')
                self.stop()

    def stop(self):
        if self.running():
            pid = self.get_pid()
            os.remove(PID_FILENAME)
            import signal
            os.kill(pid, signal.SIGQUIT)
            logging.info('Server stopped')
            sys.exit(0)
        else:
            print 'Server is not running'
            sys.exit(1)


class GUI():

    def __init__(self):
        self.root = Tkinter.Tk()
        self.root.protocol("WM_DELETE_WINDOW", self.leave)
        self.root.wm_attributes("-topmost", 1)
        self.root.focusmodel(model="active")
        self.root.config(takefocus=True)
        self.response = None


    def show_source(self, source, url, action='save'):
        self.root.title("Choose action")
        text_frame = Tkinter.Frame(self.root)
        button_frame = Tkinter.Frame(self.root)
        text = Tkinter.Text(text_frame)
        text.insert(Tkinter.INSERT ,source)
        scrollbar = Tkinter.Scrollbar(text_frame)
        text.configure(state = Tkinter.DISABLED, wrap=Tkinter.WORD, yscrollcommand=scrollbar.set)
        text.pack(side=Tkinter.LEFT, fill=Tkinter.BOTH, expand=1)
        scrollbar.pack(side=Tkinter.LEFT, fill=Tkinter.Y)
        scrollbar.config(command=text.yview)
        label = Tkinter.Label(self.root, bd=3, text='An application is attempting to save CSS for "'+url+'" with contents:', anchor=Tkinter.W, justify=Tkinter.LEFT)
        label.pack(side=Tkinter.TOP, expand=1, fill=Tkinter.BOTH)
        text_frame.pack(expand=1, fill=Tkinter.BOTH)
        b1 = Tkinter.Button(button_frame, text="Allow", command = self.yes).grid(row=0, column=0, padx=10, pady=5)
        b2 = Tkinter.Button(button_frame, text="Disallow", command = self.no).grid(row=0, column=1, padx=10, pady=5)
        button_frame.pack()
        root_width = self.root.winfo_screenwidth()/2
        root_height = self.root.winfo_screenheight()/2+40
        geom_string = "%dx%d+%d+%d" % (root_width, root_height, root_width/2, root_height/2)
        self.root.geometry(geom_string)
        self.root.focus()
        self.root.mainloop()
        return self.response

    def saveas(self, initdir=None):
        self.root.withdraw()
        filename = tkFileDialog.asksaveasfilename(parent=self.root, title='Save CSS as...', filetypes=[('CSS File', '*.css')], defaultextension='.css', initialdir=initdir)
        if len(filename)>0:
            if filename.endswith('.css'):
                self.root.destroy()
                return [True, filename]
            else:
                tkMessageBox.showwarning("Save error", "File must be .css file")
                self.saveas()
        else:
            self.root.destroy()
            return [False, None]

    def yes(self):
        self.root.destroy()
        self.response = True

    def no(self):
        self.root.destroy()
        self.response = False

    def leave(self):
        self.root.destroy()
        self.response = False




class Saver():
    def __init__(self, key, url, text, stype=None, allow=None, name=None):
        if url and text:
            success = False
            self.key = key
            if stype: self.stype = stype[0].decode('utf-8').encode('utf-8')
            else: self.stype=None
            self.url = url[0].decode('utf-8').encode('utf-8')
            self.text = text[0].decode('utf-8').encode('utf-8').replace('\r','')
            self.user_config_filename = os.path.join(CONFIGS_DIR, key+'.json')
            if os.path.exists(self.user_config_filename):
                saveas = [False,'']
                config_file = open(self.user_config_filename, 'r+')
                try:
                    data = config_file.read()
                    config = json.loads(data)
                    if self.url_in_config(self.url, config):
                        for item in config['files']:
                            if item['url']==self.url:
                                if self.stype=='saveas':
                                    if allow is None:
                                        if GUI().show_source(self.text, self.url):
                                            if name is None: saveas = GUI().saveas(SERVER_DIR)
                                            else: saveas = [True, name]
                                            if saveas[0]:
                                                self.save_css(saveas[1], self.text)
                                                item['filepath']=saveas[1]
                                                success = True
                                            else: self.send_false('Disallowed by user')
                                        else: self.send_false('Disallowed by user')
                                    else:
                                        if allow:
                                            if name is None: saveas = GUI().saveas(SERVER_DIR)
                                            else: saveas = [True, name]
                                            if saveas[0]:
                                                self.save_css(saveas[1], self.text)
                                                item['filepath']=saveas[1]
                                                success = True
                                            else: self.send_false('Disallowed by user')
                                        else:
                                            self.send_false('Disallowed by user')
                                else:
                                    self.save_css(item['filepath'], self.text)
                                    saveas[1] = item['filepath']
                                    success = True
                                break


                    else:
                        if allow is None:
                            if GUI().show_source(self.text, self.url):
                                if name is None: saveas = GUI().saveas(SERVER_DIR)
                                else: saveas = [True, name]
                                if saveas[0]:
                                    self.save_css(saveas[1], self.text)
                                    config['files'].append({'url': self.url, 'filepath': saveas[1]})
                                    success = True
                                else: self.send_false('Disallowed by user')
                            else: self.send_false('Disallowed by user')
                        else:
                            if allow:
                                if name is None: saveas = GUI().saveas(SERVER_DIR)
                                else: saveas = [True, name]
                                if saveas[0]:
                                    self.save_css(saveas[1], self.text)
                                    config['files'].append({'url': self.url, 'filepath': saveas[1]})
                                    success = True
                                else: self.send_false('Disallowed by user')
                            else:
                                self.send_false('Disallowed by user')
                except json.JSONDecodeError:
                    config = {'files': []}
                    success = True
            else:
                if allow is None:
                    if GUI().show_source(self.text, self.url):
                        config_file = open(self.user_config_filename, 'w+')
                        config = {'files': []}
                        if name is None: saveas = GUI().saveas(SERVER_DIR)
                        else: saveas = [True, name]
                        if saveas[0]:
                            self.save_css(saveas[1], self.text)
                            config['files'].append({'url': self.url, 'filepath': saveas[1]})
                            success=True
                        else: self.send_false('Disallowed by user')
                    else: self.send_false('Disallowed by user')
                else:
                    if allow:
                        config_file = open(self.user_config_filename, 'w+')
                        config = {'files': []}
                        if name is None: saveas = GUI().saveas(SERVER_DIR)
                        else: saveas = [True, name]
                        if saveas[0]:
                            self.save_css(saveas[1], self.text)
                            config['files'].append({'url': self.url, 'filepath': saveas[1]})
                            success = True
                        else: self.send_false('Disallowed by user')
                    else: self.send_false('Disallowed by user')


            if success:
                self.write_config(config_file, config)
                self.send_true(saveas[1])
        elif url: self.send_false('No "css_text" in POST ')
        elif text: self.send_false('No "css_url" in POST ')
        else: self.send_false('No "css_url" and "css_text" in POST ')

    def write_config(self, config_file, config):
        config_file.seek(0)
        config_file.write(json.dumps(config))
        config_file.close()

    def url_in_config(self, url, config):
        in_list = False
        for item in config['files']:
            if item['url']==url:
                in_list = True
                break
        return in_list

    def save_css(self, css_name, css_text):
        css_file = open(css_name, 'w+')
        css_file.write(css_text)
        css_file.close()

    def send_false(self, message):
        self.success = False
        self.message = message

    def send_true(self, filepath):
        self.success = True
        self.message = filepath


class HttpHandler(BaseHTTPServer.BaseHTTPRequestHandler):

    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write('<html><head><meta http-equiv="content-type" content="text/html; charset=UTF-8" /> </head><body><form action="/?key=23esdhsaod2" method="POST">URL:<input type="text" name="css_url"><br>CSS:<textarea name="css_text"></textarea><br><input type="text" name="type"><br><input type="submit" value="Send"></form></body></html>')


    def do_POST(self):
        path_match = re.match(PATH_PATTERN, self.path)
        success = False
        test = False
        if path_match:
            key = path_match.group(1)
            ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
            if ctype == 'application/x-www-form-urlencoded':
                length = int(self.headers.getheader('content-length'))
                post = cgi.parse_qs(self.rfile.read(length), keep_blank_values=0)
            url = post.get(CSS_URL_POST)
            text = post.get(CSS_TEXT_POST)
            stype = post.get(SAVE_TYPE)
            saver = Saver(key, url, text, stype)
            if saver.success: self.send_true(saver.message)
            else: self.send_false(saver.message)

    def send_false(self, message):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(json.dumps({'success': False, 'filepath': None, 'message': message}))

    def send_true(self, filepath):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(json.dumps({'success': True, 'filepath': filepath, 'message': ""}))

class Test():
    def __init__(self, data):
        key = data.get('key')
        if key is None:
            print "Key is required"
            sys.exit(1)
        url = data.get('url')
        text = data.get('text')
        allow = data.get('allow')
        if allow: allow=int(allow[0])
        name = data.get('name')
        if name: name=name[0]
        saver = Saver(key[0], url, text, allow, name)
        if saver.success: self.send_true(saver.message)
        else: self.send_false(saver.message)

    def send_false(self, message):
        print json.dumps({'success': False, 'filepath': None, 'message': message})

    def send_true(self, filepath):
        print json.dumps({'success': True, 'filepath': filepath, 'message': ""})

def main(args=None):
    if len(sys.argv) == 2:
        if sys.argv[1]=='start':
            s = Httpd()
            if s.running(): print "Server already running"
            else: s.start()
        if sys.argv[1]=='stop':
            s = Httpd()
            if s.running(): s.stop()
            else: print "Server is not running"
    elif len(sys.argv)==3:
        if sys.argv[1]=='test':
            Test(cgi.parse_qs(sys.argv[2]))
    else:
        print 'Usage: cqsfsaver start|stop|test "query"'


if __name__ == '__main__':
    main()

