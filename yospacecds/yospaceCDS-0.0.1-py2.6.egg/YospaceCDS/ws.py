#!/usr/bin/python

import SOAPpy
import types

# Which Yospace CDS platform should be targetted?
CDSDOMAIN = "cds1.yospace.com"

# Patch a bug in SOAPpy (boolean values not marshalled correctly)
def _dump_bool(self, obj, tag, typed = 1, ns_map = {}):
	from SOAPpy.Config import Config
	import SOAPpy.Types
	if Config.debug: print "In dump_bool."
	self.out.append(self.dumper(None, 'boolean', SOAPpy.Types.booleanType(obj), tag, typed, ns_map, self.genroot(ns_map)))
SOAPpy.SOAPBuilder.dump_bool = _dump_bool

#-- Basic Exception Class -----------------------------------------------------

class SOAPError(StandardError):
	"Report back a non 200 status as an exception"
	pass

#-- "Abstract" WebService Client Class ----------------------------------------

class _ws(SOAPpy.WSDL.Proxy):
	"Convenience class for CDS Web Services, based on the WSDL"

	SERVICEADDRESS = "set_this_to_a_service_address"

	def __init__(self, un, pw, throw_faults=1, debug=0, service=None):
		"Connect to the service and remember the un/pw"
		# Set the service address
		if service:
			self.SERVICEADDRESS = service
		# Initialise the SOAP sub-system, including loading the WSDL
		SOAPpy.WSDL.Proxy.__init__(
			self,
			self.SERVICEADDRESS,
			throw_faults = throw_faults,
			unwrap_results = 0,
		)

		# Tell the sub class what CDS auth data to use
		self.soapproxy.Username = un
		self.soapproxy.Password = pw
		# Allow debugging messages to be displayed
		if debug > 0:
			SOAPpy.Config.dumpSOAPOut = 1
			SOAPpy.Config.dumpSOAPIn = 1
			if debug > 1:
				SOAPpy.Config.dumpHeadersOut = 1
				SOAPpy.Config.dumpHeadersIn = 1

#-- Content Service -----------------------------------------------------------

def _CS_call(self, name, args, kw, ns = None, sa = None, hd = None, ma = None):
	"Wrapper for SOAPProxy.__call which handles auth data and status returns"
	# Add in the CDS auth data
	kw["clientApplicationId"] = self.Username
	kw["clientApplicationCredentials"] = self.Password
	# Then call the original method as normal
	response = self._old_call(name, args, kw, ns, sa, hd, ma)
	# Process the CDS status return code
	if self.throw_faults:
		if response.status != '200':
			raise SOAPError("%s = %s" % (name, response.status, ))
	# Return the entire response (Including the status value)
	return response

class ContentService(_ws):
	"CDS ContentService Client"
	def __init__(self, un, pw, throw_faults=1, debug=0, service=None):
		self.SERVICEADDRESS = "http://%s/cds-controller/contentService?wsdl" % (CDSDOMAIN, )
		_ws.__init__(
			self,
			un,
			pw,
			throw_faults=throw_faults,
			debug=debug,
			service=service
		)
		# RTM the soapproxy object:
		# First store the original __call method
		self.soapproxy._old_call = self.soapproxy._SOAPProxy__call
		# Then replace the orginial with a bound copy of the wrapper method
		self.soapproxy._SOAPProxy__call = types.MethodType(_CS_call, self.soapproxy, self.soapproxy.__class__)

#-- Media Item Service --------------------------------------------------------

def _MIS_call(self, name, args, kw, ns = None, sa = None, hd = None, ma = None):
	"Wrapper for SOAPProxy.__call which handles auth data and status returns"
	# Add in the CDS auth data
	kw["username"] = self.Username
	kw["password"] = self.Password
	# Then call the original method as normal
	response = self._old_call(name, args, kw, ns, sa, hd, ma)
	# Process the CDS status return code
	if self.throw_faults:
		if response.statusCode != '200':
			raise SOAPError("%s = %s" % (name, response.statusCode, ))
	# Return the entire response (Including the status value)
	return response

class MediaItemService(_ws):
	"CDS ContentService Client"
	def __init__(self, un, pw, throw_faults=1, debug=0, service=None):
		self.SERVICEADDRESS = "http://%s/mediaitemmanager/manage?wsdl" % (CDSDOMAIN, )
		_ws.__init__(
			self,
			un,
			pw,
			throw_faults=throw_faults,
			debug=debug,
			service=service
		)
		# RTM the soapproxy object:
		# First store the original __call method
		self.soapproxy._old_call = self.soapproxy._SOAPProxy__call
		# Then replace the orginial with a bound copy of the wrapper method
		self.soapproxy._SOAPProxy__call = types.MethodType(_MIS_call, self.soapproxy, self.soapproxy.__class__)

if __name__ == '__main__':
#	cs = ContentService("invalid", "invalid")
#	cs.show_methods()

	mis = MediaItemService("invalid", "invalid")
	mis.show_methods()
