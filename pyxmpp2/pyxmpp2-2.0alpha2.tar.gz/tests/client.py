

class TestClientSelect(InitiatorSelectTestCase):
    """TODO"""
    def test_stanza_timeout(self):
        handler = JustStreamConnectEventHandler()
        self.stream = StreamBase(u"jabber:client", [])
        self.start_transport([handler])
        self.loop.add_handler(self.stream)
        self.stream.initiate(self.transport)
        self.connect_transport()
        self.wait_short(0.5)
        self.assertTrue(self.stream.is_connected())
        self.server.write(C2S_SERVER_STREAM_HEAD)
        self.wait(1)
        iq = Iq(to_jid = "127.0.0.1", stanza_type = "get")
        payload = XMLPayload(XML(
                        "<test xmlns='http://pyxmpp.jajcus.net/test' />"))
        iq.set_payload(payload)
        handlers_called = []
        def res_handler(stanza):
            handlers_called.append("res_handler")
        def err_handler(stanza):
            handlers_called.append("err_handler")
        def tim_handler():
            handlers_called.append("tim_handler")
        self.stream.set_response_handlers(iq, res_handler, err_handler,
                                                        tim_handler, 2)
        self.wait(0.5)
        self.assertEqual(handlers_called, [])
        self.wait(4)
        self.assertEqual(handlers_called, ["tim_handler"])
        self.server.write(STREAM_TAIL)
        self.server.close()
        self.wait(1)
        self.assertFalse(self.stream.is_connected())
        event_classes = [e.__class__ for e in handler.events_received]
        self.assertEqual(event_classes, [ConnectingEvent, ConnectedEvent,
                                    StreamConnectedEvent, DisconnectedEvent])

