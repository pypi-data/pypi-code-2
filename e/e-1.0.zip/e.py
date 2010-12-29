
import sys
for x in sys.argv[1:]:
   exec (compile(x, '<cmdline>', 'single'))
