from dexy.handler import DexyHandler
import pexpect
import time
import handlers.subprocess

### @export "jirb-handler"
class JirbHandler(handlers.subprocess.ProcessSectionwiseInteractiveHandler):
    VERSION = "/usr/bin/env jirb --version"
    EXECUTABLE = "/usr/bin/env jirb --prompt-mode simple"
    INPUT_EXTENSIONS = [".rb"]
    PROMPT = ">>"
    TRAILING_PROMPT = "=>"
    OUTPUT_EXTENSIONS = [".txt"]
    ALIASES = ['jirb']

### @export "java-handler"
class JavaHandler(DexyHandler):
    VERSION = "/usr/bin/env java -version"
    INPUT_EXTENSIONS = [".java"]
    OUTPUT_EXTENSIONS = [".txt"]
    ALIASES = ['java']
    
    def process(self):
        # Create a working directory in artifacts with the hash name, use this
        # to store .java and .class files
        raise
        print "original file name: ", self.doc.name
        command = "/usr/bin/env javac %s" % (self.doc.name)
        self.log.debug(command)
        output = pexpect.run(command)
        self.artifact.stdout = output
        self.log.debug("\n%s" % output)
        
        command = "%s > %s" % (o_filename, self.artifact.filename)
        self.artifact.data_dict['1'] = pexpect.run(command)

