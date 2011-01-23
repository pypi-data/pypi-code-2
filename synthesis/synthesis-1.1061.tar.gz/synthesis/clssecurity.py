import os
import sys
import gnupg
from conf import settings
import testcase_settings
#from IPython.Shell import IPShellEmbed
from borg import Borg

class ClsSecurity(Borg):

	def __init__(self):
		print "Class created: %s" % self.__class__.__name__
		Borg.__init__(self)
		
		self.gpg = gnupg.GPG(gnupghome=settings.PGPHOMEDIR)
		
	def __repr__(self):
		pass

	def setFingerprint(self, fingerprint):
		self.fingerprint = fingerprint

	def run(self):
		#self.gpg = gnupg.GPG(gnupghome=settings.PGPHOMEDIR)
		#self.gpg = gnupg.GPG()
		
		return self.__repr__()
		
	def decrypt(self, encPayload):
		uData = str(self.gpg.decrypt(encPayload, passphrase=settings.PASSPHRASE))
		return uData
	
	def decryptFile(self, filename):
		stream = open(filename, "rb")
		if settings.PASSPHRASE == "":
			ascii_data = self.gpg.decrypt_file(stream, always_trust=True) 
		else:
			ascii_data = self.gpg.decrypt_file(stream, passphrase=settings.PASSPHRASE) # e.g. after stream = open(filename, "rb")
		stream.close()
		return str(ascii_data)
		
	def decryptFile2Stream(self, filename):
		from StringIO import StringIO
		uData = self.decryptFile(filename)
		uDataStream = StringIO(uData)
		return uDataStream
		
	def listKeys(self):
		keys = self.gpg.list_keys()
		print keys
		
	def encrypt(self, payload):
		# Against a memory String
		encrypted_ascii_data = self.gpg.encrypt(payload, self.fingerprint)
		return encrypted_ascii_data
		
	def encryptFile(self, filename, encryptedFile):
		#ipshell = IPShellEmbed()
		stream = open(filename, "r")
		encrypted_ascii_data = self.gpg.encrypt_file(stream, self.fingerprint) # e.g. after stream = open(filename, "rb")
		#ipshell()
		outFile = open(encryptedFile, 'w')
		outFile.write(str(encrypted_ascii_data))
		# close the output stream
		outFile.close()
		#print encrypted_ascii_data
		stream.close()
		
		
def main():
	cls = ClsSecurity()
	inputFile = os.path.join(testcase_settings.INPUTFILES_PATH, testcase_settings.XML_DECRYPTED_FILE)
	outputFile = inputFile + ".gpg"
	cls.setFingerprint('97A798CF9E8D9F470292975E70DE787C6B57800F')
	cls.encryptFile(inputFile, outputFile)
	dData = cls.decryptFile(outputFile)
	# now compare both dData and the source file
	stream = open(inputFile, 'r')
	uData = stream.read()
	if uData == dData:
		print 'same'
	else:
		print 'different'
	
	cls.run()
	cls.listKeys()

if __name__ == '__main__':
	sys.exit(main())
