import time
import sys

print ("SUCCESS ON %s SEC" % sys.argv[1])
secs = int(sys.argv[1])
time.sleep(secs)

# Return sucess
sys.exit(0)