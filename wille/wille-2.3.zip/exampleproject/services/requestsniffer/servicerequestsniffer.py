import cgi

import wille

class RequestSnifferService(wille.Service):
	def execute(self, params, servicepool, keyring, workdir):
		data = '<h1>Request Data Sniffer</h1>'
		        
		# Data
		data += '<h2>Input parameters:</h2>'
		data += '<ul>'
		for key in params:
			data += "<li>%s=%s</li>" % (key, params[key])
		if len(params) == 0:
			data += '<li>No input parameters. Try adding some!</li>'
		data += '</ul>'
		
		data += '<h2>Services</h2>'
		data += '<ul>'
		if servicepool:
			for service in servicepool.services():
				data += "<li>%s</li>" % service.name
		data += '</ul>'

		data += '<h2>Keyring</h2>'
		data += '<ul>'
		if keyring:
			print keyring.keys()
			for key in keyring.keys():
				data += ("<li><code>%s</code></li>" % cgi.escape(str(key)))
				
		else:
			data += "<li><i>(empty)</i></li>"
		data += '</ul>'

		# Return tuple response:
		# First item: data
		# Second item: additional HTTP headers
		# Third item: HTTP response code (default=200)
		return (data, {'Content-type': 'text/html'})

# Command-line support
if __name__ == "__main__": wille.run_service()
