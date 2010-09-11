# Copyright (C) 2010 by Dr. Dieter Maurer <dieter@handshake.de>; see 'LICENSE.txt' for details
"""Support for WSDL described web services accessed via SOAP (over HTTP).

See ``README.txt`` for details.
"""

from suds.client import Client
from suds.sax.parser import Parser

from zope.interface import implements, Interface
from zope.schema import TextLine, Dict, ASCIILine

from dm.zope.rpc.interfaces import IErrorCode, IErrorMessage, IDataAdapter

from dm.zope.rpc.adapter import StandardDataAdapter
from dm.zope.rpc.marshaller import CommunicatingMarshallerBase
from dm.zope.rpc.handler import handlerfactory_from_marshaller
from dm.zope.rpc.util import is_standard_request


class SudsDataAdapter(object):
  """mixin class to filter out ``suds`` peculiarities."""

  def normalize_in(self, value):
    value = super(SudsDataAdapter, self).normalize_in(value)
    # "suds" delivers an unpicklable unicode subtpye -- convert to true unicode
    if isinstance(value, unicode) and type(value) is not unicode:
      return unicode(value)
    # standard normalization keeps "suds" private information -- filter out
    if isinstance(value, dict):
      return dict(i for i in value.iteritems()
                  if not (i[0].startswith('__') and i[0].endswith('__'))
                  )
    return value


class StandardSudsDataAdapter(SudsDataAdapter, StandardDataAdapter): pass


class IWsdlMarshallerOptions(Interface):
  """Generic WSDL specific marshaller options."""

  wsdl_map = Dict(
    title=u"Map namespace to WSDL url",
    description=u"Maps the namespace found in method invocation messages to the url used to retrieve the WSDL for that namespace.",
    key_type=TextLine(),
    value_type=ASCIILine(), # in fact an url
    )

  default_namespace = TextLine(
    title=u"The namespace to be used for GET requests",
    )


class WsdlMarshaller(CommunicatingMarshallerBase):
  """Generic ``WSDL described SOAP`` marshaller."""
  implements(IWsdlMarshallerOptions)

  # unfortunately (and contrary to my expectation),
  #  "suds" does not support SOAP 1.2
  #  Thus, use the SOAP 1.1 "text/xml"
  # content_type = "application/soap+xml; charset=utf-8"
  content_type = "text/xml; charset=utf-8"
  process_get_requests = True # must remember the method


  def parse_request(self, request):
    if is_standard_request(request):
      # a "GET" like request (might also be an urlencoded "POST")
      # we need to determine the method from the url and the default namespace
      methodname = request.path[-1] # fails if the path is too short
      self.method = self._lookup(self.default_namespace, methodname)
      return
    # we have a SOAP entity
    #  it may either be in "request.other['SOAPXML']" (Zope >= 2.12)
    #  or in "request['BODY']" (do not ask for the reason for this difference)
    soap = request.other.get('SOAPXML') or request['BODY']
    # keep the content type to support both SOAP 1.1 as well as SOAP 1.2
    #  Note: there might be more differences to be handled
    #  Note: "suds" does not yet support SOAP 1.2
    #if request.get('CONTENT_TYPE', '').lower().startswith('text/xml'):
      #self.content_type = 'text/xml; charset=utf-8'
    # determine the method
    root = Parser().parse(string=soap)
    env = root.getChild('Envelope')
    env.promotePrefixes()
    body = env.getChild('Body')
    call = body.children[0] # the method invocation element
    method_name = call.name
    method = self.method = \
             self._lookup(call.namespace()[1], method_name)
    binding = method.binding.input
    # code extracted from "suds.bindings.binding.Binding.get_reply"
    body = binding.multiref.process(body)
    nodes = binding.replycontent(method, body)
    # Note: "method" has its input and output exchanged.
    #  Therefore, "returned_types" in fact means "parameter_types".
    rtypes = binding.returned_types(method)
    params = binding.replycomposite(rtypes, nodes)
    return method_name, (), IDataAdapter(self).normalize_in(params)

  def marshal_result(self, value):
    # the interpretation of "value" is a bit ambiguous:
    #  Unlike SOAP, Python does not support named output parameters
    #  nor multiple return values (not suggested by SOAP but
    #  easily modellable). Python only supports a single return value;
    #  everything else needs emulation.
    #  Following the example of ``suds.bindings.binding.Bindingget_reply``,
    #  we use WSDL inspection to get hints how to map *value* to
    #  the result.
    method = self.method
    value = IDataAdapter(self).normalize_out(value)
    __traceback_info__ = value
    # Note: ``method.unwrapped`` gives the original method (input and output
    #  not exchanged)
    rtypes = method.binding.output.returned_types(method.unwrapped_)
    # determine *args* and *kw* from *value* depending on how
    #  the WSDL wants the result
    if len(rtypes) == 0:
      # the WSDL does not want a return value
      args, kw = (), {}
    elif len(rtypes) == 1:
      # the WSDL wants a single return value -- use *value*
      args, kw = (value,), {}
    else:
      # the WSDL wants a sequence of values
      #  we pass *value" as *kw*, if it is a dict; otherwise as *args*.
      #  In the latter case, *value* must be a sequence and
      #  we strip away excess values (and hope
      #  this happens automatically in the former case)
      if isinstance(value, dict): args, kw = (), value
      else: args, kw = value[:len(rtypes)], {}
    return method.binding.output.get_message(method, args, kw)

  def marshal_exception(self, exc):
    raise NotImplementedError("cannot yet handle exceptions")


  def _lookup(self, namespace, method):
    """look up *method* in the WSDL for *namespace*.

    As we are using ``suds`` on the server (rather than client) side,
    we must exchange its ``input`` and ``output`` in order
    not to invalidate internally expected invariants (to be specific:
    ``get_reply`` always uses ``sopa.output`` and ``get_messages``
    ``soap.input`` of a method).
    We use access transformers to achieve this.

    Note: we currently rely on the ``suds`` caching. Should this prove
    not efficient enough, we would need to implement our own caching.
    Special measures would be required to use an instance based cache
    as each request uses a cloned mashaller.
    """
    __traceback_info__ = namespace, method
    suds = Client(self.wsdl_map[namespace])
    method = getattr(suds.service, method).method
    return _InputOutputExchanger(method)


class StandardWsdlMarshaller(WsdlMarshaller, StandardSudsDataAdapter):
  pass
  


class _InputOutputExchanger(object):
  """exchange method's ``input`` and ``output`` binding."""
  unwrapped_ = None

  def __init__(self, method): self.unwrapped_ = method

  def __getattr__(self, attr):
    if attr == 'soap': return _InputOutputExchanger2(self.unwrapped_.soap)
    return getattr(self.unwrapped_, attr)


class _InputOutputExchanger2(object):
  """exchange binding's ``input`` and ``output`` attributes."""
  __soap = None

  def __init__(self, soap): self.__soap = soap

  def __getattr__(self, attr):
    if attr == 'input': attr = 'output'
    elif attr == 'output': attr = 'input'
    return getattr(self.__soap, attr)
    
    

