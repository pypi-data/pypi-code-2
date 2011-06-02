# syscon:pyscreen:listener
import SocketServer
import socket
import sys
from os import environ
import base64

class pyscreenlistener(SocketServer.StreamRequestHandler):
	def handle(self):
                print "waiting for screenshot..."
                self.data = self.rfile.readline().strip()
		print "data received..."
		dta = base64.b64decode(self.data)
		print "data decoded..."
		pth = pyscreenmanager.path + "\\client_screen" + str(pyscreenmanager.imgnum) + ".jpg"
		print "write data to " + pth
		fobj = open(pth, "w+b")
		fobj.write(dta)
		fobj.close()
		print "data written..."
		pyscreenmanager.imgnum += 1

class pyscreenmanager:
	global imgnum
	global path



if __name__ == "__main__":
	HOST, PORT = socket.gethostname(), 56000
	pth = environ.get("APPDATA")
	if len(sys.argv) > 1:
		PORT = int(sys.argv[1])
	else:
                # no args given:
                PORT = int(raw_input("Enter port number: "))
                pth = raw_input("Enter path [raw string]: ")
	if len(sys.argv) > 2:
		pth = sys.argv[2]
	
	pyscreenmanager.imgnum = 0
	pyscreenmanager.path = pth
	
	server = SocketServer.TCPServer((HOST, PORT), pyscreenlistener)
        
        print HOST, PORT, pyscreenmanager.imgnum, pyscreenmanager.path
	
	server.serve_forever()
