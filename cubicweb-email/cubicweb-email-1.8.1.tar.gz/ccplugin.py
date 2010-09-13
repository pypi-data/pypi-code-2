"""cubicweb-ctl plugin providing the mboximport command

:organization: Logilab
:copyright: 2007-2009 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
__docformat__ = "restructuredtext en"

import sys
from cStringIO import StringIO

from cubicweb.toolsutils import CONNECT_OPTIONS, Command, config_connect
from cubicweb.cwctl import CWCTL

from cubes.email.mboximport import MBOXImporter


class MBOXImportCommand(Command):
    """Import files using the Unix mail box format into an cubicweb instance.
    The instance must use the email package.

    <pyro id>
      pyro identifier of the instance where emails have to be imported.

    <mbox file>
      path to a file using the Unix MBOX format. If "-" is given, stdin is read.
    """
    name = 'mboximport'
    arguments = '<pyro id> <mbox file>...'
    min_args = 2
    options = CONNECT_OPTIONS + (
        ("interactive",
         {'short': 'i', 'action' : 'store_true',
          'default': False,
          'help': 'ask confirmation to continue after an error.',
          }),
        )

    def run(self, args):
        """run the command with its specific arguments"""
        appid = args.pop()
        cnx = config_connect(appid, self.config)
        cnx.load_appobjects(cubes=None, subpath=('entities',))
        importer = MBOXImporter(cnx, verbose=True,
                                interactive=self.config.interactive)
        # set autocommit, add an option to control that if needed
        importer.autocommit_mode()
        try:
            for fpath in args:
                if fpath == '-':
                    stream = StringIO(sys.stdin.read())
                else:
                    stream = open(fpath)
                importer.import_mbox_stream(stream)
            if importer.error:
                print 'failed to import the following messages:'
                print '\n'.join(importer.error)
                sys.exit(1)
        except:
            # without a correct connection handling we exhaust repository's
            # connections pool.
            # the repository should be more resilient against bad clients !
            cnx.close()
            raise
        cnx.close()

CWCTL.register(MBOXImportCommand)
