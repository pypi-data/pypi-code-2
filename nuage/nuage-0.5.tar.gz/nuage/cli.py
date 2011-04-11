import argh
from nuage import get_version
from nuage import commands
from nuage.client import NuageClient


class CommandLineInterface():
    """CLI for nuage service"""

    def __init__(self):
        self.client = NuageClient()

    def run(self):
        """Parses params and determines wich commands to run"""
        self._update_cli()
        self._dispatch_commands()

    def _update_cli(self):
        if not self._cli_is_updated():
            #TODO: Perform an update from here
            print "Warning: There is a newer version of nuage cli-interface.\n run 'pip update nuage' to get it."

    def _cli_is_updated(self):
        """Determines if the local client is the latest version"""
        recent_version = self.client.get_cli_version()
        if float(get_version()) < float(recent_version):
            return False
        return True

    def _dispatch_commands(self):
        p = argh.ArghParser()
        p.add_commands(commands.get_commands())
        p.dispatch()


def main():
    CommandLineInterface().run()

if __name__ == "__main__":
    main()
