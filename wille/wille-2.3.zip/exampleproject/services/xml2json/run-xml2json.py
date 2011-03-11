import xml2json
import xml.dom.minidom

import wille

class XML2JSONService(wille.Service):
	def execute(self, params, servicepool, keyring, workdir):
		try:
			xmldoc = xml.dom.minidom.parseString( params['data.xml'] )
			result = xml2json.DocumentToJson( xmldoc )
		except Exception, e:
			result = '%s' % e
			return (result, {}, 400)	# Error code 400
		
		return (result, {'Content-type': 'application/json'})

# Command-line support
if __name__ == "__main__": wille.run_service()
