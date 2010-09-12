# Copyright (C) 2010 by Dr. Dieter Maurer <dieter@handshake.de>; see 'LICENSE.txt' for details
"""The configured wsdl mashaller and the corresponding handler."""
from App.Common import package_home

from dm.zope.rpc.handler import handlerfactory_from_marshaller
from dm.zope.rpc.wsdl_suds import StandardWsdlMarshaller

# Our example namespace -- the "targetNamespace" from the wsdl
ns = u"http://www.dieter.handshake.de/namespace/dm.zope.rpc/service/0.1a1/"

# try to determine a file url for the wsdl
#  The approach below may not work under windows.
#  Under typical practical conditions, the wsdl is likely to be available
#  via http. Then no such filesystem dependent tricks are necessary.
wsdl_path = package_home(globals())
wsdl_url = 'file://%s/service.wsdl' % wsdl_path

marshaller = StandardWsdlMarshaller(
  wsdl_map={ns:wsdl_url},
  default_namespace=ns,
  )

soap_handler = handlerfactory_from_marshaller(marshaller)


