import SocketServer
import socket
import os
#from os.sys import getwindowsversion
import urllib
import base64
import sys # for sys.argv
#import time

#try:
#    import thread as ThreadEngine
#except ImportError:
#    import dummy_thread as ThreadEngine
cnscr = False
try:
	from PIL import ImageGrab, Image
	cnscr = True
except:
	cnscr = False
# syscon.pytrack

class pyscreen(object):
	
	
	def __init__(self, target_name, image_send_port = 56000):
		#self.__interval = interval
		self.__dataport = image_send_port
		self.__targetpc = socket.gethostbyname(target_name)
	def shot(self):
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		sock.connect((self.__targetpc, self.__dataport))
		#while ClientManager.take_screen == True:
		#time.sleep(self.__interval)
		img = ImageGrab.grab()
		adp = os.environ.get("APPDATA")
		pth = adp + r"\scr.jpeg"
		img.save(pth)
		fobj = open(pth, "r+b")
		dta = fobj.read()
		fobj.close()
		bdt = base64.b64encode(dta)
		sock.send(bdt.rstrip("\n") + "\n")
		sock.close()

	

# syscon.client3

class sysclient(object):
	def __init__(self, cont_host_name):
		# init wincon
		try:
                        self.os = self.__checkos()
                except: # no-windows
                        self.os = "?"
		self.__controller = cont_host_name

	def execute(self, data):
		#print data
		data = str(data)
		cmd = int(data[0])
		if cmd == 0:
			# shutdown
			self.shutdown()
			return (True, "Remote machine started SHUTDOWN process.")
		elif cmd == 1:
			# executefile
			os.system(data[2:])
			return (True, "File executed: " + data[2:])
		elif cmd == 2:
			# execpy
			exec data[2:]
			return (True, "Python executed: " + data[2:])
		elif cmd == 3:
			# logoff
			self.logoff()
			return (True, "Remote user logged off.")
		elif cmd == 4:
			# download
			arr = data.split("@")
			local = arr[1]
			web = arr[2]
			self.download(local, web)
			return (True, "File " + web + " downloaded to " + local + ".")
		elif cmd == 5:
			# stopcontrol
			#print "stop!"
			return (False, "Remote control connection closed.")
		elif cmd == 6:
			# screenshot
			# {start taking screenshots}
			#print data
			arr = data.split("@")
			port = int(arr[1])
			#ClientManager.take_screen = True
			#ClientManager.ts_thread = ThreadEngine.start_new_thread(pyscreen_activate, (30, self.__controller, port))
			res = screenshot(self.__controller, port)
			if res == True:
                                return (True, "made screenshot - hope you've already started the pyscreen listener...")
                        else:
                                return (True, "Error - PIL not installed. You might find it useful to install it with 'download' and 'executefile' commands")
		elif cmd == 7:
                        # returnvalue
                        arr = data.split("@")
                        val = arr[1]
                        x = ""
                        try:
                                exec "x = " + val
                        except:
                                x = ""
                        reval = str(x)
                        return (True, reval)
                        
		#elif cmd == 7:
		#	# ??
		#	# start taking screenshots
		#	ClientManager.ts_thread.stop_all()
		#	return (True, "Stopped PYSCREENING - you can close the pyscreen control now.")
		return (True, "")

	def download(self, toFile, fromUrl):
		#print toFile, fromUrl
		"""Copy the contents of a file from a given URL
		to a local file.
		"""
		webFile = urllib.urlopen(fromUrl)
		localFile = open(toFile, "w+")
		localFile.write(webFile.read())
		webFile.close()
		localFile.close()

	# WINCON ###################################
	def __checkos(self):
		n = os.sys.getwindowsversion()
		z = str(n[0]) + '.' + str(n[1])
		if z == '6.0':
			return 'WinVista'
		elif z == '6.1':
			return 'Win7'
		elif z == '5.0':
			return 'Win2000'
		elif z == '5.1':
			return 'WinXP'
		elif z == '5.2':
			return 'WinXP' # 64bit!
		elif n[0] == 4:
			return 'WinNT' # 4.0
		elif n[0] == 3:
			return 'WinNT' # 3.x
		else:
			return '?'

	def shutdown(self):
		if self.os in ['WinVista','Win7']:
			os.system('shutdown /p')
		elif self.os == 'WinXP':
			os.system('shutdown /s /t 0')
		elif self.os in ['Win2000', 'WinNT']:
			os.system('shutdown /l /t:00 /y /c')

	def abortShutdown(self):
		if self.os not in ['Win2000', 'WinNT', '?']:
			os.system('shutdown /a')
		elif self.os in ['Win2000', 'WinNT']:
			os.system('shutdown /l /a /y')

	def logoff(self):
		if self.os not in ['Win2000', 'WinNT', '?']:
			os.system('shutdown /l /f')
		elif self.os in ['Win2000', 'WinNT']:
			os.system('logoff')

	def restart(self, restartApplications = False):
		if self.os <> '?':
			if restartApplications == True and __checkos(True) not in ['WinXP', 'Win2000', 'WinNT']:
				os.system('shutdown /g')
			elif restartApplications == False and __checkos(True) not in ['Win2000', 'WinNT']:
				os.system('shutdown /r /f')
			else: # Win2000, WinNT
				os.system('shutdown /l /r /y /c')

	def hibernate(self):
		if self.os not in ['Win2000', 'WinNT', '?']:
			os.system('shutdown /h')
		elif self.os in ['Win2000', 'WinNT']: # Windows-DLL
			os.system('rundll32.exe powrprof.dll,SetSuspendState')

	# NT ????
	def lock(self):
		# works with Windows-DLLs
		if self.os <> '?':
			os.system('rundll32.exe user32.dll,LockWorkStation')


	def killProcess(self, ProcessName):
		if self.os <> '?':
			if __checkos(True) not in ['WinNT', 'Win2000']:
				os.system('taskkill /F /IM' + ProcessName)
			else:
				os.system('kill ' + ProcessName)
	# WINCON END ###############################

class syscon(SocketServer.StreamRequestHandler):
	"""
	The RequestHandler class for our server [client in syscon].

	It is instantiated once per connection to the server, and must
	override the handle() method to implement communication to the
	client.
	"""        
        
	def handle(self):
		# self.rfile is a file-like object created by the handler;
		# we can now use e.g. readline() instead of raw recv() calls
		self.data = self.rfile.readline().strip()
		#print "%s wrote:" % self.client_address[0]
		#print self.data
		dta = ""
		for i in self.data:
			#print i
			dta += i
		self.data = dta
		#print self.data
		# Likewise, self.wfile is a file-like object used to write back
		# to the client
		client = sysclient(self.client_address[0])
		result = client.execute(self.data)
		if result[0] == False:
                        #print "stopping"
			self.request.send(result[1])
			ClientManager.interrupted = True
			#print ClientManager.interrupted
		else:
			self.request.send(result[1])

class SysconClientServer(object):
        def __init__(self, HOST, PORT):
                self.host = HOST
                self.port = PORT
                self.server = SocketServer.TCPServer((HOST, PORT), syscon)
        def StartServer(self):
                """Starts the server like TCPServer.serve_forever,
                but shuts down on interrupt."""
                while True:
                        if ClientManager.interrupted == True:
                                break
                        self.server.handle_request()
                #print "OK, STOP!!!!!"
                #self.server.shutdown()
                #print "stopped"
                ClientManager.server_stopped = True

class ClientManager(object):
	global interrupted # if the SCS shall be interrupted: set true
	global server_stopped # has been interrupted
	global canScreen # can take screenshots - PIL imported correctly
	#global take_screen # taking screenshots...
	#global ts_thread # screenshot thread

def screenshot(host, port):
        #print interval, host, port
        if ClientManager.canScreen == True:
                screen = pyscreen(host, port)
                screen.shot()
                return True
        else:
                return False

if __name__ == "__main__":
	HOST, PORT = socket.gethostname(), 51000
	if len(sys.argv) > 1:
		PORT = int(sys.argv[1])
	#print HOST, PORT
	# Create the server, binding to HOST on port PORT
	server = SysconClientServer(HOST, PORT)
        
	ClientManager.interrupted = False
	ClientManager.server_stopped = False
        #ClientManager.take_screen = False
        ClientManager.canScreen = cnscr
        
	# Activate the server; this will keep running until you
	# interrupt with ClientManager.interrupted = True
	server.StartServer()
        
	while not ClientManager.server_stopped:
		pass
	#print "stopped. at last."
	del server
	exit()
