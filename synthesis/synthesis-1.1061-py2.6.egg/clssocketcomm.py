# bidirectional communication class to interact w/ GUI interfaces (mainly win32) but works on *nix
import sys
from time import sleep

class serviceController:
	def __init__(self, bServer = True):
		import socket
		
		self.host = 'localhost'
		
		self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		
		# let the class know it's the server or the client
		self.bServer = bServer
		if bServer:
			self.serverPort = 8081
			self.clientPort = 8082
			
		#	self.s.bind(("", self.serverPort))
			
		else:
			self.serverPort = 8082
			self.clientPort = 8081
			
		self.s.bind(("", self.serverPort))
		
		# now listen for messages
		#self.listen()
	
	def send(self, msg):
		# if we are server send to client, otherwise we are client, send to server
		#if self.bServer:
		#	port = self.clientPort
		#else:
		#	port = self.serverPort
			
		self.s.sendto(msg, (self.host, self.clientPort))
		
	def getStatus(self, msg):
		self.send(msg)
		
		# set the timeout to 5 (this is in case the server is not running we need to outtie.)
		self.s.settimeout(5)
		#while 1:
			# receiving data
		# sleep for 5 seconds
		#sleep(3)
		try:
			data, addr = self.s.recvfrom(1024)
		except:
			return "Synthesis is not Running..."
		
		if data == 'synthesis:running':
			return "Synthesis is Running..."
		
	def listen(self):
		if self.bServer:
			port = self.serverPort
		else:
			port = self.clientPort
			
		print "waiting on port", port
		
		while 1:
			# receiving data
			data, addr = self.s.recvfrom(1024)
			print "Received: ", data, "from:", addr
			
			if data == 'synthesis:status':
				self.send("synthesis:running")	
			if data == 'synthesis:stop':
				print "stopping hard"
				sys.exit(0)