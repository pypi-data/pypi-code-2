"""
Manage a database of jokes.
"""

from os.path import isfile
from sys import platform

from argparse import ArgumentParser, RawDescriptionHelpFormatter

from jokes import JokeTable


###########################################################################
# Build the argument parser.
###########################################################################


parser_description =\
"""
DISPLAY COMMANDS:
    list    List all jokes by ID
    try     List all jokes with 'try' status
    keep    List all jokes with 'keep' status
    fail    List all jokes with 'fail' status
    retire  List all jokes with 'retire' status
    premise List all jokes with 'premise' status
    hist ID Print the entire history of a joke

CREATE COMMANDS:
    edit        Open today's journal file
    append ID+  Add joke ID to today's journal file
    build name  Print word and punchline count of set file date-'name'
    build name ID+
                Add joke ID to set file date-'name'

UPDATE COMMANDS:
    try ID+     Update joke ID to 'try' status
    keep ID+    Update joke ID to 'keep' status
    fail ID+    Update joke ID to 'fail' status
    retire ID+  Update joke ID to 'retire' status
    premise ID+ Update joke ID to 'premise' status
"""
parser = ArgumentParser(
    prog="everjoke",
    formatter_class=RawDescriptionHelpFormatter,
    description=parser_description,
    epilog='Break their legs!')  # I'm witty!
parser.add_argument(
    'COMMAND',
    nargs='*',
    help="list | build, append, edit |\
          try, fail, keep, retire, premise")


###########################################################################
# CONTROLLER
###########################################################################


class Controller():
    """ Interface between command line arguments and the joke database.  """

    def __init__(self):
        self.jokeTable = JokeTable()
        self.commandMap = {
            'list': self._list,
            'try': self._try,
            'keep': self._keep,
            'fail': self._fail,
            'retire': self._retire,
            'premise': self._premise,
            'edit': self._edit,
            'build': self._build,
            'append': self._append,
            'collect': self._collect,
            'hist': self._hist}

    def ProcessCommand(self, command, args):
        self.commandMap.get(command, self._errHandler)(args)

    def _list(self, args):
        for jokeID in args:
            self.PrintJoke(jokeID)
        if not args:
            self.ListJokes()

    def _Status(self, status, args):
        for jokeID in args:
            self.jokeTable.SetJokeStatus(jokeID, status)
        self.ListJokes(status)
        
    def _try(self, args):
        self._Status('Try', args)

    def _keep(self, args):
        self._Status('Keep', args)

    def _fail(self, args):
        self._Status('Fail', args)

    def _retire(self, args):
        self._Status('Retire', args)

    def _premise(self, args):
        self._Status('Premise', args)

    def _edit(self, args):
        self.jokeTable.EditJournal()

    def _build(self, args):
        set_name = args.pop(0)
        for jokeID in args:
            self.jokeTable.AppendJokeToFile(jokeID, set_name)
        if not args:
            print "Please specify jokes by ID."

    def _append(self, args):
        for jokeID in args:
            self.jokeTable.AppendJokeToFile(jokeID)
        if not args:
            print "Please specify jokes by ID."

    def _collect(self, args):
        for filename in args:
            self.jokeTable.AddJokesFromFile(filename)

    def _hist(self, args):
        for jokeID in args:
            self.PrintJokeHistory(jokeID)

    def _errHandler(self, args):
        print 'Invalid command, try "everjoke --help".'

    def ListJokes(self, status=None):
        """Print jokes from the database to stdout."""
        q = self.jokeTable.GetJokeList(status)
        for joke in q:
            print "%4i %-25s %-6s %-5i %3i*" %\
                  (joke.id, joke.name, joke.status, joke.wordcount,
                  joke.punchcount)

    def CollectFile(self, filename):
        self.jokeTable.AddJokesFromFile(filename)
        print "Collected jokes from %s." % filename

    def PrintJoke(self, id):
        joke = self.jokeTable.GetJokeByID(id)
        print "== %s ==\n%s" % (joke.name, joke.bodies[-1].text)

    def PrintJokeHistory(self, id):
        joke = self.jokeTable.GetJokeByID(id)
        print "== %s ==\n%s" % (joke.name, joke.bodies[-1].text)
        for body in joke.bodies:
            print "\n========\n"
            print body.text


###########################################################################
# MAIN
###########################################################################


def main():
    """Parse options and send to the controller."""
    controller = Controller()
    args = parser.parse_args()

    # Create variables for the primary command and following arguments.
    if args.COMMAND:
        command = args.COMMAND.pop(0)
        args = args.COMMAND
        controller.ProcessCommand(command, args)
    else:
        parser.print_help()
        exit()


###########################################################################
# Run the program!
###########################################################################


if __name__ == "__main__":
    main()
