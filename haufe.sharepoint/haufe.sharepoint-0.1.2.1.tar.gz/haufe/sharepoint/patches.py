################################################################
# haufe.sharepoint
################################################################

"""
suds monkey patches
"""

import logging
import suds.metrics as metrics
from suds.transport import TransportError, Request
from suds.plugin import PluginContainer

log = logging.getLogger(__name__)

def send(self, soapenv):
    """
    Send soap message.
    @param soapenv: A soap envelope to send.
    @type soapenv: L{Document}
    @return: The reply to the sent message.
    @rtype: I{builtin} or I{subclass of} L{Object}
    """

    result = None
    location = self.location()
    binding = self.method.binding.input
    transport = self.options.transport
    retxml = self.options.retxml
    nosend = self.options.nosend
    prettyxml = self.options.prettyxml
    timer = metrics.Timer()
    log.debug('sending to (%s)\nmessage:\n%s', location, soapenv)
    try:
        self.last_sent(soapenv)
        plugins = PluginContainer(self.options.plugins)
        plugins.message.marshalled(envelope=soapenv.root())
        soapenv = soapenv.str()
        soapenv = soapenv.encode('utf-8')

        # Hack ajung to make the SOAP request fit
        soapenv = soapenv.replace('ns0:Body', 'SOAP-ENV:Body')
        soapenv = soapenv.replace('<ns0:', '<ns1:')
        soapenv = soapenv.replace('</ns0:', '</ns1:')
#        print soapenv
        ctx = plugins.message.sending(envelope=soapenv)
        soapenv = ctx.envelope
        if nosend:
            return RequestContext(self, binding, soapenv)
        request = Request(location, soapenv)
        request.headers = self.headers()
        timer.start()
        reply = transport.send(request)
        timer.stop()
        metrics.log.debug('waited %s on server reply', timer)
        ctx = plugins.message.received(reply=reply.message)
        reply.message = ctx.reply
        if retxml:
            result = reply.message
        else:
            result = self.succeeded(binding, reply.message)
    except TransportError, e:
        if e.httpcode in (202,204):
            result = None
        else:
            log.error(self.last_sent())
            result = self.failed(binding, e)
    return result

# Monkey patch SoapClient.send()
from suds.client import SoapClient
SoapClient.send = send
log.debug('Patched suds.client.SoapClient.send()')
