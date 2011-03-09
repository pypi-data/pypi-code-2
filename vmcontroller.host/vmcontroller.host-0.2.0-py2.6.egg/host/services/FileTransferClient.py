try:
    import os
    import logging

    from twisted.internet import reactor, protocol, stdio, defer
    from twisted.protocols import basic
    from twisted.internet.protocol import ClientFactory

    from vmcontroller.common.FileTransfer import *
except ImportError, e:
    print "Import error in %s : %s" % (__name__, e)
    import sys
    sys.exit()

#FIXME: The Ugly Code
class FileTransferClient(basic.LineReceiver):
    delimiter = '\n'
    
    def __init__(self, server_ip, server_port, files_path):
        self.server_ip = server_ip
        self.server_port = server_port
        self.files_path = files_path
        self._transfers = {}
        self.logger = logging.getLogger('%s.%s' % (self.__class__.__module__, self.__class__.__name__))

        self.factory = FileTransferClientFactory(self.files_path)
        self.connection = reactor.connectTCP(self.server_ip, self.server_port, self.factory)
        self.factory.deferred.addCallback(self._display_response)

    def listFile(self):
        self.connection.transport.write('list\n')
        self.factory.deferred.addCallback(self._display_response)

    def getFile(self, fileName, dres):
        self.connection.transport.write('get %s\n' % fileName)
        self.factory.deferred.addCallback(self._display_response)
        dres.callback('Request sent')

    def putFile(self, filePath, fileName, dres):
        if not os.path.isfile(filePath):
            self.logger.debug('This file does not exist: ', filePath)
            dres.callback('ERROR Transferring file: ', filePath)
            return

        fileSize = os.path.getsize(filePath) / 1024
        self.connection.transport.write('PUT %s %s\n' % (fileName, get_file_md5_hash(filePath)))
        self.setRawMode()
        self.logger.info('Uploading file: %s->%s (%d KB)' % (filePath, fileName, fileSize))

        for bytes in read_bytes_from_file(filePath):
            self.connection.transport.write(bytes)
        
        self.connection.transport.write('\r\n')
        self.factory.deferred.addCallback(self._display_response)
        dres.callback('Transfer OK')

    def _sendCommand(self, line):
        """ Sends a command to the server. """
        print "Command:", line

        data = clean_and_split_input(line) 
        if len(data) == 0 or data == '':
            return 

        command = data[0].lower()
        if not command in COMMANDS:
            self.self.logger.debug('Invalid command')
            return
        
        if command == 'list':
            return self.listFile()
        elif command == 'get':
            try:
                fileName = data[1]
            except IndexError:
                self.logger.debug('Missing filename')
                return
            
            self.getFile(fileName)
        elif command == 'put':
            try:
                filePath = data[1]
                fileName = data[2]
            except IndexError:
                self.logger.debug('Missing local file path or remote file name')
                return

            self.getFile(filePath, fileName)
        else:
            self.connection.transport.write('%s %s\n' % (command, data[1]))

        self.factory.deferred.addCallback(self._display_response)

    def _display_response(self, lines = None):
        """ Displays a server response. """
        self.logger.debug("Server says:")
        if lines:
            for line in lines:
                print '%s' % (line)

        self.factory.deferred = defer.Deferred()

class FileTransferProtocol(basic.LineReceiver):
    delimiter = '\n'
    def __init__(self):
        self.logger = logging.getLogger('%s.%s' % (self.__class__.__module__, self.__class__.__name__))  

    def connectionMade(self):
        self.buffer = []
        self.file_handler = None
        self.file_data = ()

        self.logger.debug('Connected to the server')
        
    def connectionLost(self, reason):
        self.file_handler = None
        self.file_data = ()
        
        self.logger.debug('Connection to the server has been lost')
        #reactor.stop()
    
    def lineReceived(self, line):
        if line == 'ENDMSG':
            self.factory.deferred.callback(self.buffer)
            self.buffer = []
        elif line.startswith('HASH'):
            # Received a file name and hash, server is sending us a file
            data = clean_and_split_input(line)

            filename = data[1]
            file_hash = data[2]
            
            self.file_data = (filename, file_hash)
            self.setRawMode()
        else:
            self.buffer.append(line)
        
    def rawDataReceived(self, data):
        filename = self.file_data[0]
        file_path = os.path.join(self.factory.files_path, filename)
        
        self.logger.debug('Receiving file chunk (%d KB)' % (len(data)))
        
        if not self.file_handler:
            self.file_handler = open(file_path, 'wb')
            
        if data.endswith('\r\n'):
            # Last chunk
            data = data[:-2]
            self.file_handler.write(data)
            self.setLineMode()
            
            self.file_handler.close()
            self.file_handler = None
            
            if validate_file_md5_hash(file_path, self.file_data[1]):
                self.logger.debug('File %s has been successfully transfered and saved' % (filename))
            else:
                os.unlink(file_path)
                self.logger.debug('File %s has been successfully transfered, but deleted due to invalid MD5 hash' % (filename))
        else:
            self.file_handler.write(data)

class FileTransferClientFactory(protocol.ClientFactory):
    protocol = FileTransferProtocol
    
    def __init__(self, files_path):
        self.files_path = files_path
        self.deferred = defer.Deferred()

if __name__ == '__main__':
    # FIXME Get these stuff automatically
    vmIp = "192.168.56.101"
    fileDirPath = '/tmp'
    fileServerPort = 1234

    fileUtil = FileTransferClient(vmIp, fileServerPort, fileDirPath)

    pathToLocalFileName = '/bin/uname'
    pathToRemoteFileName = 'uname-bin'
    print "Transferring file: %s to VM(%s)" % (pathToLocalFileName, vmIp)

    reactor.callLater(5, fileUtil.putFile, pathToLocalFileName, pathToRemoteFileName)
#    fileUtil.sendFile(pathToLocalFileName, pathToRemoteFileName)
#    stdio.StandardIO(CommandLineProtocol(IP, PORT, LOCALPATH))
    reactor.run()
