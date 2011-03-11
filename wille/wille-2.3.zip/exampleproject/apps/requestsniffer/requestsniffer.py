import cgi

import wille

class IndexPage:
	def GET(self, request):
		params = request.input()
		wille = request.wille_client()
		data = '<h1>App Request Sniffer</h1>'
		
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
		if wille.services():
			for service in wille.services():
				data += "<li>%s</li>" % service.name
		data += '</ul>'

		data += '<h2>Keyring</h2>'
		data += '<ul>'
		if wille.keyring:
			print wille.keyring.keys()
			for key in wille.keyring.keys():
				data += ("<li><code>%s</code></li>" % cgi.escape(str(key)))
		else:
			data += "<li><i>(empty)</i></li>"
		data += '</ul>'
		
		return data
	
	def POST(self, request):
		return self.GET(request)

urls = (
	("/", IndexPage),
)

# Standalone launch
if __name__ == "__main__": wille.run_app(urls)
