import os
import sys

APP_ROOT = os.getenv('APP_ROOT')

sys.path.insert(0, '%s/pomsets-gui/src' % APP_ROOT)
sys.path.insert(0, '%s/pomsets-core/src' % APP_ROOT)
sys.path.insert(0, '%s/cloudpool/src' % APP_ROOT)
sys.path.insert(0, '%s/pypatterns/src' % APP_ROOT)

from pomsets_qt import *

import cloud as PicloudModule
PicloudModule.start_simulator()

if __name__=="__main__":
    main()
