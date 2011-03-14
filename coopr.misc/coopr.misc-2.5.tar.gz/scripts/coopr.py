#  _________________________________________________________________________
#
#  Coopr: A COmmon Optimization Python Repository
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  _________________________________________________________________________

# Revision: $Revision$
# Date:     $Date$

import sys

class CooprInstaller(Installer):

    def __init__(self):
        Installer.__init__(self)
        self.default_dirname='coopr'
        self.config_file='https://software.sandia.gov/svn/public/coopr/vpy/installer.ini'
        if sys.version_info[:2] < (2,5) or sys.version_info[:2] >= (3,0):
            print ""
            print "------------------------------------------------------------------"
            print "WARNING: Most Coopr packages will only work with Python 2.5 - 2.7."
            print "         You attempted to installed Coopr with:"
            print sys.version
            print "------------------------------------------------------------------"
            print ""
            sys.exit(1)

    def modify_parser(self, parser):
        Installer.modify_parser(self, parser)

        parser.add_option('--coin',
            help='Use one or more packages from the Coin Bazaar software repository.  Multiple packages are specified with a comma-separated list.',
            action='store',
            dest='coin',
            default=None)
        parser.add_option(
            '--no-site-packages',
            dest='no_site_packages',
            action='store_true',
            help="Don't give access to the global site-packages dir to the "
                "virtual environment",
            default=False)
        parser.remove_option("--site-packages")


    def get_other_packages(self, options):
        if options.coin is None:
            return
        for pkg in options.coin.split(','):
            if pkg is '':
                continue
            self.add_repository('coopr.'+pkg, root='https://projects.coin-or.org/svn/CoinBazaar/projects/coopr.'+pkg, dev=True, username=os.environ.get('COINOR_USERNAME',None))

def create_installer():
    return CooprInstaller()
