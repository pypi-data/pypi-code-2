import logging
from distutils.core import Command

from nowsync.scripts import commands

class NowSyncServerCommand(Command):
    description = "run NowSync server"
    user_options = []
    
    def initialize_options(self):
        pass
    
    def finalize_options(self):
        pass
    
    def run(self):
        commands.run_server()
                
class NowSyncClientCommand(Command):
    description = "run NowSync client"
    user_options = []
    
    def initialize_options(self):
        pass
    
    def finalize_options(self):
        pass
    
    def run(self):
        commands.run_client()