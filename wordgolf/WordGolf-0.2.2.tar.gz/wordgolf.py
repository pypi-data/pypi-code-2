"""Main startup file"""

from optparse import OptionParser
import sys

if sys.version_info[0] == 3:
    print 'Python 3 is not supported'
    sys.exit(1)
elif sys.version_info[1] <= 5:
    print 'Python 2.6+ is required'
    sys.exit(1)
    
parser = OptionParser()
parser.add_option("-a", "--any", dest="any", default=False, action="store_true",
                  help="accept any word (don't check spelling)")
parser.add_option("-s", "--suggest", dest="suggest", default=False, action="store_true",
                  help="fill in a short word on right click")
parser.add_option("-f", "--framerate", dest="framerate", default=60, type="int",
                  help="framerate to use for the engine")
parser.add_option("-p", "--holes", dest="holes", default="3,6,9,12,15,18", type="str",
                  help="possible options for how many holes to play")
                  
(options, args) = parser.parse_args()

import game.graphical
game.graphical.main(options, args)



