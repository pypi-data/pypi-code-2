import wille

class WeatherService(wille.Service):
	"""WeatherService - Wille Python service for creating weather report based on given address/location"""
	def execute(self, params, servicepool, keyring, workdir):
		# Parse end urlencode input parameter(s)
		from urllib import quote
		e_address = quote(params['address'])

		# Define to get a seven day weather report, starting from today
		from datetime import datetime, timedelta
		starttime = datetime.today().strftime("%Y-%m-%d")
		endtime = (datetime.today()+timedelta(days=7)).strftime("%Y-%m-%d")
		
		# Geocode address
		import httplib2
		import simplejson as json
		geocoder_root_url = 'http://maps.google.com/maps/api/geocode/json?'
		geocoder_req_url = geocoder_root_url+'address='+e_address+'&sensor=false'
		h = httplib2.Http("")
		resp, content = h.request(geocoder_req_url)
		geocoder_result = json.loads(content)
		location = geocoder_result['results'][0]['geometry']['location']
		
		# Get a day weather report
		from suds.client import Client
		forecast_wsdl_url = 'http://www.weather.gov/forecasts/xml/DWMLgen/wsdl/ndfdXML.wsdl'
		client = Client(forecast_wsdl_url)
		weather_report = client.service.NDFDgen(latitude = location['lat'], \
											    longitude = location['lng'], \
											    product = 'time-series', \
											    startTime = starttime, \
											    endTime = endtime, \
											    weatherParameters = False )
		
		# Return weather report XML
		return (weather_report.encode('utf-8'), {'Content-type': 'application/xml; charset=utf-8'})

# Command-line support
if __name__ == "__main__": wille.run_service()
