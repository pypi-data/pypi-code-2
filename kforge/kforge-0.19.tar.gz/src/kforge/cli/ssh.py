import os
import sys
import shlex
from subprocess import call
from subprocess import Popen, PIPE
import re
import kforge.regexps
from threading import Thread

# Todo: Test for cloning after adding changesets (Mercurial, Git, and Subversion).
# Todo: Test for pulling adding revisions from another clone (Mercurial, Git, and Subversion).

class SshCommandRunner(object):

    def __init__(self):

        try:
            lenArgv = len(sys.argv)
            assert lenArgv == 3, "SSH command needs 3 'argv' arguments (there are %s)." % lenArgv

            configPath = sys.argv[1]
            os.environ['KFORGE_SETTINGS'] = configPath
            try:
                from kforge.soleInstance import application
                import kforge.regexps
            except Exception, inst:
                raise Exception, "KForge error: Unable to import kforge"

            if not 'ssh' in application.registry.plugins:
                raise Exception, "KForge error: SSH functionality is not enabled"

            sshKeyId = sys.argv[2]
            try:
                assert sshKeyId
            except:
                msg = "SSH handler has bad configuration (key ID not given)."
                application.logger.warning(msg)
                raise Exception, "Internal server error (1)"

            sshKeys = application.registry.sshKeys.findDomainObjects(id=sshKeyId)
            if not sshKeys:
                msg = "SSH handler has bad configuration (key ID '%s' not found in register)." % sshKeyId
                application.logger.warning(msg)
                raise Exception, "Internal server error (2)"

            if len(sshKeys) > 1:
                msg = "SSH handler discovered model error (more than one ssh key for ID '%s')." % sshKeyId
                application.logger.warning(msg)
                raise Exception, "Internal server error (3)"

            sshKey = sshKeys[0]

            try:
                if not sshKey.isConsummated:
                    sshKey.isConsummated = True
                    sshKey.save()
            except Exception, inst:
                msg = "SSH handler could not update 'isConsummated' attribute of ssh key '%s': %s" % (sshKeyId, inst)
                application.logger.warning(msg)
                raise Exception, "Internal server error (4)"

            if not sshKey.person:
                msg = "SSH handler discovered model error (missing person for ssh key '%s')." % sshKeyId
                application.logger.warning(msg)
                raise Exception, "Internal server error (5)"

            if not sshKey.person.name:
                msg = "SSH handler discovered model error (missing person name for person ID '%s')." % sshKey.person.id
                application.logger.warning(msg)
                raise Exception, "Internal server error (6)"

            person = sshKey.person
            personName = person.name

            sshRequest = os.environ['SSH_ORIGINAL_COMMAND']

            if not sshRequest:
                msg = "SSH command not found in request from person '%s'." % personName
                application.logger.warning(msg)
                raise Exception, "Bad request"
                
            application.logger.info("SSH request from person '%s' (key '%s'): %s" % (personName, sshKeyId, sshRequest))

            try:
                if sshRequest.startswith('git'):
                    commandClass = GitCommand
                elif sshRequest.startswith('hg'):
                    commandClass = MercurialCommand
                elif sshRequest.startswith('svn'):
                    commandClass = SubversionCommand
                else:
                    raise Exception, "SSH command is not supported: %s" % sshRequest

                command = commandClass(
                    sshRequest=sshRequest,
                    person=person,
                    application=application,
                )
                command.run()

            except ServiceNotFound, inst:
                msg = "Repository not found for SSH request from '%s': %s: %s." % (personName, sshRequest, inst)
                application.logger.warning(msg)
                raise Exception, "kforge: Service not found for requested path: %s" % command.urlPath
            except AccessDenied, inst:
                application.logger.info("Access denied for SSH request from '%s': %s: %s." % (personName, sshRequest, inst))
                raise Exception, "kforge: Access denied"
            except Exception, inst:
                application.logger.warning("Error processing SSH request from '%s': %s: %s." % (personName, sshRequest, inst))
                raise Exception, "kforge: Internal server error (7)"

        except Exception, inst:
            print >>sys.stderr, inst
            sys.exit(-1)


class AccessDenied(Exception): pass


class BaseCommand(object):

    def __init__(self, sshRequest, application=None, person=None):
        self.sshRequest = sshRequest
        self.application = application
        self.person = person

    def run(self):
        self.splitSshRequest()
        self.validateRequest()
        self.initActionName()
        self.initUrlPath()
        self.initService()
        self.assertAccessAuthorized()
        self.rewriteRequestArgs()
        self.initShellCmd()
        self.call()

    def splitSshRequest(self):
        sshRequestParts = shlex.split(str(self.sshRequest))
        self.sshRequestCmd = sshRequestParts[0]
        self.sshRequestArgs = sshRequestParts[1:]

    def validateRequest(self):
        raise Exception, "Method not implemented."

    def initActionName(self):
        raise Exception, "Method not implemented."

    def initUrlPath(self):
        raise Exception, "Method not implemented."

    def initService(self):
        urlPathParts = self.urlPath.strip("'").strip('/').split('/')
        try:
            assert len(urlPathParts) == 2, "Service path needs two parts: %s" % self.urlPath

            projectName = urlPathParts[0]
            pattern = re.compile('^%s$' % kforge.regexps.projectName)
            assert pattern.match(projectName), "Project name '%s' is not valid" % projectName

            serviceName = urlPathParts[1]
            pattern = re.compile('^%s$' % kforge.regexps.serviceName)
            assert pattern.match(serviceName), "Service name '%s' is not valid" % serviceName

            project = self.application.registry.projects[projectName]
            service = project.services[serviceName]
        except Exception, inst:
            raise ServiceNotFound, inst
        self.service = service
        self.application.logger.info("SSH request for access to service: %s" % self.service)
        self.servicePath = self.application.fileSystem.getServicePath(self.service)

    def rewriteRequestArgs(self):
        raise Exception, "Method not implemented."

    def assertAccessAuthorized(self):
        isAuthorised = self.isAccessAuthorised(
            actionName=self.actionName,
        )
        if not isAuthorised:
            raise AccessDenied, "SSH command is not authorised"

    def isAccessAuthorised(self, actionName):
        return self.application.accessController.isAccessAuthorised(
            person=self.person,
            protectedObject=self.service.plugin,
            actionName=actionName,
            project=self.service.project,
        )

    def initShellCmd(self):
        self.shellCmd = self.sshRequestCmd + " " + " ".join(self.sshRequestArgs)

    def call(self):
        try:
            self.application.logger.info("Executing command via SSH: %s" % self.shellCmd)
            returnCode = call(self.shellCmd, shell=True)
            if returnCode < 0:
                raise Exception, "SSH command was terminated by signal: %s" % (returnCode)
            elif returnCode > 0:
                raise Exception, "SSH command exited with non-zero error code: %s" % (returnCode)
            self.application.logger.debug("SSH command executed OK")
        except OSError, inst:
            raise Exception, "SSH command execution failed: %s" % inst


class GitCommand(BaseCommand):

    def validateRequest(self):
        if self.sshRequestCmd == 'git':
            if len(self.sshRequestArgs) != 2:
                msg = "Git command '%s' needs two arguments: %s" % (
                    self.sshRequestCmd, self.sshRequestArgs)
                raise Exception, msg
            if self.sshRequestArgs[0] not in ['upload-pack', 'receive-pack']:
                msg = "Git command argument '%s' is not supported." % self.sshRequestArgs[0]
                raise Exception, msg
        elif self.sshRequestCmd in ['git-upload-pack', 'git-receive-pack']:
            if len(self.sshRequestArgs) != 1:
                msg = "Git command '%s' needs one argument: %s" % (
                    self.sshRequestCmd, self.sshRequestArgs)
                raise Exception, msg
        else:
            msg = "Git command '%s' not supported." % self.sshRequestCmd
            raise Exception, msg

    def initActionName(self):
        self.actionName = 'Update'
        if self.sshRequestCmd == 'git':
            if self.sshRequestArgs[0] == 'upload-pack':
                self.actionName = 'Read'
        else:
            if self.sshRequestCmd == 'git-upload-pack':
                self.actionName = 'Read'

    def initUrlPath(self):
        if self.sshRequestCmd == 'git':
            self.urlPath = self.sshRequestArgs[1]
        else:
            self.urlPath = self.sshRequestArgs[0]

    def rewriteRequestArgs(self):
        if self.sshRequestCmd == 'git':
            self.sshRequestArgs[1] = self.servicePath
        else:
            self.sshRequestArgs[0] = self.servicePath


class MercurialCommand(BaseCommand):

    def validateRequest(self):
        if self.sshRequestCmd != 'hg':
            msg = "Mercurial command '%s' not supported." % self.sshRequestCmd
            raise Exception, msg
        if len(self.sshRequestArgs) != 4:
            msg = "Mercurial command args look wrong (len): %s" % self.sshRequestArgs
            raise Exception, msg
        if self.sshRequestArgs[0] != '-R':
            msg = "Mercurial command args look wrong (0): %s" % self.sshRequestArgs
            raise Exception, msg
        if self.sshRequestArgs[2] != 'serve':
            msg = "Mercurial command args look wrong (2): %s" % self.sshRequestArgs
            raise Exception, msg
        if self.sshRequestArgs[3] != '--stdio':
            msg = "Mercurial command args look wrong (3): %s" % self.sshRequestArgs
            raise Exception, msg

    def initActionName(self):
        self.actionName = 'Read'

    def initUrlPath(self):
        self.urlPath = self.sshRequestArgs[1]

    def rewriteRequestArgs(self):
        self.sshRequestArgs[1] = os.path.join(self.servicePath, 'repo')

    def call(self):
        self.application.logger.info("Executing command via SSH: %s" % self.shellCmd)
        canUpdate = self.isAccessAuthorised(actionName='Update')
        try:
            self.server = Popen(self.shellCmd, stdin=PIPE, stdout=PIPE, shell=True)
            # Start direct client-server communication.
            if canUpdate:
                inboundReader = ReadSingleChar
                validInboundPatterns = []
            else:
                inboundReader = ReadHgMessage
                validInboundPatterns = [
                    re.compile('^hello\n$'),
                    re.compile('^between'),
                    re.compile('^heads'),
                    re.compile('^changegroup'),
                    re.compile('^branches'),
                ]
            outboundReader = ReadSingleChar
            validOutboundPatterns = []
            stdinThread = PipeThread(name='Pipe inbound', stdin=sys.stdin, stdout=self.server.stdin, reader=inboundReader, logger=self.application.logger, validPatterns=validInboundPatterns)
            stdoutThread = PipeThread(name='Pipe outbound', stdin=self.server.stdout, stdout=sys.stdout, reader=outboundReader, logger=self.application.logger, validPatterns=validOutboundPatterns)
            stdinThread.start()
            stdoutThread.start()
            #self.application.logger.info("Waiting for server to finish...")
            returnCode = self.server.wait()
            #self.application.logger.info("Server  finished...")
            #self.application.logger.info("Joining on threads....")
            stdoutThread.join()
            #self.application.logger.info("Joined on Stdout thread.")
            stdinThread.join()
            #self.application.logger.info("Joined on Stdin thread.")
            if returnCode < 0:
                raise Exception, "SSH command was terminated by signal: %s" % (returnCode)
            elif returnCode > 0:
                raise Exception, "SSH command exited with non-zero error code: %s" % (returnCode)
            elif stdinThread.error:
                if isinstance(stdinThread.error, AccessDenied):
                    raise AccessDenied, "Access denied by inbound thread: %s" % (stdinThread.error)

                else:
                    raise Exception, "SSH inbound thread exited with error: %s" % (stdinThread.error)
            elif stdoutThread.error:
                raise Exception, "SSH outbound thread exited with error: %s" % (stdoutThread.error)
            else:
                self.application.logger.info("SSH command executed OK")
        except OSError, inst:
            raise Exception, "SSH command execution failed: %s" % inst


class SubversionCommand(BaseCommand):

    def validateRequest(self):
        if self.sshRequestCmd != 'svnserve':
            msg = "Subversion command '%s' not supported." % self.sshRequestCmd
            raise Exception, msg
        if len(self.sshRequestArgs) != 1:
            msg = "Subversion request args look wrong (len): %s" % self.sshRequestArgs
            raise Exception, msg
        if self.sshRequestArgs[0] != '-t':
            msg = "Subversion request args look wrong (0): %s" % self.sshRequestArgs
            raise Exception, msg

    def initActionName(self):
        self.actionName = 'Read'

    def initUrlPath(self):
        # Tease the requested service path from client.
        sys.stdin = os.fdopen(sys.stdin.fileno(), 'r', 0)
        sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)
        # Send server greeting to the client.
        self.server = Popen('svnserve -t', stdin=PIPE, stdout=PIPE, shell=True)
        try:
            #self.application.logger.info("Reading svnserve greeting...")
            greeting = self.readServerMessage()
            #greeting = '( success ( 2 2 ( ) ( edit-pipeline svndiff1 absent-entries commit-revprops depth log-revprops partial-replay ) ) ) '
            self.sendClientMessage(greeting)
            self.application.logger.info("Sent svnserve greeting to client: %s" % greeting)
        finally:
            self.server.stdin.close()
            self.server.wait()
        self.svnGreetingResponse = self.readClientMessage()
        self.application.logger.info("Received greeting response from svn client: %s" % self.svnGreetingResponse)
        result = re.search('svn\+ssh://(\S*)\s', self.svnGreetingResponse)
        if not result:
            raise Exception, "Failed to tease service URL from Subversion client."
        self.serviceUrl = result.group().strip()
        #self.application.logger.info("Teased out Subversion service URL: '%s'" % self.serviceUrl)
        serviceUrlParts = self.serviceUrl.split('/')
        self.urlPath = '/' + '/'.join(serviceUrlParts[3:5])
        self.urlNoPath = '/'.join(serviceUrlParts[:3])
        if not self.urlPath:
            raise Exception, "Failed to tease service URL path from Subversion client."
        self.application.logger.info("Teased out Subversion service path: %s" % self.urlPath)

    def rewriteRequestArgs(self):
        self.sshRequestArgs.append('--tunnel-user')
        self.sshRequestArgs.append(self.person.name)
        self.sshRequestArgs.append('-r')
        self.sshRequestArgs.append(os.path.dirname(self.servicePath))

    def call(self):
        self.application.logger.info("Executing command via SSH: %s" % self.shellCmd)
        urlPatternString = '^\d+:' + self.urlNoPath.replace('+', '\\+').replace('.', '\\.')
        #self.application.logger.warning("URL pattern: %s" % urlPatternString)
        urlPattern = re.compile(urlPatternString)
        clientSideUrl = self.urlNoPath + self.urlPath
        serverSideUrl = self.urlNoPath + '/%s' % self.service.id
        #self.application.logger.warning("Client side: %s" % clientSideUrl)
        #self.application.logger.warning("Server side: %s" % serverSideUrl)
        inboundRewriter = UrlRewriter(urlPattern=urlPattern, oldUrl=clientSideUrl, newUrl=serverSideUrl, logger=self.application.logger)
        outboundRewriter = UrlRewriter(urlPattern=urlPattern, oldUrl=serverSideUrl, newUrl=clientSideUrl, logger=self.application.logger)
        canUpdate = self.isAccessAuthorised(actionName='Update')
        try:
            self.server = Popen(self.shellCmd, stdin=PIPE, stdout=PIPE, shell=True)
            # Inject messages to get things going again.
            # Discard greeting from the server (client has already seen it).
            self.readServerMessage()
            # Send greeting response from the server (we teased it from the client).
            greetingResponse = inboundRewriter.rewrite(self.svnGreetingResponse)
            self.sendServerMessage(greetingResponse)
            # Carry on with direct client-server communication.
            if canUpdate:
                validInboundPatterns = []
            else:
                validInboundPatterns = [
                    re.compile('^\(\ EXTERNAL .*'),
                    re.compile('^\(\ get-latest-rev .*'),
                    re.compile('^\(\ reparent .*'),
                    re.compile('^\(\ check-path.*'),
                    re.compile('^\(\ update .*'),
                    re.compile('^\(\ set-path .*'),
                    re.compile('^\(\ finish-report .*'),
                    re.compile('^\(\ success .*'),
                ]
            validOutboundPatterns = []
            stdinThread = PipeThread(name='Pipe inbound', stdin=sys.stdin, stdout=self.server.stdin, reader=ReadSvnMessage, logger=self.application.logger, rewriter=inboundRewriter, validPatterns=validInboundPatterns)
            stdoutThread = PipeThread(name='Pipe outbound', stdin=self.server.stdout, stdout=sys.stdout, reader=ReadSvnMessage, logger=self.application.logger, rewriter=outboundRewriter, validPatterns=validOutboundPatterns)
            stdinThread.start()
            stdoutThread.start()
            #self.application.logger.info("Waiting for server to finish...")
            returnCode = self.server.wait()
            #self.application.logger.info("Server  finished...")
            #self.application.logger.info("Joining on threads....")
            stdoutThread.join()
            #self.application.logger.info("Joined on Stdout thread.")
            stdinThread.join()
            #self.application.logger.info("Joined on Stdin thread.")
            if returnCode < 0:
                raise Exception, "SSH command was terminated by signal: %s" % (returnCode)
            elif returnCode > 0:
                raise Exception, "SSH command exited with non-zero error code: %s" % (returnCode)
            elif stdinThread.error:
                if isinstance(stdinThread.error, AccessDenied):
                    raise AccessDenied, "Access denied by inbound thread: %s" % (stdinThread.error)

                else:
                    raise Exception, "SSH inbound thread exited with error: %s" % (stdinThread.error)
            elif stdoutThread.error:
                raise Exception, "SSH outbound thread exited with error: %s" % (stdoutThread.error)
            else:
                self.application.logger.info("SSH command executed OK")
        except OSError, inst:
            raise Exception, "SSH command execution failed: %s" % inst

    def readClientMessage(self):
        message = ReadSvnMessage(sys.stdin, logger=self.application.logger).read()
        #self.application.logger.info("Received message from client: '%s'" % message)
        return message

    def sendClientMessage(self, message):
        #self.application.logger.info("Sending message to client: '%s'" % message)
        sys.stdout.write(message)

    def readServerMessage(self):
        message = ReadSvnMessage(self.server.stdout, logger=self.application.logger).read()
        #self.application.logger.info("Received message from server: '%s'" % message)
        return message

    def sendServerMessage(self, message):
        #self.application.logger.info("Sending message to server: '%s'" % message)
        self.server.stdin.write(message)



class PipeThread(Thread):

    def __init__(self, name, stdin, stdout, reader, logger, rewriter=None, validPatterns=[]):
        Thread.__init__(self)
        self.name = name
        self.stdin = stdin
        self.stdout = stdout
        self.reader = reader
        self.logger = logger
        self.rewriter = rewriter
        self.validPatterns = validPatterns
        self.service = None
        self.error = None

    def run(self):
        self.log('Running...')
        try:
            while True:
                self.log('Reading...')
                message = self.reader(self.stdin, logger=self.logger).read()
                self.log("Received message: '%s'" % message)
                # Rewrite URLs.
                if self.rewriter:
                    message = self.rewriter.rewrite(message)
                if self.validPatterns:
                    isMessageValid = False
                    for validPattern in self.validPatterns:
                        if validPattern.match(message):
                            isMessageValid = True
                            break
                    if not isMessageValid:
                        msg = "Message is not allowed: %s" % (message)
                        self.log(msg)
                        raise AccessDenied, msg
                self.stdout.write(message)
                self.stdout.flush()
                #self.log("Sent message: '%s'" % message)
        except EndOfFile:
            #self.log('End of file.')
            self.stdout.close()
            self.stdout = None
            self.stdin = None
        except Exception, inst:
            self.error = inst
            self.log('Error: %s' % inst)
            self.stdout.write('\n')
            self.stdout.flush()
            self.stdout.close()
            self.stdout = None
            self.stdin = None
            #raise
        #finally:
            #self.log('Stopping...')

    def log(self, line):
        self.logger.info(self.name+": "+line)


class ReadSvnMessage(object):

    def __init__(self, stream, logger):
        self.stream = stream
        self.logger = logger

    def read(self):
        hasMessage = False
        message = ''
        brackets = 0
        token = ''
        while not hasMessage:
            hasToken = False
            c = self.stream.read(1)
            #self.logger.info("Char: '%s' brackets: %s token: %s" % (c, brackets, token))
            if c == '':
                raise EndOfFile
            token += c
            if token == '( ':
                hasToken = True
                brackets += 1
            elif token == ') ':
                hasToken = True
                brackets -= 1
            elif re.match('\d+:', token):
                octetCount = int(token.strip(':'))
                token += self.stream.read(octetCount)
                hasToken = True
            elif re.match('\S+\s', token):
                hasToken = True
            elif re.match('\s', token):
                hasToken = True
            if hasToken:
                #self.logger.info("Token: '%s'" % token)
                message += token
                token = ''
                if not brackets:
                    hasMessage = True
                    #self.logger.info("Message: '%s'" % message)
        return message


class ReadHgMessage(object):

    def __init__(self, stream, logger):
        self.stream = stream
        self.logger = logger

    def read(self):
        hasMessage = False
        message = ''
        token = ''
        while not hasMessage:
            hasToken = False
            c = self.stream.read(1)
            #self.logger.info("Char: '%s' token: %s" % (c, token))
            if c == '':
                self.logger.info("Raising EOF.")
                raise EndOfFile
            token += c
            if token in ['between\n', 'changegroup\n', 'branches\n', 'changegroupsubset\n']:
                # There is more message.
                pass
            elif token.endswith('\n'):
                hasToken = True
            if hasToken:
                #self.logger.info("Token: '%s'" % token)
                message += token
                messageStripped = message.strip()
                tokenSplit = token.strip().split()
                if message in ['hello\n', 'between\n', 'heads\n']: #, 'unbundle\n']:
                    # There is no more message.
                    pass
                elif tokenSplit and re.match('\d+$', tokenSplit[-1]):
                    # There is more message, get it now.
                    length = tokenSplit[-1]
                    message += self.stream.read(int(length))
                else:
                    raise AccessDenied, "KForge doesn't yet know about mercurial command: %s" % message
                token = ''
                hasMessage = True
        return message


class ReadSingleChar(object):

    def __init__(self, stream, logger):
        self.stream = stream
        self.logger = logger

    def read(self):
        message = ''
        c = self.stream.read(1)
        if c == '':
            raise EndOfFile
        message = c
        #self.logger.info("Single char message: '%s'" % (c))
        return message


class UrlRewriter(object):

    def __init__(self, urlPattern, oldUrl, newUrl, logger):
        self.urlPattern = urlPattern
        self.oldUrl = oldUrl
        self.newUrl = newUrl
        self.logger = logger

    def rewrite(self, oldMessage):
        # Need to change octet count as well as string.
        newTokens = []
        oldTokens = self.tokenize(oldMessage)
        for oldToken in oldTokens:
            #self.log("Got token: %s" % oldToken)
            if self.urlPattern.match(oldToken):
                #self.log("Matched token: %s" % oldToken)
                newValue = oldToken.split(':', 1)[1].replace(self.oldUrl, self.newUrl)
                #self.log("Rewrote token: %s" % newToken)
                newLength = len(newValue)
                newToken = '%d:%s' % (newLength, newValue)
            else:
                newToken = oldToken
            newTokens.append(newToken)
        return ''.join(newTokens)

    def tokenize(self, message):
        message = list(message)
        tokens = []
        token = ''
        while message:
            hasToken = False
            c = message.pop(0)
            token += c
            if token == '( ':
                hasToken = True
            elif token == ') ':
                hasToken = True
            elif re.match('\d+:', token):
                octetCount = int(token.strip(':'))
                while octetCount:
                    token += message.pop(0)
                    octetCount -= 1
                hasToken = True
            elif re.match('\S+\s', token):
                hasToken = True
            elif re.match('\s', token):
                hasToken = True
            if hasToken:
                tokens.append(token)
                token = ''
        return tokens

    def log(self, line):
        self.logger.info("Rewriter: "+line)


class ServiceNotFound(Exception): pass

class EndOfFile(Exception): pass


