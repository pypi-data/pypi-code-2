import socket
import sys

class Connection(object):
    def __init__(self, computername, port = 51000):
        self.__computer = computername
        self.__ip = socket.gethostbyname(computername)
        self.__port = port
        print "Connection object to " + computername + " (IP " + socket.gethostbyname(computername) + ") on port " + str(port)
    def send(self, command, path = None, url = None):
        print "Sending " + command + " " + str(path) + " " + str(url) + " to " + self.__computer
        cmd = str(self.getShortCommand(command))
        abort = False
        if int(cmd[0]) in [1,2,6,7]:
            if path is None:
                abort = True
            cmd += "@" + str(path)
        elif int(cmd[0]) == 4:
            if path is None or url is None:
                abort = True
            cmd += "@" + str(path) + "@" + str(url)
        if int(cmd[0]) > -1 and abort != True:
            print "Data to send: " + cmd
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((self.__ip, self.__port))
            sock.send(cmd + "\n")
            if int(cmd[0]) <> 5:
                received = sock.recv(8192)
                print "Client answer: " + received
            sock.close()
    def getShortCommand(self, longcmd):
        cmdlist = ["shutdown","executefile","execpy","logoff","download","stopcontrol","screenshot", "returnvalue"] #, "stoppyscreen"]
        return cmdlist.index(longcmd)
    def close(self):
        self.send("stopcontrol")
    def screenshot(self):
        self.send("screenshot", "56000")

