import time
import sys

# Simple summing based integer checksum
def checksum_simple(data):
	chksum = int(0)	
	for item in data:
		chksum += int(ord(item))
	return chksum

if __name__=='__main__':
	if len(sys.argv)<3:
		print ("Usage: upload_test.py [filename] [checksum]")
		sys.exit(1)
	filename = sys.argv[1]
	checksum = int(sys.argv[2])

	raw_data = open(filename,'rb').read()
	calc_checksum = checksum_simple(raw_data)
	if checksum == calc_checksum:
		print ("OK - checksum match (%s)" % checksum)
	else:
		print ("CHECKSUM ERROR (was: %s, should be: %s)" % (calc_checksum, checksum))
		sys.exit(-1)