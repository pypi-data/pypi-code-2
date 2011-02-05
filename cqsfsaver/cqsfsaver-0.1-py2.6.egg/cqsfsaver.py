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

SERVER_DIR = os.path.join(os.environ['HOME'], '.vqsfsaver')
if not os.path.exists(SERVER_DIR): os.mkdir(SERVER_DIR)
PID_FILENAME = os.path.join(SERVER_DIR, 'running.pid')

### Creating logs dir and setup logging
LOGS_DIR = os.path.join(SERVER_DIR, 'logs')
LOG_FILENAME = os.path.join(LOGS_DIR, 'server.log')
if not os.path.exists(LOG_FILENAME):
    os.mkdir(LOGS_DIR)
    open(LOG_FILENAME, "a")
logging.basicConfig(filename=LOG_FILENAME,level=logging.NOTSET, format = '%(levelname)s\t%(asctime)s - %(message)s')
sys.stdout = open(os.devnull, 'w')
sys.stderr = open(os.devnull, 'w')

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


class HttpHandler(BaseHTTPServer.BaseHTTPRequestHandler):

    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write('<html><head><meta http-equiv="content-type" content="text/html; charset=UTF-8" /> </head><body><form action="/?key=23esdhsaod2" method="POST">URL:<input type="text" name="css_url"><br>CSS:<input type="text" name="css_text"><br><input type="submit" value="Send"></form></body></html>')

    def do_POST(self):
        path_match = re.match(PATH_PATTERN, self.path)
        if path_match:
            key = path_match.group(1)
            ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
            if ctype == 'application/x-www-form-urlencoded':
                length = int(self.headers.getheader('content-length'))
                post = cgi.parse_qs(self.rfile.read(length), keep_blank_values=0)
            url = post.get(CSS_URL_POST)
            text = post.get(CSS_TEXT_POST)
            if url and text:
                logging.info('ALL DATA')
                url = url[0].decode('utf-8').encode('utf-8')
                text = text[0].decode('utf-8').encode('utf-8')
                logging.info('decode data')
                if GUI().show_source(text, url):
                    logging.info('show cour')
                    filename = os.path.join(CONFIGS_DIR, key+'.json')
                    saveas = [False,'']
                    if os.path.exists(filename):
                        config_file = open(filename, 'r+')
                        try:
                            data = config_file.read()#.replace('\\', '\\\\') ##windows fix
                            config = json.loads(data)
                            ###dirty
                            in_list = False
                            for item in config['files']:
                                if item['url']==url:
                                    in_list = True
                                    break
                            if in_list:
                                for item in config['files']:
                                    if item['url']==url:
                                        css_file = open(item['filepath'], 'w+')
                                        css_file.write(text)
                                        css_file.close()
                                        saveas[1] = item['filepath']
                                        break
                            else:
                                saveas = GUI().saveas(SERVER_DIR)
                                if saveas[0]:
                                    css_file = open(saveas[1], 'w+')
                                    css_file.write(text)
                                    css_file.close()
                                    config['files'].append({'url': url, 'filepath': saveas[1]})
                                else:
                                    self.send_response(200)
                                    self.send_header("Content-type", "text/html")
                                    self.end_headers()
                                    self.wfile.write(json.dumps({'success': False, 'filepath': None, 'message': "Disallowed by user"}))
                                    return True
                            ###EOD
                        except json.JSONDecodeError:
                            config = {'files': []}
                    else:
                        config_file = open(filename, 'w+')
                        config = {'files': []}
                        saveas = GUI().saveas(SERVER_DIR)
                        if saveas[0]:
                            css_file = open(saveas[1], 'w+')
                            css_file.write(text)
                            css_file.close()
                            config['files'].append({'url': url, 'filepath': saveas[1]})
                        else:
                            self.send_response(200)
                            self.send_header("Content-type", "text/html")
                            self.end_headers()
                            self.wfile.write(json.dumps({'success': False, 'filepath': None, 'message': "Disallowed by user"}))
                            return
                    config_file.seek(0)
                    config_file.write(json.dumps(config))
                    config_file.close()
                    self.send_response(200)
                    self.send_header("Content-type", "text/html")
                    self.end_headers()
                    self.wfile.write(json.dumps({'success': True, 'filepath': saveas[1], 'message': ""}))
                    config_file.close()
                else:
                    self.send_response(200)
                    self.send_header("Content-type", "text/html")
                    self.end_headers()
                    self.wfile.write(json.dumps({'success': False, 'filepath': None, 'message': "Disallowed by user"}))
            elif url:
                self.no('CSS')

            elif text:
                self.no('URL')
            else:
                self.no('DATA')


    def no(self, t):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(json.dumps({'success': False, 'filepath': None, 'message': "No "+t+" in POST"}))


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
    else:
        print "Usage: cqsfsaver start|stop"


if __name__ == '__main__':
    main()

