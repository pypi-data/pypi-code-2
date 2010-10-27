#!/usr/bin/env python

import logging,corr,sys,Queue,katcp
from optparse import OptionParser
from katcp.kattypes import request, return_reply, Float, Int, Str


logging.basicConfig(level=logging.INFO,
                    stream=sys.stderr,
                    format="%(asctime)s - %(name)s - %(filename)s:%(lineno)s - %(levelname)s - %(message)s")


class DeviceExampleServer(katcp.DeviceServer):

    ## Interface version information.
    VERSION_INFO = ("Python CASPER packetised correlator server", 0, 1)

    ## Device server build / instance information.
    BUILD_INFO = ("corr", 0, 1, "rc1")

    #pylint: disable-msg=R0904
    def setup_sensors(self):
        pass

    def __init__(self, *args, **kwargs):
        super(DeviceExampleServer, self).__init__(*args, **kwargs)
        self.c = None

    @request(Str(), Int())
    @return_reply()
    def request_connect(self, sock, config_file, log_len):
        """Connect to all the ROACH boards. Please specify the config file and the log length. Clears any existing log."""
        self.lh = corr.log_handlers.DebugLogHandler(log_len)
        self.c = corr.corr_functions.Correlator(config_file,self.lh,log_level=logging.INFO)
        return ("ok",)

    @request(Int())
    @return_reply()
    def request_initialise(self, sock, n_retries):
        """Initialise the correlator. This programs the FPGAs, configures network interfaces etc. Includes error checks. Consult the log in event of errors."""
        if self.c is None:
            return katcp.Message.reply("fail","... you haven't connected yet!")
        try: 
            self.c.initialise(n_retries)
            return ("ok",)
        except:
            return ("fail","Something broke. Check the log.")

    @request(include_msg=True)
    @return_reply(Int(min=0))
    def request_get_log(self, sock, orgmsg):
        """Fetch the log."""
        if self.c is None:
            print 'cant do that yet'
            return ("fail","... you haven't connected yet!")

        #self.reply_inform(sock, katcp.Message.inform(orgmsg.name, "foo", "bar"),orgmsg)
        #self.reply_inform(sock, katcp.Message.inform(orgmsg.name, "foo", orgmsg)
        #self.inform(sock, katcp.Message.inform("log", "arg1"))

        print "Something broke. Sending this log:"
        self.lh.printMessages()

        for logent in self.c.log_handler._records:
            if logent.exc_info:
                self.reply_inform(sock, katcp.Message.inform(orgmsg.name,'%s: %s Exception: '%(logent.name,logent.msg),logent.exc_info[0:-1]),orgmsg)        
            else:
                self.reply_inform(sock, katcp.Message.inform(orgmsg.name, '%s: %s'%(logent.name,logent.msg)),orgmsg)
        return ("ok", len(self.c.log_handler._records))


    @request(include_msg=True)
    @return_reply()
    def request_start_tx(self, sock, orgmsg):
        """Start transmission to the IP given in the config file."""
        try:
            self.c.start_tx()
            return ("ok",)
        except:
            return ("fail","Something broke. Check the log.")
            
    @request(include_msg=True)
    @return_reply()
    def request_stop_tx(self, sock, orgmsg):
        """Stop transmission to the IP given in the config file."""
        try:
            self.c.stop_tx()
            return ("ok",)
        except:
            return ("fail","Something broke. Check the log.")
            


if __name__ == "__main__":

    usage = "usage: %prog [options]"
    parser = OptionParser(usage=usage)
    parser.add_option('-a', '--host', dest='host', type="string", default="", metavar='HOST',
                      help='listen to HOST (default="" - all hosts)')
    parser.add_option('-p', '--port', dest='port', type=long, default=1235, metavar='N',
                      help='attach to port N (default=1235)')
    (opts, args) = parser.parse_args()

    print "Server listening on port %d, Ctrl-C to terminate server" % opts.port
    restart_queue = Queue.Queue()
    server = DeviceExampleServer(opts.host, opts.port)
    server.set_restart_queue(restart_queue)

    server.start()
    print "Started."

    try:
        while True:
            try:
                device = restart_queue.get(timeout=0.5)
            except Queue.Empty:
                device = None
            if device is not None:
                print "Stopping ..."
                device.stop()
                device.join()
                print "Restarting ..."
                device.start()
                print "Started."
    except KeyboardInterrupt:
        print "Shutting down ..."
        server.stop()
        server.join()
