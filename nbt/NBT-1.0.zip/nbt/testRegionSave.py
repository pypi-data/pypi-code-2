import gzip
import nbt
import shutil

def main():

	# original file (extracted from region file)
	origFilePath = "extractedChunk.tmp"
	
	# copy it for testing
	newFilePath = "copiedChunk.tmp"
	shutil.copyfile(origFilePath, newFilePath)
	
	# open it with gzip, extract the size, then close
	gzipFile = gzip.open(newFilePath, 'rb')
	deflatedBytes = gzipFile.read()
	print "  Size of deflated bytes pre-save: " + str(len(deflatedBytes))
	gzipFile.close()
	
	# open it with NBTFile parser
	try:
		nb = nbt.NBTFile(newFilePath)
		#print nb.pretty_tree()
	except Exception, e:
		print "could not open nbt file " + str(e)
	
	# save without any changes
	nb.write_file()
	
	# open it with gzip
	print "Attempting to open post-save"
	try:
		gzipFile = gzip.open(newFilePath, 'rb')
		deflatedBytes = gzipFile.read()
		print "  Size of deflated bytes post-save: " + str(len(deflatedBytes))
	except Exception,e:
		print "  Error: " + str(e)
	gzipFile.close()

if __name__ == "__main__":
	main()