#!/usr/bin/env python
""" This script provides a very basic KATCP interface to the correlator. It does not include any debug facilities beyond basic logging.
Author: Jason Manley
Date: 2010-11-11"""

import logging,corr,sys,Queue,katcp
from optparse import OptionParser
from katcp.kattypes import request, return_reply, Float, Int, Str,struct


logging.basicConfig(level=logging.WARN,
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
        """Connect to all the ROACH boards. Please specify the config file and the log length. Clears any existing log. Call this again if you make external changes to the config file to reload it."""
        self.lh = corr.log_handlers.DebugLogHandler(log_len)
        self.c = corr.corr_functions.Correlator(config_file,self.lh,log_level=logging.INFO)
        return ("ok",)

    @request(Int())
    @return_reply()
    def request_initialise(self, sock, n_retries):
        """Initialise the correlator. This programs the FPGAs, configures network interfaces etc. Includes error checks. Consult the log in event of errors."""
        if self.c is None:
            return ("fail","... you haven't connected yet!")
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
            return ("fail","... you haven't connected yet!")

        print "\nlog:"
        self.lh.printMessages()

        for logent in self.c.log_handler._records:
            if logent.exc_info:
                print '%s: %s Exception: '%(logent.name,logent.msg),logent.exc_info[0:-1]
                self.reply_inform(sock, katcp.Message.inform("log",'%s: %s Exception: '%(logent.name,logent.msg),logent.exc_info[0:-1]),orgmsg)        
            else:
#log error 1234567 basic "the error string"
                self.reply_inform(sock, katcp.Message.inform("log",logent.levelname.lower(),'%i'%(logent.created*1000), logent.name ,logent.msg),orgmsg)
                #print 'Sending this message:',logent.msg
        return ("ok", len(self.c.log_handler._records))

    @request()
    @return_reply()
    def request_clr_log(self, sock):
        """Clears the log."""
        if self.c is None:
            return ("fail","... you haven't connected yet!")
        self.c.log_handler.clear()
        return ("ok",)

    @request()
    @return_reply(Str(),Str())
    def request_tx_start(self, sock):
        """Start transmission to the IP address given in the config file."""
        if self.c is None:
            return ("fail","... you haven't connected yet!")
        try:
            self.c.tx_start()
            return ("ok",
            "data %s:%i"%(self.c.config['rx_udp_ip_str'],self.c.config['rx_udp_port']),
            "meta %s:%i"%(self.c.config['rx_meta_ip_str'],self.c.config['rx_udp_port'])
            )
        except:
            return ("fail","Something broke. Check the log.")
            
    @request()
    @return_reply()
    def request_tx_stop(self, sock):
        """Stop transmission to the IP given in the config file."""
        if self.c is None:
            return ("fail","... you haven't connected yet!")
        try:
            self.c.tx_stop()
            return ("ok",)
        except:
            return ("fail","Something broke. Check the log.")
            
    @request()
    @return_reply(Str())
    def request_tx_status(self, sock):
        """Check the TX status. Returns enabled or disabled."""
        if self.c is None:
            return ("fail","... you haven't connected yet!")
        try:
            if self.c.tx_status_get(): return("ok","enabled")
            else: return("ok","disabled")
        except:
            return ("fail","Couldn't complete the request. Something broke. Check the log.")
            
    @request()
    @return_reply()
    def request_check_sys(self, sock):
        """Checks system health. If ok, system is operating nominally. If fail, you should consult the log to figure out what's wrong."""
        if self.c is None:
            return ("fail","... you haven't connected yet!")
        try:
            if self.c.check_all(): return ("ok",)
            else: return("fail","System is broken. Check the log.")
        except:
            return ("fail","Something broke spectacularly and the check didn't complete. Scrutinise the log.")
            
    @request()
    @return_reply(Int(min=0))
    def request_resync(self, sock):
        """Rearms the system. Returns the time at which the system was synch'd in ms since unix epoch."""
        if self.c is None:
            return ("fail","... you haven't connected yet!")
        try:
            time=self.c.arm()
            return ("ok",'%i'%(time*1000))
        except:
            return ("fail","Something broke spectacularly and the arm didn't complete. Scrutinise the log.")
            
    @request(Str(),include_msg=True)
    def request_get_adc_snapshot(self, sock, orgmsg, ant_str):
        """Grabs a snapshot of data from the antenna, pol specified."""
        if self.c is None:
            return katcp.Message.reply(orgmsg.name,"fail","... you haven't connected yet!")
        try:
            ant,pol=(int(ant_str[:-1]),ant_str[-1])
            if ant < 0 or ant > self.c.config['n_ants']: 
                return katcp.Message.reply(orgmsg.name,"fail","Antenna index out of range (0-%i)."%self.c.config['n_ants'])
            if not pol in self.c.config['pol_map']: 
                return katcp.Message.reply(orgmsg.name,"fail","Bad polarisation specified.")
            snapName='adc_snap'
            bramName='bram'
            ffpga_n,xfpga_n,fxaui_n,xxaui_n,feng_input = self.c.get_ant_location(ant,pol) 
            packedData = self.c.ffpgas[ffpga_n].get_snap(snapName + str(feng_input), [bramName],man_trig=True,man_valid=True,wait_period=0.01)
            # unpack the data
            unpackedBytes = struct.unpack('>%ib'%(packedData['length']*4), packedData[bramName])
            print unpackedBytes
            return katcp.Message.reply(orgmsg.name,'ok',*unpackedBytes)

        except:
            return ("fail","Couldn't complete data grab.")
            
    @request(Float(min=0))
    @return_reply()
    def request_acc_time(self, sock, acc_time):
        """Set the accumulation time in seconds (float)."""
        if self.c is None:
            return ("fail","... you haven't connected yet!")
        try:
            self.c.acc_time_set(acc_time)
            return ("ok",)
        except:
            return ("fail","Something broke spectacularly and the request didn't complete. Scrutinise the log.")
            
    @request(include_msg=True)
    @return_reply(Int())
    def request_get_adc_ampl(self, sock, orgmsg):
        """Get the current RF input levels to the DBE in dBm."""
        if self.c is None:
            return ("fail","... you haven't connected yet!")
        amps=self.c.adc_amplitudes_get()
        for i in amps:
            rf_level=amps[i]['rms_db'] - self.c.rf_status_get(*i)[1] 
            self.reply_inform(sock, katcp.Message.inform(orgmsg.name,"%i%c"%(i[0],i[1]),"%2.2f"%rf_level),orgmsg)
        return ("ok", len(amps))
        
    @request(include_msg=True)
    @return_reply(Int())
    def request_get_ant_status(self, sock, orgmsg):
        """Decode and report the status of all connected F engines. This will automatically clear the registers after the readback."""
        if self.c is None:
            return ("fail","... you haven't connected yet!")
        fstat = self.c.feng_status_get_all()
        self.c.rst_fstat()
        for i in fstat:
            out_str=[]
            for ent in fstat[i]: 
                out_str.append(str(ent))
                out_str.append(str(fstat[i][ent]))
            self.reply_inform(sock, katcp.Message.inform(orgmsg.name,"%i%c"%(i[0],i[1]),*out_str),orgmsg)
        return ("ok", len(fstat))
        
    @request(Str(),include_msg=True)
    def request_eq_get(self, sock, orgmsg, ant_str):
        """Get the current EQ configuration."""
        if self.c is None:
            return katcp.Message.reply(orgmsg.name,"fail","... you haven't connected yet!")
        ant,pol=(int(ant_str[:-1]),ant_str[-1])
        if ant < 0 or ant > self.c.config['n_ants']: 
            return katcp.Message.reply(orgmsg.name,"fail","Antenna index out of range (0-%i)."%self.c.config['n_ants'])
        if not pol in self.c.config['pol_map']: 
            return katcp.Message.reply(orgmsg.name,"fail","Bad polarisation specified.")
        eq=self.c.eq_spectrum_get(ant,pol)
        return katcp.Message.reply(orgmsg.name,'ok',*eq)
    
        
    def request_eq_set(self, sock, orgmsg):
        """Set the current EQ configuration for a given antenna. ?eq-set 0x 1123+456j 555+666j 987+765j..."""
        if self.c is None:
            return katcp.Message.reply(orgmsg.name,"fail","... you haven't connected yet!")
        ant_str=orgmsg.arguments[0]
        ant,pol=(int(ant_str[:-1]),ant_str[-1])
        if ant < 0 or ant > self.c.config['n_ants']: 
            return katcp.Message.reply(orgmsg.name,"fail","Antenna index out of range (0-%i)."%self.c.config['n_ants'])
        if not pol in self.c.config['pol_map']: 
            return katcp.Message.reply(orgmsg.name,"fail","Bad polarisation specified.")

        eq_coeffs=[]
        if len(orgmsg.arguments) != (self.c.config['n_chans']+1): #+1 to account for antenna label
            return katcp.Message.reply(orgmsg.name,"fail","Sorry, you didn't specify the right number of coefficients (expecting %i, got %i)."%(self.c.config['n_chans'],len(orgmsg.arguments)-1))

        for arg in orgmsg.arguments[1:]:
            eq_coeffs.append(eval(arg))

        self.c.eq_spectrum_set(ant,pol,init_coeffs=eq_coeffs)

        return katcp.Message.reply(orgmsg.name,'ok')

    def request_fr_delay_set(self, sock, orgmsg):
        """Set the fringe rate and delay compensation config for a given antenna. Parms: antpol, fringe_offset (degrees), fr_rate (Hz), delay (seconds), delay rate, load_time (Unix seconds), <ignore check>. If there is a seventh argument, don't do any checks to see if things loaded properly. If the load time is negative, load asap."""
        if self.c is None:
            return katcp.Message.reply(orgmsg.name,"fail","... you haven't connected yet!")
        ant_str=orgmsg.arguments[0]
        ant,pol=(int(ant_str[:-1]),ant_str[-1])
        if ant < 0 or ant > self.c.config['n_ants']: 
            return katcp.Message.reply(orgmsg.name,"fail","Antenna index out of range (0-%i)."%self.c.config['n_ants'])
        if not pol in self.c.config['pol_map']: 
            return katcp.Message.reply(orgmsg.name,"fail","Bad polarisation specified.")

        fr_offset   =float(orgmsg.arguments[1])
        fr_rate     =float(orgmsg.arguments[2])
        delay       =float(orgmsg.arguments[3])
        del_rate    =float(orgmsg.arguments[4])
        ld_time     =float(orgmsg.arguments[5])

        if len(orgmsg.arguments)>6: 
            ld_check=False
        #    print 'Ignoring load check.'
        else: 
            ld_check=True
        #    print 'Check for correct load.'

        stat = self.c.fr_delay_set(ant,pol,fringe_phase=fr_offset,fringe_rate=fr_rate,delay=delay,delay_rate=del_rate,ld_time=ld_time,ld_check=ld_check)
        out_str=[]
        for ent in stat: 
            out_str.append(str(ent))
            out_str.append("%12.10e"%(stat[ent]))

        return katcp.Message.reply(orgmsg.name,'ok',*out_str)
        

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
