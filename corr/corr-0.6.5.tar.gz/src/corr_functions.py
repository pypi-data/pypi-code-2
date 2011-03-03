#! /usr/bin/env python
""" 
Selection of commonly-used correlator control functions.

Todo:
change ant,pol handling to be a tuple?

Author: Jason Manley\n
Revisions:\n
2011-02-11: JRM Issue SPEAD data descriptors for interleaved case.
2011-01-02: JRM Removed requirement for stats package (basic mode calc built-in).
                Bugfix to arm and check_feng_clks logic (waiting for half second).
2011-01-03: JRM Modified check_fpga_comms to limit random number 2**32.
2010-12-02  JRM Added half-second wait for feng clk check's PPS count
2010-11-26: JRM Added longterm ppc count check in feng clock check.
2010-11-22: JRM corr-0.6.0 now with support for fengines with 10gbe cores instead of xaui links.
                Mods to fr_delay calcs for fine delay.
                spead, pcnt and mcnt from time functions now account for wrapping counters.
2010-10-18: JRM initialise function added.
                Fix to SPEAD metadata issue when using iADCs.
2010-08-05: JRM acc_len_set -> acc_n_set. acc_let_set now in seconds.
2010-06-28  JRM Port to use ROACH based F and X engines.
                Changed naming convention for function calls.
2010-04-02  JCL Removed base_ant0 software register from Xengines, moved it to Fengines, and renamed it to use ibob_addr0 and ibob_data0.  
                New function write_ibob().
                Check for VACC errors.
2010-01-06  JRM Added gbe_out enable to X engine control register
2009-12-14  JRM Changed snap_x to expect two kinds of snap block, original simple kind, and new one with circular capture, which should have certain additional registers (wr_since_trig).
2009-12-10  JRM Started adding SPEAD stuff.
2009-12-01  JRM Added check for loopback mux sync to, and fixed bugs in, loopback_check_mcnt.\n
                Changed all "check" functions to just return true/false for global system health. Some have "verbose" option to print more detailed errors.\n
                Added loopback_mux_rst to xeng_ctrl
2009-11-06  JRM Bugfix snap_x offset triggering.\n
2009-11-04  JRM Added ibob_eq_x.\n
2009-10-29  JRM Bugfix snap_x.\n
2009-06-26  JRM UNDER CONSTRUCTION.\n
\n"""

import corr, time, sys, numpy, os, logging, katcp, struct

def statsmode(inlist):
    """Very rudimentarily calculates the mode of an input list. Only returns one value, the first mode. Can't deal with ties!"""
    value=inlist[0]
    count=inlist.count(value)
    for i in inlist:
        if inlist.count(i) > count:
            value = i 
            count = inlist.count(i)
    return value 

class Correlator:
    def __init__(self, config_file,log_handler=None,log_level=logging.ERROR):
        self.config = corr.cn_conf.CorrConf(config_file)
        self.xsrvs = self.config['servers_x']
        self.fsrvs = self.config['servers_f']
        self.allsrvs = self.fsrvs + self.xsrvs

        if log_handler == None: log_handler=corr.log_handlers.DebugLogHandler(100)
        self.log_handler = log_handler
        self.floggers=[logging.getLogger(s) for s in self.fsrvs]
        self.xloggers=[logging.getLogger(s) for s in self.xsrvs]
        self.syslogger=logging.getLogger('corrsys')
        self.loggers=self.floggers + self.xloggers

        self.xfpgas=[corr.katcp_wrapper.FpgaClient(server,self.config['katcp_port'],
                       timeout=10,logger=self.xloggers[s]) for s,server in enumerate(self.xsrvs)]
        self.ffpgas=[corr.katcp_wrapper.FpgaClient(server,self.config['katcp_port'],
                       timeout=10,logger=self.floggers[s]) for s,server in enumerate(self.fsrvs)]
        self.allfpgas = self.ffpgas + self.xfpgas

        for logger in (self.loggers): 
            logger.addHandler(self.log_handler)
            logger.setLevel(log_level)
        self.syslogger.addHandler(self.log_handler)
        self.syslogger.setLevel(log_level)

        time.sleep(1)
        if not self.check_katcp_connections():
            raise RuntimeError("Connection to FPGA boards failed.")

    def __del__(self):
        self.disconnect_all()

    def disconnect_all(self):
        """Stop all TCP KATCP links to all FPGAs defined in the config file."""
        #tested ok corr-0.5.0 2010-07-19
        try:
            for fpga in (self.allfpgas): fpga.stop()
        except:
            pass

    def get_revs(self):
        """Extracts and returns a dictionary of the version control information from the F and X engines."""
        rv={}
        rv['feng_user'] = self.ffpgas[0].read_uint("rcs_user")
        rv['xeng_user'] = self.xfpgas[0].read_uint("rcs_user")
        return rv

    def get_bl_order(self):
        """Return the order of baseline data output by a CASPER correlator X engine."""
        n_ants=self.config['n_ants']
        order1, order2 = [], []
        for i in range(n_ants):
            for j in range(int(n_ants/2),-1,-1):
                k = (i-j) % n_ants
                if i >= k: order1.append((k, i))
                else: order2.append((i, k))
        order2 = [o for o in order2 if o not in order1]
        return tuple([o for o in order1 + order2])

    def get_crosspol_order(self):
        "Returns the order of the cross-pol terms out the X engines"
        pol1=self.config['rev_pol_map'][0]
        pol2=self.config['rev_pol_map'][1]
        return (pol1+pol1,pol2+pol2,pol1+pol2,pol2+pol1) 

    def prog_all(self):
        """Programs all the FPGAs."""
        #tested ok corr-0.5.0 2010-07-19
        for fpga in self.ffpgas:
            fpga.progdev(self.config['bitstream_f'])
        for fpga in self.xfpgas:
            fpga.progdev(self.config['bitstream_x'])
        if not self.check_fpga_comms(): 
            raise RuntimeError("Failed to successfully program FPGAs.")
        else:
            self.syslogger.info("All FPGAs programmed ok.")

    def check_fpga_comms(self):
        """Checks FPGA <-> BORPH communications by writing a random number into a special register, reading it back and comparing."""
        #Modified 2010-01-03 so that it works on 32 bit machines by only generating random numbers up to 2**30.
        rv = True
        for fn,fpga in enumerate(self.allfpgas):
            #keep the random number below 2^32-1 and do not include zero (default register start value), but use a fair bit of the address space...
            rn=numpy.random.randint(1,2**30)
            try: 
                fpga.write_int('sys_scratchpad',rn)
                self.loggers[fn].info("FPGA comms ok")
            except: 
                rv=False
                self.loggers[fn].error("FPGA comms failed")
        if rv==True: self.syslogger.info("All FPGA comms ok.")
        return rv

    def deprog_all(self):
        """Deprograms all the FPGAs."""
        #tested ok corr-0.5.0 2010-07-19
        for fpga in self.ffpgas:
            fpga.progdev('')
        for fpga in self.xfpgas:
            fpga.progdev('')
        self.syslogger.info("All FPGAs deprogrammed.")

    def xread_all(self,register,bram_size,offset=0):
        """Reads a register of specified size from all X-engines. Returns a list."""
        rv = [fpga.read(register,bram_size,offset) for fpga in self.xfpgas]
        return rv

    def fread_all(self,register,bram_size,offset=0):
        """Reads a register of specified size from all F-engines. Returns a list."""
        rv = [fpga.read(register,bram_size,offset) for fpga in self.ffpgas]
        return rv

    def xread_uint_all(self, register):
        """Reads a value from register 'register' for all X-engine FPGAs."""
        return [fpga.read_uint(register) for fpga in self.xfpgas]

    def fread_uint_all(self, register):
        """Reads a value from register 'register' for all F-engine FPGAs."""
        return [fpga.read_uint(register) for fpga in self.ffpgas]

    def xwrite_int_all(self,register,value):
        """Writes to a 32-bit software register on all X-engines."""
        [fpga.write_int(register,value) for fpga in self.xfpgas]

    def fwrite_int_all(self,register,value):
        """Writes to a 32-bit software register on all F-engines."""
        [fpga.write_int(register,value) for fpga in self.ffpgas]

    def feng_ctrl_set_all(self,**kwargs):
        """Sets bits of all the Fengine control registers. Keeps any previous state for individual X engines.
            \nPossible boolean kwargs:
            \n\t tvg_noise_sel
            \n\t tvg_ffdel_sel
            \n\t tvg_pkt_sel
            \n\t tvg_ct_sel
            \n\t tvg_en
            \n\t adc_protect_disable 
            \n\t flasher_en
            \n\t gbe_enable
            \n\t gbe_rst
            \n\t clr_status
            \n\t arm
            \n\t mrst
            \n\t soft_sync"""
        #modified oct 26 2010 to keep previous state
        key_bit_lookup={
            'tvg_noise_sel':20,
            'tvg_ffdel_sel':19,
            'tvg_pkt_sel':  18,
            'tvg_ct_sel':   17,
            'tvg_en':       16,
            'adc_protect_disable':   13,
            'flasher_en':   12,
            'gbe_enable':   9,
            'gbe_rst':      8,
            'clr_status':   3,
            'arm':          2,
            'soft_sync':    1,
            'mrst':         0,
            }
        values = self.feng_ctrl_get_all()
        run_cnt=0
        run_cnt_target=1
        while run_cnt < run_cnt_target:
            for fn,fpga in enumerate(self.ffpgas):
                value=values[fn]['raw']
                for key in kwargs:
                    if (kwargs[key] == 'toggle') and (run_cnt==0):
                        value = value ^ (1<<(key_bit_lookup[key]))
                    elif (kwargs[key] == 'pulse'):
                        run_cnt_target = 3
                        if run_cnt == 0: value = value & ~(1<<(key_bit_lookup[key]))
                        elif run_cnt == 1: value = value | (1<<(key_bit_lookup[key]))
                        elif run_cnt == 2: value = value & ~(1<<(key_bit_lookup[key]))
                    elif kwargs[key] == True: 
                        value = value | (1<<(key_bit_lookup[key]))
                    elif kwargs[key] == False: 
                        value = value & ~(1<<(key_bit_lookup[key]))
                    else: 
                        raise RuntimeError("Sorry, you must specify True, False, 'toggle' or 'pulse' for %s."%key)
                fpga.write_int('control', value)
            run_cnt = run_cnt +1


    def feng_ctrl_get_all(self):
        """Reads and decodes the values from all the Fengine control registers."""
        all_values = self.fread_uint_all('control')
        return [{'mrst':bool(value&(1<<0)),
                'soft_sync':bool(value&(1<<1)),
                'arm':bool(value&(1<<2)),
                'clr_status':bool(value&(1<<3)),
                'gbe_rst': bool(value&(1<<8)),
                'gbe_enable': bool(value&(1<<9)),
                'adc_protect_disable':bool(value&(1<<13)),
                'flasher_en':bool(value&(1<<12)),
                'tvg_en':bool(value&(1<<16)),
                'tvg_ct_sel':bool(value&(1<<17)),
                'tvg_pkt_sel':bool(value&(1<<18)),
                'tvg_ffdel_sel':bool(value&(1<<19)),
                'tvg_noise_sel':bool(value&(1<<20)),
                'raw':value,
                } for value in all_values]

    def kitt_enable(self):
        """Turn on the Knightrider effect for system idle."""
        self.feng_ctrl_set_all(flasher_en=True)
        self.xeng_ctrl_set_all(flasher_en=True)

    def kitt_disable(self):
        """Turn off the Knightrider effect for system idle."""
        self.feng_ctrl_set_all(flasher_en=False)
        self.xeng_ctrl_set_all(flasher_en=False)

    def feng_tvg_sel(self,noise=False,ct=False,pkt=False,ffdel=False):
        """Turns TVGs on/off on the F engines."""
        self.feng_ctrl_set_all(tvg_en=True,  tvg_noise_sel=noise, tvg_ct_sel=ct, tvg_pkt_sel=pkt, tvg_ffdel_sel=ffdel)
        self.feng_ctrl_set_all(tvg_en=False, tvg_noise_sel=noise, tvg_ct_sel=ct, tvg_pkt_sel=pkt, tvg_ffdel_sel=ffdel)

    def xeng_ctrl_set_all(self,**kwargs):
        """Sets bits of all the Xengine control registers. Keeps any previous state for individual X engines.
            \nPossible boolean kwargs:
            \n\t loopback_mux_rst
            \n\t gbe_out_enable
            \n\t gbe_out_rst
            \n\t gbe_enable
            \n\t flasher_en 
            \n\t gbe_rst
            \n\t cnt_rst
            \n\t vacc_rst"""
        #modified oct 26 2010 to keep previous state
        #modified 12 Nov 2010 to add toggle function
        values = self.xeng_ctrl_get_all()
        run_cnt=0
        run_cnt_target=1
        #print run_cnt,self.xeng_ctrl_get_all()[0]
        key_bit_lookup={'flasher_en':12,'loopback_mux_rst':10,'gbe_out_enable':16,'gbe_enable':9,'gbe_rst':15,'cnt_rst':8,'vacc_rst':0,'gbe_out_rst':11}
        while run_cnt < run_cnt_target:
            for fn,fpga in enumerate(self.xfpgas):
                value=values[fn]['raw']
                for key in kwargs:
                    if (kwargs[key] == 'toggle') and (run_cnt==0):
                        value = value ^ (1<<(key_bit_lookup[key]))
                    elif (kwargs[key] == 'pulse'):
                        run_cnt_target = 3
                        if run_cnt == 0: value = value & ~(1<<(key_bit_lookup[key]))
                        elif run_cnt == 1: value = value | (1<<(key_bit_lookup[key]))
                        elif run_cnt == 2: value = value & ~(1<<(key_bit_lookup[key]))
                    elif kwargs[key] == True: 
                        value = value | (1<<(key_bit_lookup[key]))
                    elif kwargs[key] == False: 
                        value = value & ~(1<<(key_bit_lookup[key]))
                    else: 
                        raise RuntimeError("Sorry, you must specify True, False, 'toggle' or 'pulse' for %s."%key)
                fpga.write_int('ctrl', value)
            run_cnt = run_cnt +1
            #print run_cnt,self.xeng_ctrl_get_all()[0]

    def xeng_ctrl_get_all(self):
        """
        Reads and decodes the values from all the X-engine control registers.
        @return a list by X-engine fpga hostname
        """
        values = self.xread_uint_all('ctrl')
        return [{'raw':value,
                'gbe_out_enable':bool(value&(1<<16)),
                'gbe_rst':bool(value&(1<<15)),
                'flasher_en':bool(value&(1<<12)),
                'gbe_out_rst':bool(value&(1<<11)),
                'loopback_mux_rst':bool(value&(1<<10)),
                'gbe_enable':bool(value&(1<<9)),
                'cnt_rst':bool(value&(1<<8)),
                'vacc_rst':bool(value&(1<<0))} for value in values]

    def fft_shift_set_all(self,fft_shift=-1):
        """Configure the FFT on all F engines to the specified schedule. If not specified, default to schedule listed in config file."""
        #tested ok corr-0.5.0 2010-07-20
        if fft_shift <0:
            fft_shift = self.config['fft_shift']
        for ant in range(self.config['f_per_fpga']*self.config['n_pols']):
            self.fwrite_int_all("fft_shift%i"%ant,fft_shift)
        self.syslogger.info('Set FFT shift patterns on all Fengs to 0x%x.'%fft_shift)

    def fft_shift_get_all(self):
        rv={}
        for ant in range(self.config['n_ants']):
            for pol in self.config['pols']:
                ffpga_n,xfpga_n,fxaui_n,xxaui_n,feng_input = self.get_ant_location(ant,pol)
                rv[(ant,pol)]=self.ffpgas[ffpga_n].read_uint('fft_shift%i'%feng_input)
        return rv

    def feng_status_get_all(self):
        """Reads and decodes the status register from all the Fengines."""
        rv={}
        for ant in range(self.config['n_ants']):
            for pol in self.config['pols']:
                ffpga_n,xfpga_n,fxaui_n,xxaui_n,feng_input = self.get_ant_location(ant,pol)
                value = self.ffpgas[ffpga_n].read_uint('fstatus%i'%feng_input)
                #for xaui_n in range(self.config['n_xaui_per_ffpga
                rv[(ant,pol)]={
#                                'sync_val':(value&((2**32)-(2**28)))>>28,
                                'xaui_lnkdn':bool(value&(1<<17)),
                                'xaui_over':bool(value&(1<<16)),
                                'adc_bad':bool(value&(1<<4)),
                                'ct_error':bool(value&(1<<3)),
                                'adc_overrange':bool(value&(1<<2)),
                                'fft_overrange':bool(value&(1<<1)),
                                'quant_overrange':bool(value&(1<<0))}
        return rv

    def initialise(self,n_retries=40,reprogram=True,clock_check=True,set_eq=True,config_10gbe=True,config_output=True,send_spead=True):
        """Initialises the system and checks for errors."""
        if reprogram:
            self.deprog_all()
            time.sleep(1)
            self.prog_all()

        self.tx_stop()

        if self.config['feng_out_type'] == '10gbe':
            self.feng_ctrl_set_all(gbe_enable=False, gbe_rst=False) 
            self.feng_ctrl_set_all(gbe_enable=False, gbe_rst=True)
            self.syslogger.info("Holding F engine 10GbE cores in reset.")

        self.xeng_ctrl_set_all(gbe_enable=False, gbe_rst=False) 
        self.xeng_ctrl_set_all(gbe_enable=False, gbe_rst=True)
        self.syslogger.info("Holding X engine 10GbE cores in reset.")

        if not self.arm(): self.syslogger.error("Failed to successfully arm and trigger system.")
        if clock_check == True: 
            if not self.check_feng_clks(): 
                raise RuntimeError("System clocks are bad. Please fix and try again.")

        #Only need to set brd id on xeng if there's no incomming 10gbe, else get from base ip addr
        if self.config['feng_out_type'] == '10gbe':
            self.xeng_brd_id_set()
        self.feng_brd_id_set()

        if self.config['adc_type'] == 'katadc': 
            self.rf_gain_set_all()

        self.fft_shift_set_all()

        if set_eq: self.eq_set_all()
        else: self.syslogger.info('Skipped EQ config.')

        if config_10gbe: 
            self.config_roach_10gbe_ports()
            sleep_time=((self.config['10gbe_ip']&255 + self.config['n_xeng']*self.config['n_xaui_ports_per_xfpga'])*0.1) 
            self.syslogger.info("Waiting %i seconds for ARP to complete."%sleep_time)
            time.sleep(sleep_time)
            
        if self.config['feng_out_type'] == '10gbe':
            self.feng_ctrl_set_all(gbe_enable=False, gbe_rst=False) 
            self.feng_ctrl_set_all(gbe_enable=True, gbe_rst=False)
            self.syslogger.info('F engine 10GbE cores re-enabled.')

        self.xeng_ctrl_set_all(gbe_enable=False, gbe_rst=False)
        self.xeng_ctrl_set_all(gbe_enable=True, gbe_rst=False)
        self.syslogger.info("X engine 10GbE cores re-enabled.")

        time.sleep(len(self.xfpgas)/2)
        self.rst_cnt()
        time.sleep(1)


        if self.config['feng_out_type'] == 'xaui':
            if not self.check_xaui_error(): raise RuntimeError("XAUI checks failed.")
            if not self.check_xaui_sync(): raise RuntimeError("Fengines appear to be out of sync.")
        if not self.check_10gbe_tx(): raise RuntimeError("10GbE cores are not transmitting properly.")
        if not self.check_10gbe_rx(): raise RuntimeError("10GbE cores are not receiving properly.")
        if self.config['feng_out_type'] == 'xaui':
            if not self.check_loopback_mcnt_wait(n_retries=n_retries): raise RuntimeError("Loopback muxes didn't sync.")
        if not self.check_x_miss(): raise RuntimeError("X engines are missing data.")
        self.acc_time_set()
        self.rst_cnt()
        self.syslogger.info("Waiting %i seconds for an integration to finish so we can test the VACCs."%self.config['int_time'])
        time.sleep(self.config['int_time']+0.1)
        if not self.check_vacc(): raise RuntimeError("Vector accumulators are broken.")

        if send_spead:
            self.spead_static_meta_issue()
            self.spead_time_meta_issue()
            self.spead_data_descriptor_issue()
            self.spead_eq_meta_issue()

        if config_output: 
            self.config_udp_output()
            #self.tx_start()

        self.kitt_enable()
        self.syslogger.info("Initialisation completed.")

    def tx_start(self):
        """Start outputting SPEAD products. Only works for systems with 10GbE output atm."""
        #if ip<0:
        #    ip=self.config['rx_udp_ip']
        #else:
        #    self.config.write('receiver','rx_udp_ip_str',socket.inet_ntoa(ip))
        #    self.config['rx_udp_ip']=ip
        if self.config['out_type']=='10gbe':
            self.xeng_ctrl_set_all(gbe_out_enable=True)
            self.syslogger.info("Correlator output started to %s:%i."%(
            self.config['rx_udp_ip_str'],
            self.config['rx_udp_port']))
        else:
            self.syslogger.error('Sorry, your output type is not supported. Could not enable output.')
            #raise RuntimeError('Sorry, your output type is not supported.')


    def tx_stop(self):
        """Stops outputting SPEAD data over 10GbE links."""
        if self.config['out_type']=='10gbe':
            self.xeng_ctrl_set_all(gbe_out_enable=False)
            self.syslogger.info("Correlator output paused.")
        else:
            #raise RuntimeError('Sorry, your output type is not supported.')
            self.syslogger.warn("Sorry, your output type is not supported. Cannot disable output.")

    def tx_status_get(self):
        """Returns boolean true/false if the correlator is currently outputting data. Currently only works on systems with 10GbE output."""
        if self.config['out_type']!='10gbe': raise RuntimeError("This function only works for systems with 10GbE output!")
        rv=True
        stat=self.xeng_ctrl_get_all()
        for xn,xsrv in enumerate(self.xsrvs):
            if stat[xn]['gbe_out_enable'] != True or stat[xn]['gbe_out_rst']!=False: rv=False
        return rv

    def check_feng_clks(self, quick_test=False):
        """ Checks all Fengine FPGAs' clk_frequency registers to confirm correct PPS operation. Requires that the system be sync'd."""
        #tested ok corr-0.5.0 2010-07-19
        rv=True
        expect_rate = round(self.config['feng_clk']/1000000) #expected clock rate in MHz.

        #estimate actual clk freq 
        if quick_test==False:
            clk_freq=self.feng_clks_get()
            clk_mhz=[round(cf) for cf in clk_freq] #round to nearest MHz
            for fbrd,fsrv in enumerate(self.fsrvs):
                if clk_freq[fbrd] <= 100: 
                    self.floggers[fbrd].error("No clock detected!")
                    rv=False

                if (clk_mhz[fbrd] > (expect_rate+1)) or (clk_mhz[fbrd] < (expect_rate -1)) or (clk_mhz[fbrd]==0):
                   self.floggers[fbrd].error("Estimated clock freq is %i MHz, where expected rate is %i MHz."%(clk_mhz[fbrd], expect_rate))
                   rv=False


            if rv==False: 
                self.syslogger.error("Some Fengine clocks are dead. We can't continue.")
                return False
            else: 
                self.syslogger.info("Fengine clocks are approximately correct at %i MHz."%expect_rate)

        #check long-term integrity
        #wait for within 100ms of a second, then delay a bit and query PPS count.
        ready=((int(time.time()*10)%10)==5)
        while not ready: 
            ready=((int(time.time()*10)%10)==5)
            #print time.time()
            time.sleep(0.05)
        uptime=[ut[1] for ut in self.feng_uptime()]
        exp_uptime = numpy.floor(time.time() - self.config['sync_time'])
        mode = statsmode(uptime)
        modalmean=numpy.mean(mode)
        for fbrd,fsrv in enumerate(self.fsrvs):
            if uptime[fbrd] == 0: 
                rv=False
                self.floggers[fbrd].error("No PPS detected! PPS count is zero.")

            elif (uptime[fbrd] > (modalmean+1)) or (uptime[fbrd] < (modalmean -1)) or (uptime[fbrd]==0):
                rv=False
                self.floggers[fbrd].error("PPS count is %i pulses, where modal mean is %i pulses. This board has a bad 1PPS input."%(uptime[fbrd], modalmean))

            elif uptime[fbrd] != exp_uptime: 
                rv=False
                self.floggers[fbrd].error("Expected uptime is %i seconds, but we've counted %i PPS pulses."%(exp_uptime,uptime[fbrd]))
            else:
                self.floggers[fbrd].info("Uptime is %i seconds, as expected."%(uptime[fbrd]))

        #check the PPS against sampling clock.
        all_values = self.fread_uint_all('clk_frequency')
        mode = statsmode(all_values)
        modalmean=numpy.mean(mode)
        #modalmean=stats.mean(mode[1])
        modalfreq=numpy.round((expect_rate*1000000.)/modalmean,3)
        if (modalfreq != 1):
            self.syslogger.error("PPS period is approx %3.2f Hz, not 1Hz."%modalfreq)
            rv=False
        else:
            self.syslogger.info("Assuming a clock of %iMHz and that the PPS and clock are correct on most boards, PPS period is %3.2fHz and clock rate is %6.3fMHz."%(expect_rate,modalfreq,modalmean/1000000.))

        for fbrd,fsrv in enumerate(self.fsrvs):
            if all_values[fbrd] == 0: 
                self.floggers[fbrd].error("No PPS or no clock... clk_freq register is zero!")
                rv=False
            if (all_values[fbrd] > (modalmean+2)) or (all_values[fbrd] < (modalmean -2)) or (all_values[fbrd]==0):
                self.floggers[fbrd].error("Clocks between PPS pulses is %i, where modal mean is %i. This board has a bad sampling clock or PPS input."%(all_values[fbrd], modalmean))
                rv=False
            else:
                self.floggers[fbrd].info("Clocks between PPS pulses is %i as expected."%(all_values[fbrd]))

        return rv

    def feng_uptime(self):
        """Returns a list of tuples of (armed_status and pps_count) for all fengine fpgas. Where the count since last arm of the pps signals received (and hence number of seconds since last arm)."""
        #tested ok corr-0.5.0 2010-07-19
        all_values = self.fread_uint_all('pps_count')
        pps_cnt = [val & 0x7FFFFFFF for val in all_values]
        arm_stat = [bool(val & 0x80000000) for val in all_values]
        return [(arm_stat[fn],pps_cnt[fn]) for fn in range(len(self.ffpgas))]

    def mcnt_current_get(self,ant=None,pol=None):
        "Returns the current mcnt for a given antenna, pol. If not specified, return a list of mcnts for all connected f engine FPGAs"
        #tested ok corr-0.5.0 2010-07-19
        if ant==None and pol==None:
            msw = self.fread_uint_all('mcount_msw')
            lsw = self.fread_uint_all('mcount_lsw')
            mcnt = [(msw[i] << 32) + lsw[i] for i,srv in enumerate(self.fsrvs)]
            return mcnt
        else:
            ffpga_n,xfpga_n,fxaui_n,xxaui_n,feng_input = self.get_ant_location(ant,pol)
            msw = self.ffpgas[ffpga_n].read_uint('mcount_msw')
            lsw = self.ffpgas[ffpga_n].read_uint('mcount_lsw')
            return (msw << 32) + lsw 
    
    def pcnt_current_get(self):
        "Returns the current packet count. ASSUMES THE SYSTEM IS SYNC'd!"
        msw = self.ffpgas[0].read_uint('mcount_msw')
        lsw = self.ffpgas[0].read_uint('mcount_lsw')
        return int(((msw << 32) + lsw)*self.config['pcnt_scale_factor']/self.config['mcnt_scale_factor'])
    
    def arm(self,spead_update=True):
        """Arms all F engines, records arm time in config file and issues SPEAD update. Returns the UTC time at which the system was sync'd in seconds since the Unix epoch (MCNT=0)"""
        #tested ok corr-0.5.0 2010-07-19
        #wait for within 100ms of a half-second, then send out the arm signal.
        ready=((int(time.time()*10)%10)==5)
        while not ready: 
            ready=((int(time.time()*10)%10)==5)
        trig_time=int(numpy.ceil(time.time()+1)) #Syncs on the next second, to ensure any sync pulses already in the datapipeline have a chance to propagate out.
        self.feng_ctrl_set_all(arm=False)
        self.feng_ctrl_set_all(arm=True)
        self.config.write('correlator','sync_time',trig_time)
        self.feng_ctrl_set_all(arm=False)
        time.sleep(2.1)
        armed_stat=[armed[0] for armed in self.feng_uptime()]
        rv=True
        for i,stat in enumerate(armed_stat):
            if armed_stat[i]:
                self.floggers[i].error("Did not trigger. Check clock and 1PPS.")
                rv=False
            else:
                self.floggers[i].info("Arm successful.")
        if rv==True:
            if spead_update: self.spead_time_meta_issue()
            self.syslogger.info("All boards armed and triggered OK.")
            return trig_time
        else:
            self.syslogger.error("Failed to arm and trigger the system properly.")
            raise RuntimeError("Failed to arm and trigger the system properly.")

    def get_roach_gbe_conf(self,start_addr,fpga,port):
        """Generates 10GbE configuration strings for ROACH-based xengines starting from 
        ip "start_addr" for FPGA numbered "FPGA" (offset from start addr).
        Returns a (mac,ip,port) tuple suitable for passing to tap_start."""
        sys.stdout.flush()
        ip = (start_addr + fpga) & ((1<<32)-1)
        mac = (2<<40) + (2<<32) + ip
        return (mac,ip,port)

    def rst_cnt(self):
        """Resets all error counters on all connected boards."""
        self.xeng_ctrl_set_all(cnt_rst=False)
        self.xeng_ctrl_set_all(cnt_rst=True)
        self.xeng_ctrl_set_all(cnt_rst=False)
        self.rst_fstat()

    def rst_fstat(self):
        """Clears the status registers on all connected F engines."""
        self.feng_ctrl_set_all(clr_status='pulse')

    def rst_vaccs(self):
        """Resets all Xengine Vector Accumulators."""
        self.xeng_ctrl_set_all(vacc_rst='pulse')

    def xeng_clks_get(self):
        """Returns the approximate clock rate of each X engine FPGA in MHz."""
        #tested ok corr-0.5.0 2010-07-19
        return [fpga.est_brd_clk() for fpga in self.xfpgas]

    def feng_clks_get(self):
        """Returns the approximate clock rate of each F engine FPGA in MHz."""
        #tested ok corr-0.5.0 2010-07-19
        return [fpga.est_brd_clk() for fpga in self.ffpgas]

    def check_katcp_connections(self):
        """Returns a boolean result of a KATCP ping to all all connected boards."""
        result = True
        for fn,fpga in enumerate(self.allfpgas):
            try:
                fpga.ping()
                self.loggers[fn].info('KATCP connection ok.')
            except:
                self.loggers[fn].error('KATCP connection failure.')
                result = False
        if result == True: self.syslogger.info('KATCP communication with all boards ok.')
        else: self.syslogger.error('KATCP communication with one or more boards FAILED.')
        return result

    def check_x_miss(self):
        """Returns boolean pass/fail to indicate if any X engine has missed any data, or if the descrambler is stalled."""
        rv = True
        for x in range(self.config['x_per_fpga']):
            err_check = self.xread_uint_all('pkt_reord_err%i'%(x))
            cnt_check = self.xread_uint_all('pkt_reord_cnt%i'%(x))
            for xbrd,xsrv in enumerate(self.xsrvs):
                if (err_check[xbrd] !=0) or (cnt_check[xbrd] == 0) :
                    self.xloggers[xbrd].error("Missing X engine data on this xeng %i."%x)
                    rv=False
                else:
                    self.xloggers[xbrd].info("All X engine data on this xeng %i OK."%x)
        if rv == True: self.syslogger.info("No missing Xeng data.")
        else: self.syslogger.error("Some Xeng data missing.")
        return rv

    def check_xaui_error(self):
        """Returns a boolean indicating if any X engines have bad incomming XAUI links.
        Checks that data is flowing and that no errors have occured. Returns True/False."""
        if self.config['feng_out_type'] != 'xaui': raise RuntimeError("According to your config file, you don't have any XAUI cables connected to your F engines!")
        rv = True
        for x in range(self.config['n_xaui_ports_per_xfpga']):
            cnt_check = self.xread_uint_all('xaui_cnt%i'%(x))
            err_check = self.xread_uint_all('xaui_err%i'%x)
            for f in range(self.config['n_ants']/self.config['n_ants_per_xaui']/self.config['n_xaui_ports_per_xfpga']):
                if (cnt_check[f] == 0):
                    rv=False
                    self.xloggers[f].error('No F engine data on XAUI port %i.'%(x))
                elif (err_check[f] !=0):
                    self.xloggers[f].error('Bad F engine data on XAUI port %i.'%(x))
                    rv=False
                else:
                    self.xloggers[f].info('F engine data on XAUI port %i OK.'%(x))

        if rv == True: self.syslogger.info("All XAUI links look good.")
        else: self.syslogger.error("Some bad XAUI links here.")
        return rv
    
    def check_10gbe_tx(self):
        """Checks that the 10GbE cores are transmitting data. Outputs boolean good/bad."""
        rv=True
        if self.config['feng_out_type'] == 'xaui':
            for x in range(self.config['n_xaui_ports_per_xfpga']):
                firstpass_check = self.xread_uint_all('gbe_tx_cnt%i'%x)
                time.sleep(0.01)
                secondpass_check = self.xread_uint_all('gbe_tx_cnt%i'%x)

                for f in range(self.config['n_ants']/self.config['n_ants_per_xaui']/self.config['n_xaui_ports_per_xfpga']):
                    if (secondpass_check[f] == 0) or (secondpass_check[f] == firstpass_check[f]):
                        self.xloggers[f].error('10GbE core %i is not sending any data.'%(x))
                        rv = False
                    else:
                        self.xloggers[f].info('10GbE core %i is sending data.'%(x))
        elif self.config['feng_out_type'] == '10gbe':
            stat=self.feng_status_get_all()
            for ant,pol in stat:
                ffpga_n,xfpga_n,fxaui_n,xxaui_n,feng_input = self.get_ant_location(ant,pol)
                if stat[(ant,pol)]['xaui_lnkdn'] == True:
                    self.floggers[ffpga_n].error("10GbE core %i for input %i%c link is down."%(fxaui_n,ant,pol))
                    rv = False
                elif stat[(ant,pol)]['xaui_over'] == True:
                    self.floggers[ffpga_n].error('10GbE core %i for input %i%c is overflowing.'%(fxaui_n,ant,pol))
                    rv = False
                
            for x in range(self.config['n_xaui_ports_per_ffpga']):
                firstpass_check = self.fread_uint_all('gbe_tx_cnt%i'%x)
                time.sleep(0.01)
                secondpass_check = self.fread_uint_all('gbe_tx_cnt%i'%x)
                for f in range(self.config['n_ffpgas']):
                    if (secondpass_check[f] == 0) or (secondpass_check[f] == firstpass_check[f]):
                        self.floggers[f].error('10GbE core %i is not sending any data.'%(x))
                        rv = False
                    else:
                        self.floggers[f].info('10GbE core %i is sending data.'%(x))

        else:
            self.syslogger.error("Skipped 10GbE TX check")

        if rv == True: self.syslogger.info("10GbE TX exchange check passed.")
        else: self.syslogger.error("Some 10GbE cores aren't sending data.")
        return rv

    def check_10gbe_rx(self):
        """Checks that all the 10GbE cores are receiving packets."""
        rv=True
        for x in range(min(self.config['n_xaui_ports_per_xfpga'],self.config['x_per_fpga'])):
            firstpass_check = self.xread_uint_all('gbe_rx_cnt%i'%x)
            time.sleep(0.01)
            secondpass_check = self.xread_uint_all('gbe_rx_cnt%i'%x)
            for s,xsrv in enumerate(self.xsrvs):
                if (secondpass_check[s] == 0):
                    rv=False
                    self.xloggers[s].error('10GbE core %i is not receiving any packets.'%(x))
                elif (secondpass_check[s] == firstpass_check[s]):
                    rv=False
                    self.xloggers[s].error('10GbE core %i received %i packets, but then stopped..'%(x,secondpass_check[s]))
                else:
                    self.xloggers[s].info('10GbE core %i received %i packets total. All OK.'%(x,secondpass_check[s]))
        if rv == True: self.syslogger.info("All 10GbE cores are receiving data.")
        else: self.syslogger.error("Some 10GbE cores aren't receiving data.")
        return rv

    def check_loopback_mcnt_wait(self,n_retries=40):
        """Waits up to n_retries for loopback muxes to sync before returning false if it is still failing."""
        sys.stdout.flush()
        loopback_ok=self.check_loopback_mcnt()
        loop_retry_cnt=0
        while (not loopback_ok) and (loop_retry_cnt< n_retries):
            time.sleep(1)
            loop_retry_cnt+=1
            self.syslogger.info("waiting for loopback lock... %i tries so far."%loop_retry_cnt)
            sys.stdout.flush()
            loopback_ok=self.check_loopback_mcnt()
        if self.check_loopback_mcnt(): 
            self.syslogger.info("loopback lock achieved after %i tries."%loop_retry_cnt)
            return True
        else: 
            self.syslogger.error("Failed to achieve loopback lock after %i tries."%n_retries)
            return False


    def check_loopback_mcnt(self):
        """Checks to see if the mux_pkts block has become stuck waiting for a crazy mcnt Returns boolean true/false."""
        rv=True
        for x in range(min(self.config['n_xaui_ports_per_xfpga'],self.config['x_per_fpga'])):
            firstpass_check = self.xread_all('loopback_mux%i_mcnt'%x,4)
            time.sleep(0.01)
            secondpass_check = self.xread_all('loopback_mux%i_mcnt'%x,4)
            for f in range(self.config['n_ants']/self.config['n_ants_per_xaui']/self.config['n_xaui_ports_per_xfpga']):
                firstloopmcnt,firstgbemcnt=struct.unpack('>HH',firstpass_check[f])
                secondloopmcnt,secondgbemcnt=struct.unpack('>HH',secondpass_check[f])

                if (secondgbemcnt == firstgbemcnt):
                    self.xloggers[f].error('10GbE input on GbE port %i is stalled.' %(x))
                    rv = False

                if (secondloopmcnt == firstloopmcnt):
                    self.xloggers[f].error('Loopback on GbE port %i is stalled.' %x)
                    rv = False

                if abs(secondloopmcnt - secondgbemcnt) > (self.config['x_per_fpga']*len(self.xsrvs)): 
                    self.xloggers[f].error('Loopback mux on GbE port %i is not syncd.'%x)
                    rv=False
        if rv == True: self.syslogger.info("All loopback muxes are locked.")
        else: self.syslogger.error("Some loopback muxes aren't locked.")
        return rv


    def check_vacc(self):
        """Returns boolean pass/fail to indicate if any X engine has vector accumulator errors."""
        rv = True
        for x in range(self.config['x_per_fpga']):
            err_check = self.xread_uint_all('vacc_err_cnt%i'%(x))
            cnt_check = self.xread_uint_all('vacc_cnt%i'%(x))
            for nx,xsrv in enumerate(self.xsrvs):
                if (err_check[nx] !=0):
                    self.xloggers[nx].error('Vector accumulator errors on this X engine %i.'%(x))
                    rv=False
                if (cnt_check[nx] == 0) :
                    self.xloggers[nx].error('No vector accumulator data this X engine %i.'%(x))
                    rv=False
        if rv == True: self.syslogger.info("All vector accumulators are workin' perfectly.")
        else: self.syslogger.error("Some vector accumulators are broken.")
        return rv

    def check_all(self,clock_check=True):
        """Checks system health. If true, system is operating nominally. If false, you should run the other checks or consult the logs to figure out what's wrong."""
        if clock_check == True: 
            #if not self.check_xeng_clks(): return False
            if not self.check_feng_clks(): return False
        if self.config['feng_out_type'] == 'xaui':
            if not self.check_xaui_error(): return False
            if not self.check_xaui_sync(): return False
        if not self.check_10gbe_tx(): return False
        if not self.check_10gbe_rx(): return False
        if self.config['feng_out_type'] == 'xaui':
            if not self.check_loopback_mcnt_wait(n_retries=n_retries): return False
        if not self.check_x_miss(): return False
        return True

    def tvg_vacc_sel(self,constant=0,n_values=-1,spike_value=-1,spike_location=0,counter=False):
        """Select Vector Accumulator TVG in X engines. Disables other TVGs in the process. 
            Options can be any combination of the following:
                constant:   Integer.    Insert a constant value for accumulation.
                n_values:   Integer.    How many numbers to inject into VACC. Value less than zero uses xengine timing.
                spike_value:    Int.    Inject a spike of this value in each accumulated vector. value less than zero disables.
                spike_location: Int.    Position in vector where spike should be placed.
                counter:    Boolean.    Place a ramp in the VACC.
        """
        #bit5 = rst
        #bit4 = inject counter
        #bit3 = inject vector
        #bit2 = valid_sel
        #bit1 = data_sel
        #bit0 = enable pulse generation

        if spike_value>=0:
            ctrl = (counter<<4) + (1<<3) + (1<<1)
        else:
            ctrl = (counter<<4) + (0<<3) + (1<<1)

        if n_values>0:
            ctrl += (1<<2)
            
        for xeng in range(self.config['x_per_fpga']):
            self.xwrite_int_all('vacc_tvg%i_write1'%(xeng),constant)
            self.xwrite_int_all('vacc_tvg%i_ins_vect_loc'%(xeng),spike_location)
            self.xwrite_int_all('vacc_tvg%i_ins_vect_val'%(xeng),spike_value)
            self.xwrite_int_all('vacc_tvg%i_n_pulses'%(xeng),n_values)
            self.xwrite_int_all('vacc_tvg%i_n_per_group'%(xeng),self.config['n_bls']*self.config['n_stokes']*2)
            self.xwrite_int_all('vacc_tvg%i_group_period'%(xeng),self.config['n_ants']*self.config['xeng_acc_len'])
            self.xwrite_int_all('tvg_sel',(ctrl + (1<<5))<<9)
            self.xwrite_int_all('tvg_sel',(ctrl + (0<<5) + 1)<<9)


    def tvg_xeng_sel(self,mode=0, user_values=()):
        """Select Xengine TVG. Disables VACC (and other) TVGs in the process. Mode can be:
            0: no TVG selected.
            1: select 4-bit counters. Real components count up, imaginary components count down. Bot polarisations have equal values.
            2: Fixed numbers: Pol0real=0.125, Pol0imag=-0.75, Pol1real=0.5, Pol1imag=-0.2
            3: User-defined input values. Should be 8 values, passed as tuple in user_value."""

        if mode>4 or mode<0:
            raise RuntimeError("Invalid mode selection. Mode must be in range(0,4).")
        else:
            self.xwrite_int_all('tvg_sel',mode<<3) 

        if mode==3:
            for i,v in enumerate(user_val):
                for xeng in range(self.config['x_per_fpga']):
                    self.xwrite_int_all('xeng_tvg%i_tv%i'%(xeng,i),v)

    def fr_delay_set(self,ant,pol,delay=0,delay_rate=0,fringe_phase=0,fringe_rate=0,ld_time=-1,ld_check=True):
        """Configures a given ant-pol to a delay in seconds using both the coarse and the fine delay. Also configures the fringe rotation components. This is a blocking call. \n
        By default, it will wait 'till load time and verify that things worked as expected. This check can be disabled by setting ld_check param to False. \n
        Load time is optional; if not specified, load ASAP.\n
        \t Fringe offset is in degrees.\n
        \t Fringe rate is in cycles per second (Hz).\n
        \t Delay is in seconds.\n
        \t Delay rate is in seconds per second.\n
        Notes: \n
        DOES NOT ACCOUNT FOR WRAPPING MCNT.\n
        IS A ONCE-OFF UPDATE (no babysitting by software)\n"""
        #Fix to fine delay calc on 2010-11-19

        fine_delay_bits=16
        coarse_delay_bits=16
        fine_delay_rate_bits=16
        fringe_offset_bits=16
        fringe_rate_bits=16

        bitshift_schedule=23
        
        min_ld_time = 0.1 #assume we're able to set and check all the registers in 100ms
        ffpga_n,xfpga_n,fxaui_n,xxaui_n,feng_input = self.get_ant_location(ant,pol)

        #delays in terms of ADC clock cycles:
        delay_n=delay*self.config['adc_clk']    #delay in clock cycles
        #coarse_delay = int(numpy.round(delay_n)) #delay in whole clock cycles #good for rev 369.
        coarse_delay = int(delay_n) #delay in whole clock cycles #testing for rev370
        fine_delay = (delay_n-coarse_delay)    #delay remainder. need a negative slope for positive delay
        fine_delay_i = int(fine_delay*(2**(fine_delay_bits)))  #16 bits of signed data over range 0 to +pi
    
        fine_delay_rate=int(float(delay_rate) * (2**(bitshift_schedule + fine_delay_rate_bits-1))) 

        #figure out the fringe as a fraction of a cycle        
        fr_offset=int(fringe_phase/float(360) * (2**(fringe_offset_bits)))
        #figure out the fringe rate. Input is in cycles per second (Hz). 1) divide by brd clock rate to get cycles per clock. 2) multiply by 2**20
        fr_rate = int(float(fringe_rate) / self.config['feng_clk'] * (2**(bitshift_schedule + fringe_rate_bits-1)))

        cnts=self.ffpgas[ffpga_n].read_uint('delay_tr_status%i'%feng_input)
        arm_cnt0=cnts>>16
        ld_cnt0=cnts&0xffff

        act_delay=(coarse_delay + float(fine_delay_i)/2**fine_delay_bits)/self.config['adc_clk']
        act_fringe_offset = float(fr_offset)/(2**fringe_offset_bits)*360 
        act_fringe_rate = float(fr_rate)/(2**(fringe_rate_bits+bitshift_schedule-1))*self.config['feng_clk']
        act_delay_rate = float(fine_delay_rate)/(2**(bitshift_schedule + fine_delay_rate_bits-1))

        if (delay != 0):
            if (fine_delay_i==0) and (coarse_delay==0): 
                self.floggers[ffpga_n].error('Requested delay is too small for this configuration (our resolution is too low).')
            elif abs(fine_delay_i) > 2**(fine_delay_bits): 
                self.floggers[ffpga_n].error('Internal logic error calculating fine delays.')
                raise RuntimeError('Internal logic error calculating fine delays.')
            elif abs(coarse_delay) > (2**(coarse_delay_bits)): 
                self.floggers[ffpga_n].error('Requested coarse delay (%es) is out of range (+-%es).'%(
                float(coarse_delay)/self.config['adc_clk'],
                float(2**(coarse_delay_bits-1))/self.config['adc_clk']))
                raise RuntimeError('Requested delay (%es) is out of range (+-%es).'%(
                float(coarse_delay)/self.config['adc_clk'],
                float(2**(coarse_delay_bits-1))/self.config['adc_clk']))
            else: self.floggers[ffpga_n].warn('Delay actually set to %e seconds.'%act_delay)

        if (delay_rate != 0):
            if (fine_delay_rate==0): self.floggers[ffpga_n].error('Requested delay rate too slow for this configuration.')
            if (abs(fine_delay_rate) > 2**(fine_delay_rate_bits-1)): 
                self.floggers[ffpga_n].error('Requested delay rate out of range (+-%e).'%(2**(bitshift_schedule-1)))
                raise RuntimeError('Requested delay rate is out of range (+-%e).'%(1./(2**(bitshift_schedule))))
            else: self.floggers[ffpga_n].warn('Delay rate actually set to %e seconds per second.'%act_delay_rate) 

        if (fringe_phase !=0):
            if (fr_offset == 0): 
                self.floggers[ffpga_n].error('Requested fringe phase is too small for this configuration (we do not have enough resolution).')
            else: self.floggers[ffpga_n].warn('Fringe offset actually set to %6.3f degrees.'%act_fringe_offset)

        if (fringe_rate != 0):
            if (fr_rate==0): 
                self.floggers[ffpga_n].error('Requested fringe rate is too slow for this configuration.')
            else: self.floggers[ffpga_n].warn('Fringe rate actually set to %e Hz.'%act_fringe_rate)

        #get the current mcnt for this feng:
        mcnt=self.mcnt_current_get(ant,pol)

        #figure out the load time
        if ld_time < 0: 
            #figure out the load-time mcnt:
            ld_mcnt=int(mcnt + self.config['mcnt_scale_factor']*(min_ld_time))
        else:
            if (ld_time < (time.time() + min_ld_time)): 
                self.syslogger.error("Cannot load at a time in the past.")
                raise RuntimeError("Cannot load at a time in the past.")
            ld_mcnt=self.mcnt_from_time(ld_time)
        if (ld_mcnt < (mcnt + self.config['mcnt_scale_factor']*min_ld_time)): raise RuntimeError("This works out to a loadtime in the past!")
        
        #setup the delays:
        self.ffpgas[ffpga_n].write_int('coarse_delay%i'%feng_input,coarse_delay)
        self.floggers[ffpga_n].debug("Set a coarse delay of %i clocks."%coarse_delay)
        #fine delay (LSbs) is fraction of a cycle * 2^15 (16 bits allocated, signed integer). 
        #increment fine_delay by MSbs much every FPGA clock cycle shifted 2**20???
        self.ffpgas[ffpga_n].write('a1_fd%i'%feng_input,struct.pack('>hh',fine_delay_rate,fine_delay_i))
        self.floggers[ffpga_n].debug("Wrote %4x to fine_delay and %4x to fine_delay_rate register a1_fd%i."%(fine_delay_i,fine_delay_rate,feng_input))
        
        #print 'Coarse delay: %i, fine delay: %2.3f (%i), delay_rate: %2.2f (%i).'%(coarse_delay,fine_delay,fine_delay_i,delay_rate,fine_delay_rate)

        #setup the fringe rotation
        #LSbs is offset as a fraction of a cycle in fix_16_15 (1 = pi radians ; -1 = -1radians). 
        #MSbs is fringe rate as fractional increment to fr_offset per FPGA clock cycle as fix_16.15. FPGA divides this rate by 2**20 internally.
        self.ffpgas[ffpga_n].write('a0_fd%i'%feng_input,struct.pack('>hh',fr_rate,fr_offset))  
        self.floggers[ffpga_n].debug("Wrote %4x to fringe_offset and %4x to fringe_rate register a0_fd%i."%(fr_offset,fr_rate,feng_input))
        #print 'Phase offset: %2.3f (%i), phase rate: %2.3f (%i).'%(fringe_phase,fr_offset,fringe_rate,fr_rate)

        #set the load time:
        self.ffpgas[ffpga_n].write_int('ld_time_lsw%i'%feng_input,(ld_mcnt&0xffffffff))
        self.ffpgas[ffpga_n].write_int('ld_time_msw%i'%feng_input,(ld_mcnt>>32)|(1<<31))
        self.ffpgas[ffpga_n].write_int('ld_time_msw%i'%feng_input,(ld_mcnt>>32)&0x7fffffff)

        if ld_check == False:
            return {
                'act_delay': act_delay,
                'act_fringe_offset': act_fringe_offset,
                'act_fringe_rate': act_fringe_rate,
                'act_delay_rate': act_delay_rate}

        #check that it loaded correctly:
        #wait 'till the time has elapsed
        sleep_time=self.time_from_mcnt(ld_mcnt) - self.time_from_mcnt(mcnt)
        #print 'waiting %2.3f seconds (now: %i, ldtime: %i)'%(sleep_time, self.time_from_mcnt(ld_mcnt),self.time_from_mcnt(mcnt))
        time.sleep(sleep_time)

        cnts=self.ffpgas[ffpga_n].read_uint('delay_tr_status%i'%feng_input)
        if (arm_cnt0 == (cnts>>16)): 
            if (cnts>>16)==0: 
                self.floggers[ffpga_n].error('Ant %i%s (Feng %i) appears to be held in master reset. Load failed.'%(ant,pol,feng_input))
                raise RuntimeError('Ant %i%s (Feng %i on %s) appears to be held in master reset. Load failed.'%(ant,pol,feng_input,self.fsrvs[ffpga_n]))
            else: 
                self.floggers[ffpga_n].error('Ant %i%s (Feng %i) did not arm. Load failed.'%(ant,pol,feng_input,))
                raise RuntimeError('Ant %i%s (Feng %i on %s) did not arm. Load failed.'%(ant,pol,feng_input,self.fsrvs[ffpga_n]))
        if (ld_cnt0 >= (cnts&0xffff)): 
            after_mcnt=self.mcnt_current_get(ant,pol) 
            #print 'before: %i, target: %i, after: %i'%(mcnt,ld_mcnt,after_mcnt)
            #print 'start: %10.3f, target: %10.3f, after: %10.3f'%(self.time_from_mcnt(mcnt),self.time_from_mcnt(ld_mcnt),self.time_from_mcnt(after_mcnt))
            if after_mcnt > ld_mcnt: 
                self.floggers[ffpga_n].error('We missed loading the registers by about %4.1f ms.'%((after_mcnt-ld_mcnt)/self.config['mcnt_scale_factor']*1000))
                raise RuntimeError('We missed loading the registers by about %4.1f ms.'%((after_mcnt-ld_mcnt)/self.config['mcnt_scale_factor']*1000))
            else: 
                self.floggers[ffpga_n].error('Ant %i%s (Feng %i) did not load correctly for an unknown reason.'%(ant,pol,feng_input))
                raise RuntimeError('Ant %i%s (Feng %i on %s) did not load correctly for an unknown reason.'%(ant,pol,feng_input,self.fsrvs[ffpga_n]))

        return {
            'act_delay': act_delay,
            'act_fringe_offset': act_fringe_offset,
            'act_fringe_rate': act_fringe_rate,
            'act_delay_rate': act_delay_rate}
        

    def time_from_mcnt(self,mcnt):
        """Returns the unix time UTC equivalent to the input MCNT. Does NOT account for wrapping MCNT."""
        return self.config['sync_time']+float(mcnt)/self.config['mcnt_scale_factor']
        
    def mcnt_from_time(self,time_seconds):
        """Returns the mcnt of the correlator from a given UTC system time (seconds since Unix Epoch). Accounts for wrapping mcnt."""
        return int((time_seconds - self.config['sync_time'])*self.config['mcnt_scale_factor'])%(2**self.config['mcnt_bits'])

        #print 'Current Feng mcnt: %16X, uptime: %16is, target mcnt: %16X (%16i)'%(current_mcnt,uptime,target_pkt_mcnt,target_pkt_mcnt)
        
    def time_from_pcnt(self,pcnt):
        """Returns the unix time UTC equivalent to the input packet timestamp. Does NOT account for wrapping pcnt."""
        return self.config['sync_time']+float(pcnt)/float(self.config['pcnt_scale_factor'])
        
    def pcnt_from_time(self,time_seconds):
        """Returns the packet timestamp from a given UTC system time (seconds since Unix Epoch). Accounts for wrapping pcnt."""
        return int((time_seconds - self.config['sync_time'])*self.config['pcnt_scale_factor'])%(2**self.config['pcnt_bits'])

    def time_from_spead(self,spead_time):
        """Returns the unix time UTC equivalent to the input packet timestamp. Does not account for wrapping timestamp counters."""
        return self.config['sync_time']+float(spead_time)/float(self.config['spead_timestamp_scale_factor'])
        
    def spead_timestamp_from_time(self,time_seconds):
        """Returns the packet timestamp from a given UTC system time (seconds since Unix Epoch). Accounts for wrapping timestamp."""
        return int((time_seconds - self.config['sync_time'])*self.config['spead_timestamp_scale_factor'])%(2**(self.config['spead_flavour'][1]))

    def acc_n_set(self,n_accs=-1,spead_update=True):
        """Set the Accumulation Length (in # of spectrum accumulations). If not specified, get the config from the config file."""
        if n_accs<0: n_accs=self.config['acc_len']
        n_accs = int(n_accs / self.config['xeng_acc_len'])
        self.xwrite_int_all('acc_len', n_accs)
        self.config.write('correlator','acc_len',n_accs)
        self.config.calc_int_time()
        self.syslogger.info("Set accumulation period to %2.2fs."%self.config['int_time'])
        self.vacc_sync() #this is needed in case we decrease the accumulation period on a new_acc transition where some vaccs would then be out of sync
        if spead_update: 
            self.spead_time_meta_issue()
            self.syslogger.info("SPEAD time metadata update sent.")

    def acc_time_set(self,acc_time=-1):
        """Set the accumulation time in seconds. If not specified, use the default from the config file."""
        if acc_time<0: acc_time=self.config['int_time']
        n_accs = acc_time * self.config['bandwidth']/self.config['n_chans'] 
        self.acc_n_set(n_accs=n_accs)

    def feng_brd_id_set(self):
        """Sets the F engine boards' antenna indices. (Numbers the board_id software register.)"""
        for f,fpga in enumerate(self.ffpgas):
            fpga.write_int('board_id', f)
        self.syslogger.info('F engine board IDs set ok.')

    def xeng_brd_id_set(self):
        """Sets the X engine boards' board_ids. This should not be necessary on newwer designs with XAUI links which extract this info from the 10GbE IP addresses."""
        for f,fpga in enumerate(self.xfpgas):
            fpga.write_int('board_id',f)
        self.syslogger.info('X engine board IDs set ok.')

    def get_ant_location(self, ant, pol='x'):
        " Returns the (ffpga_n,xfpga_n,fxaui_n,xxaui_n,feng_input) location for a given antenna. Ant is integer, as are all returns."
        #tested ok corr-0.5.0 2010-10-26
        if ant > self.config['n_ants']: 
            raise RuntimeError("There is no antenna %i in this design (total %i antennas)."%(ant,self.config['n_ants']))
        ffpga_n  = ant/self.config['f_per_fpga']
        fxaui_n  = ant/self.config['n_ants_per_xaui']%self.config['n_xaui_ports_per_ffpga']
        xfpga_n  = ant/self.config['n_ants_per_xaui']/self.config['n_xaui_ports_per_xfpga']
        xxaui_n  = ant/self.config['n_ants_per_xaui']%self.config['n_xaui_ports_per_xfpga']
        feng_input = ant%(self.config['f_per_fpga'])*self.config['n_pols'] + self.config['pol_map'][pol]
        return (ffpga_n,xfpga_n,fxaui_n,xxaui_n,feng_input)

    def config_roach_10gbe_ports(self):
        """Configures 10GbE ports on roach X engines for correlator data exchange using TGTAP."""
        if self.config['feng_out_type'] == '10gbe':
            self.fwrite_int_all('gbe_port', self.config['10gbe_port'])
            for fn,fpga in enumerate(self.ffpgas):
                for fc in range(self.config['n_xaui_ports_per_ffpga']):
                    start_addr=self.config['10gbe_ip']-(self.config['n_xaui_ports_per_ffpga'] * self.config['n_feng'])
                    start_port=self.config['10gbe_port']
                    mac,ip,port=self.get_roach_gbe_conf(start_addr,(fn*self.config['n_xaui_ports_per_ffpga']+fc),start_port)
                    fpga.tap_start('gbe%i'%fc,'gbe%i'%fc,mac,ip,port)
                    # THIS LINE SHOULD NOT BE REQUIRED WITH DAVE'S UPCOMING 10GBE CORE MODS
                    # Set the Xengines' starting IP address.
                    fpga.write_int('gbe_ip%i'%fc, self.config['10gbe_ip'])
        else:
            self.xwrite_int_all('gbe_port', self.config['10gbe_port'])

        for f,fpga in enumerate(self.xfpgas):
            for x in range(self.config['n_xaui_ports_per_xfpga']):
                start_addr=self.config['10gbe_ip']
                start_port=self.config['10gbe_port']
                mac,ip,port=self.get_roach_gbe_conf(start_addr,(f*self.config['n_xaui_ports_per_xfpga']+x),start_port)
                fpga.tap_start('gbe%i'%x,'gbe%i'%x,mac,ip,port)
                # THIS LINE SHOULD NOT BE REQUIRED WITH DAVE'S UPCOMING 10GBE CORE MODS
                # Assign an IP address to each XAUI port's associated 10GbE core.
                if self.config['feng_out_type'] == 'xaui':
                    fpga.write_int('gbe_ip%i'%x, ip)
        self.syslogger.info('All 10GbE cores configured.')
                        
#    def config_roach_10gbe_ports_static(self):
#        """STATICALLY configures 10GbE ports on roach X engines for correlator data exchange. Will not work with 10GbE output (we don't know the receiving computer's MAC)."""
#        arp_table=[(2**48)-1 for i in range(256)]
#
#        for f,fpga in enumerate(self.xfpgas):
#            for x in range(self.config['n_xaui_ports_per_xfpga']):
#                start_addr=self.config['10gbe_ip']
#                start_port=self.config['10gbe_port']
#                mac,ip,port=self.get_roach_gbe_conf(start_addr,(f*self.config['n_xaui_ports_per_xfpga']+x),start_port)
#                arp_table[ip%256]=mac
#
#        for f,fpga in enumerate(self.xfpgas):
#            for x in range(self.config['n_xaui_ports_per_xfpga']):
#                mac,ip,port=self.get_roach_gbe_conf(start_addr,(f*self.config['n_xaui_ports_per_xfpga']+x),start_port)
#                fpga.config_10gbe_core('gbe%i'%x,mac,ip,port,arp_table)
#                # THIS LINE SHOULD NOT BE REQUIRED WITH DAVE'S UPCOMING 10GBE CORE MODS
#                # Assign an IP address to each XAUI port's associated 10GbE core.
#                fpga.write_int('gbe_ip%i'%x, ip)

    def config_udp_output(self):
        """Configures the X engine 10GbE output cores. CURRENTLY DISABLED."""
        self.xwrite_int_all('gbe_out_ip',self.config['rx_udp_ip'])
        self.xwrite_int_all('gbe_out_port',self.config['rx_udp_port'])
        #self.xwrite_int_all('gbe_out_pkt_len',self.config['rx_pkt_payload_len']) now a compile-time option

        #Temporary for correlators with separate gbe core for output data:
        #for x in range(self.config['x_per_fpga']):
        #    for f,fpga in enumerate(self.xfpgas):
        #        ip_offset=self.config['10gbe_ip']+len(self.xfpgas)*self.config['x_per_fpga']
        #        mac,ip,port=self.get_roach_gbe_conf(ip_offset,(f*self.config['n_xaui_ports_per_xfpga']+x),self.config['rx_udp_port'])
        #        fpga.tap_start('gbe_out%i'%x,mac,ip,port)

    def enable_udp_output(self):
        """Just calls tx_start. Here for backwards compatibility."""
        self.tx_start()

    def disable_udp_output(self):
        """Just calls tx_stop. Here for backwards compatibility."""
        self.tx_stop()

    def deconfig_roach_10gbe_ports(self):
        """Stops tgtap drivers for the X (and possibly F) engines."""
        if self.config['feng_out_type'] == '10gbe':
            for f,fpga in enumerate(self.ffpgas):
                for x in range(self.config['n_xaui_ports_per_ffpga']):
                    fpga.tap_stop('gbe%i'%x)

        for f,fpga in enumerate(self.xfpgas):
            for x in range(self.config['n_xaui_ports_per_xfpga']):
                fpga.tap_stop('gbe%i'%x)

    def vacc_ld_stat_get(self):
        "grabs and decodes the VACC load status registers."
        rv={}
        for xf_n,srv in enumerate(self.xsrvs):
            rv[srv]={}
            for loc_xeng_n in range(self.config['x_per_fpga']):
                cnts=self.xfpgas[xf_n].read_uint('vacc_ld_status%i'%loc_xeng_n)
                rv[srv]['arm_cnt%i'%loc_xeng_n] = cnts>>16
                rv[srv]['ld_cnt%i'%loc_xeng_n] = cnts&0xffff
        return rv

    def vacc_sync(self,ld_time=-1):
        """Arms all vector accumulators to start accumulating at a given time. If no time is specified, after about a second from now."""
#rev: 2011-02-02 JRM:   added warning calc for leadtime. fewer time.time() calls.
        min_ld_time=0.5

        arm_cnt0={}
        ld_cnt0={}
        t_start=time.time()
        for loc_xeng_n in range(self.config['x_per_fpga']):
            for xf_n,srv in enumerate(self.xsrvs):
                xeng_n = loc_xeng_n * self.config['x_per_fpga'] + xf_n
                cnts=self.xfpgas[xf_n].read_uint('vacc_ld_status%i'%loc_xeng_n)
                arm_cnt0[xeng_n]=cnts>>16
                ld_cnt0[xeng_n]=cnts&0xffff
                if arm_cnt0[xeng_n] != ld_cnt0[xeng_n]: 
                    self.xloggers[xf_n].warning("VACC sync'ing: arm count and load count differ by %i, resetting VACCs."%(arm_cnt0[xeng_n] - ld_cnt0[xeng_n]))
                    self.rst_vaccs()

        pcnt=self.pcnt_current_get()

        #figure out the load time
        if ld_time < 0:
            #figure out the load-time pcnt:
            ld_pcnt=self.pcnt_from_time(t_start+min_ld_time)
        else:
            if (ld_time <= t_start+min_ld_time): 
                self.syslogger.error("Cannot load at a time in the past. Need at least %2.2f seconds leadtime."%(time.time()-t_start+min_ld_time))
                raise RuntimeError("Cannot load at a time in the past. Need at least %2.2f seconds leadtime."%(time.time()-t_start+min_ld_time))
            ld_pcnt=self.pcnt_from_time(ld_time)


        if (ld_pcnt <= pcnt): 
            self.syslogger.error("Error occurred. Cannot load at a time in the past.")
            raise RuntimeError("Error occurred. Cannot load at a time in the past.")

        if ld_pcnt > ((2**48)-1):
            self.syslogger.warning("Looks like the 48bit pcnt has wrapped.")
            ld_pcnt=ld_pcnt&0xffffffffffff


        #round to the nearest spectrum cycle. this is: n_ants*(n_chans_per_xeng)*(xeng_acc_len) clock cycles. pcnts themselves are rounded to nearest xeng_acc_len.
        #round_target=self.config['n_ants']*self.config['n_chans']/self.config['n_xeng']
        #However, hardware rounds to n_chans, irrespective of anything else (oops!).
        #ld_pcnt=(ld_pcnt/self.config['n_chans'])*self.config['n_chans']

        self.xwrite_int_all('vacc_time_msw',(ld_pcnt>>32)+(0<<31))
        self.xwrite_int_all('vacc_time_lsw',(ld_pcnt&0xffffffff))
        self.xwrite_int_all('vacc_time_msw',(ld_pcnt>>32)+(1<<31))
        self.xwrite_int_all('vacc_time_msw',(ld_pcnt>>32)+(0<<31))

        #wait 'till the time has elapsed
        time.sleep(self.time_from_pcnt(ld_pcnt) - self.time_from_pcnt(pcnt))
        time.sleep(0.2) #account for a crazy network latency
        after_pcnt=self.pcnt_current_get()
        #print 'waiting %2.3f seconds'%sleep_time

        for loc_xeng_n in range(self.config['x_per_fpga']):
            for xf_n,srv in enumerate(self.xsrvs):
                xeng_n = loc_xeng_n * self.config['x_per_fpga'] + xf_n
                cnts=self.xfpgas[xf_n].read_uint('vacc_ld_status%i'%loc_xeng_n)
                if ((cnts>>16)==0): 
                    self.xloggers[xf_n].error('VACC %i on %s appears to be held in reset.'%(loc_xeng_n,srv))
                    raise RuntimeError('VACC %i on %s appears to be held in reset.'%(loc_xeng_n,srv))
                if (arm_cnt0[xeng_n] == (cnts>>16)): 
                    self.xloggers[xf_n].error('VACC %i on %s did not arm.'%(loc_xeng_n,srv))
                    raise RuntimeError('VACC %i on %s did not arm.'%(loc_xeng_n,srv))
                if (ld_cnt0[xeng_n] >= (cnts&0xffff)): 
                    #print 'before: %i, target: %i, after: %i'%(pcnt,ld_pcnt,after_pcnt)
                    #print 'start: %10.3f, target: %10.3f, after: %10.3f'%(self.time_from_pcnt(pcnt),self.time_from_pcnt(ld_pcnt),self.time_from_pcnt(after_pcnt))
                    if after_pcnt > ld_pcnt: 
                        self.xloggers[xf_n].error('We missed loading the registers by about %4.1f ms.'%((self.time_from_pcnt(after_pcnt)-self.time_from_pcnt(ld_pcnt)) * 1000))
                        raise RuntimeError('We missed loading the registers by about %4.1f ms.'%((self.time_from_pcnt(after_pcnt)-self.time_from_pcnt(ld_pcnt)) * 1000))
                    else: raise RuntimeError('Xeng %i on %s did not load correctly for an unknown reason.'%(loc_xeng_n,srv))
                    

    def xsnap_all(self,dev_name,brams,man_trig=False,man_valid=False,wait_period=1,offset=-1,circular_capture=False):
        """Triggers and retrieves data from the a snap block device on all the X engines. Depending on the hardware capabilities, it can optionally capture with an offset. The actual captured length and starting offset is returned with the dictionary of data for each FPGA (useful if you've done a circular capture and can't calculate this yourself).\n
        \tdev_name: string, name of the snap block.\n
        \tman_trig: boolean, Trigger the snap block manually.\n
        \toffset: integer, wait this number of valids before beginning capture. Set to negative value if your hardware doesn't support this or the circular capture function.\n
        \tcircular_capture: boolean, Enable the circular capture function.\n
        \twait_period: integer, wait this number of seconds between triggering and trying to read-back the data.\n
        \tbrams: list, names of the bram components.\n
        \tRETURNS: dictionary with keywords: \n
        \t\tlengths: list of integers matching number of valids captured off each fpga.\n
        \t\toffset: optional (depending on snap block version) list of number of valids elapsed since last trigger on each fpga.
        \t\t{brams}: list of data from each fpga for corresponding bram.\n
        """
        #2011-02-03 JRM Added wait forever option
        if offset >= 0:
            #print 'Capturing from snap offset',offset
            self.xwrite_int_all(dev_name+'_trig_offset',offset)

        #print 'Triggering Capture...',
        self.xwrite_int_all(dev_name+'_ctrl',(0 + (man_trig<<1) + (man_valid<<2) + (circular_capture<<3)))
        self.xwrite_int_all(dev_name+'_ctrl',(1 + (man_trig<<1) + (man_valid<<2) + (circular_capture<<3)))

        done=False
        start_time=time.time()
        while not (done and (offset!=0 or circular_capture)) and ((time.time()-start_time)<wait_period or (wait_period<0)): 
            addr      = self.xread_uint_all(dev_name+'_addr')
            done_list = [not bool(i & 0x80000000) for i in addr]
            if (done_list == [True for i in self.xsrvs]): done=True
        bram_sizes=[i&0x7fffffff for i in self.xread_uint_all(dev_name+'_addr')]
        bram_dmp={'lengths':numpy.add(bram_sizes,1)}
        bram_dmp['offsets']=[0 for f in self.xfpgas]
        #print 'Addr+1:',bram_dmp['lengths']
        for f,fpga in enumerate(self.xfpgas):
            if (bram_sizes[f] != fpga.read_uint(dev_name+'_addr')&0x7fffffff) or bram_sizes[f]==0:
                #if address is still changing, then the snap block didn't finish capturing. we return empty.  
                print "Looks like snap block on %s didn't finish."%self.xsrvs[f]
                bram_dmp['lengths'][f]=0
                bram_dmp['offsets'][f]=0
                bram_sizes[f]=0

        if (circular_capture or (offset>=0)) and not man_trig:
            bram_dmp['offsets']=numpy.subtract(numpy.add(self.xread_uint_all(dev_name+'_tr_en_cnt'),offset),bram_sizes)
            #print 'Valids since offset trig:',self.read_uint_all(dev_name+'_tr_en_cnt')
            #print 'offsets:',bram_dmp['offsets']
        else: bram_dmp['offsets']=[0 for f in self.xfpgas]
    
        for f,fpga in enumerate(self.xfpgas):
            if (bram_dmp['offsets'][f] < 0):  
                self.xloggers[f].error('SNAP block hardware or logic failure happened.')
                raise RuntimeError('SNAP block hardware or logic failure happened.')
                bram_dmp['lengths'][f]=0
                bram_dmp['offsets'][f]=0
                bram_sizes[f]=0

        for b,bram in enumerate(brams):
            bram_path = dev_name+'_'+bram
            bram_dmp[bram]=[]
            for f,fpga in enumerate(self.xfpgas):
                if (bram_sizes[f] == 0): 
                    bram_dmp[bram].append([])
                else: 
                    bram_dmp[bram].append(fpga.read(bram_path,(bram_sizes[f]+1)*4))
        return bram_dmp

    def fsnap_all(self,dev_name,brams,man_trig=False,man_valid=False,wait_period=1,offset=-1,circular_capture=False):
        """Triggers and retrieves data from the a snap block device on all the F engines. Depending on the hardware capabilities, it can optionally capture with an offset. The actual captured length and starting offset is returned with the dictionary of data for each FPGA (useful if you've done a circular capture and can't calculate this yourself).\n
        \tdev_name: string, name of the snap block.\n
        \tman_trig: boolean, Trigger the snap block manually.\n
        \toffset: integer, wait this number of valids before beginning capture. Set to zero if your hardware doesn't support this or the circular capture function. Set to negative if you've got a modern snap block with end-of-capture detect but actually want to start at offset zero.\n
        \tcircular_capture: boolean, Enable the circular capture function.\n
        \twait_period: integer, wait this number of seconds between triggering and trying to read-back the data. Make it negative to wait forever.\n
        \tbrams: list, names of the bram components.\n
        \tRETURNS: dictionary with keywords: \n
        \t\tlengths: list of integers matching number of valids captured off each fpga.\n
        \t\toffset: optional (depending on snap block version) list of number of valids elapsed since last trigger on each fpga.
        \t\t{brams}: list of data from each fpga for corresponding bram.\n
        """
        #2011-02-03 JRM Added wait forever option
        if offset >= 0:
            self.fwrite_int_all(dev_name+'_trig_offset',offset)
            #print 'Capturing from snap offset %i'%offset

        #print 'Triggering Capture...',
        self.fwrite_int_all(dev_name+'_ctrl',(0 + (man_trig<<1) + (man_valid<<2) + (circular_capture<<3)))
        self.fwrite_int_all(dev_name+'_ctrl',(1 + (man_trig<<1) + (man_valid<<2) + (circular_capture<<3)))

        done=False
        start_time=time.time()
        while not (done and (offset!=0 or circular_capture)) and ((time.time()-start_time)<wait_period or (wait_period < 0)):
            addr      = self.fread_uint_all(dev_name+'_addr')
            done_list = [not bool(i & 0x80000000) for i in addr]
            if (done_list == [True for i in self.fsrvs]): done=True
        bram_sizes=[i&0x7fffffff for i in self.fread_uint_all(dev_name+'_addr')]
        bram_dmp={'lengths':numpy.add(bram_sizes,1)}
        bram_dmp['offsets']=[0 for f in self.ffpgas]
        #print 'Addr+1:',bram_dmp['lengths']
        for f,fpga in enumerate(self.ffpgas):
            if (bram_sizes[f] != fpga.read_uint(dev_name+'_addr')&0x7fffffff) or bram_sizes[f]==0:
                #if address is still changing, then the snap block didn't finish capturing. we return empty.  
                print "Looks like snap block on %s didn't finish."%self.fsrvs[f]
                bram_dmp['lengths'][f]=0
                bram_dmp['offsets'][f]=0
                bram_sizes[f]=0

        if (circular_capture or (offset>=0)) and not man_trig:
            bram_dmp['offsets']=numpy.subtract(numpy.add(self.fread_uint_all(dev_name+'_tr_en_cnt'),offset),bram_sizes)
            #print 'Valids since offset trig:',self.read_uint_all(dev_name+'_tr_en_cnt')
            #print 'offsets:',bram_dmp['offsets']
        else: bram_dmp['offsets']=[0 for f in self.ffpgas]
    
        for f,fpga in enumerate(self.ffpgas):
            if (bram_dmp['offsets'][f] < 0):  
                self.floggers[f].error('SNAP block hardware or logic failure happened.')
                raise RuntimeError('SNAP block hardware or logic failure happened.')
                bram_dmp['lengths'][f]=0
                bram_dmp['offsets'][f]=0
                bram_sizes[f]=0

        for b,bram in enumerate(brams):
            bram_path = dev_name+'_'+bram
            bram_dmp[bram]=[]
            for f,fpga in enumerate(self.ffpgas):
                if (bram_sizes[f] == 0): 
                    bram_dmp[bram].append([])
                else: 
                    bram_dmp[bram].append(fpga.read(bram_path,(bram_sizes[f]+1)*4))
        return bram_dmp

    def check_xaui_sync(self):
        """Checks if all F engines are in sync by examining mcnts at sync of incomming XAUI streams. \n
        If this test passes, it does not gaurantee that the system is indeed sync'd,
         merely that the F engines were reset between the same 1PPS pulses.
        Returns boolean true/false if system is in sync.
        """
        if self.config['feng_out_type'] != 'xaui': raise RuntimeError("According to your config file, you don't have any XAUI cables connected to your F engines!")
        max_mcnt_difference=4
        mcnts=dict()
        mcnts_list=[]
        mcnt_tot=0
        rv=True

        for ant in range(0,self.config['n_ants'],self.config['n_ants_per_xaui']):
            f = ant / self.config['n_ants_per_xaui'] / self.config['n_xaui_ports_per_xfpga']
            x = ant / self.config['n_ants_per_xaui'] % self.config['n_xaui_ports_per_xfpga']

            n_xaui=f*self.config['n_xaui_ports_per_xfpga']+x
            #print 'Checking antenna %i on fpga %i, xaui %i. Entry %i.'%(ant,f,x,n_xaui)
            mcnts[n_xaui]=dict()
            mcnts[n_xaui]['mcnt'] =self.xfpgas[f].read_uint('xaui_sync_mcnt%i'%x)
            mcnts_list.append(mcnts[n_xaui]['mcnt'])

        mcnts['mode']=statsmode(mcnts_list)
        if mcnts['mode']==0:
            self.syslogger.error("Too many XAUI links are receiving no data. Unable to produce a reliable mcnt result.")
            raise RuntimeError("Too many XAUI links are receiving no data. Unable to produce a reliable result.")
        mcnts['modalmean']=numpy.mean(mcnts['mode'])

#        mcnts:['mean']=stats.mean(mcnts_list)
#        mcnts['median']=stats.median(mcnts_list)
#        print 'mean: %i, median: %i, modal mean: %i mode:'%(mcnts['mean'],mcnts['median'],mcnts['modalmean']),mcnts['mode']

        for ant in range(0,self.config['n_ants'],self.config['n_ants_per_xaui']):
            f = ant / self.config['n_ants_per_xaui'] / self.config['n_xaui_ports_per_xfpga']
            x = ant / self.config['n_ants_per_xaui'] % self.config['n_xaui_ports_per_xfpga']
            n_xaui=f*self.config['n_xaui_ports_per_xfpga']+x
            if mcnts[n_xaui]['mcnt']>(mcnts['modalmean']+max_mcnt_difference) or mcnts[n_xaui]['mcnt'] < (mcnts['modalmean']-max_mcnt_difference):
                rv=False
                self.syslogger.error('Sync check failed on %s, port %i with error of %i.'%(self.xservers[f],x,mcnts[n_xaui]['mcnt']-mcnts['modalmean']))
        return rv

    def rf_gain_set(self,ant,pol,gain=None):
        """Enables the RF switch and configures the RF attenuators on KATADC boards. pol is ['x'|'y']. \n
        \t KATADC's valid range is -11.5 to 20dB. \n
        \t If no gain is specified, use the defaults from the config file."""
        #tested ok corr-0.5.0 2010-07-19
        #RF switch is in MSb.
        if self.config['adc_type'] != 'katadc' : raise RuntimeError("Unsupported ADC type of %s. Only katadc is supported."%self.config['adc_type'])
        ffpga_n,xfpga_n,fxaui_n,xxaui_n,feng_input = self.get_ant_location(ant,pol)
        if gain == None:
            gain = self.config['rf_gain_%i%c'%(ant,pol)] 
        if gain > 20 or gain < -11.5:
             self.floggers[ffpga_n].error("Invalid gain setting of %i. Valid range for KATADC is -11.5 to +20")
             raise RuntimeError("Invalid gain setting of %i. Valid range for KATADC is -11.5 to +20")
        self.ffpgas[ffpga_n].write_int('adc_ctrl%i'%feng_input,(1<<31)+int((20-gain)*2))
        self.config.write('equalisation','rf_gain_%i%c'%(ant,pol),gain)
        self.floggers[ffpga_n].info("KATADC %i RF gain set to %2.1f."%(feng_input,round(gain*2)/2))

    def rf_status_get(self,ant,pol):
        """Grabs the current value of the RF attenuators and RF switch state for KATADC boards. return (enabled,gain in dB) pol is ['x'|'y']"""
        #tested ok corr-0.5.0 2010-07-19
        #RF switch is in MSb.
        if self.config['adc_type'] != 'katadc' : raise RuntimeError("Unsupported ADC type of %s. Only katadc is supported."%self.config['adc_type'])
        ffpga_n,xfpga_n,fxaui_n,xxaui_n,feng_input = self.get_ant_location(ant,pol)
        value = self.ffpgas[ffpga_n].read_uint('adc_ctrl%i'%feng_input)
        return (bool(value&(1<<31)),20.0-(value&0x3f)*0.5)

    def rf_status_get_all(self):
        """Grabs the current status of the RF chain on all KATADC boards."""
        #RF switch is in MSb.
        #tested ok corr-0.5.0 2010-07-19
        if self.config['adc_type'] != 'katadc' : raise RuntimeError("Unsupported ADC type of %s. Only katadc is supported."%self.config['adc_type'])
        rv={}
        for ant in range(self.config['n_ants']):
            for pol in self.config['pols']:
                rv[(ant,pol)]=self.rf_status_get(ant,pol)
        return rv

    def rf_gain_set_all(self,gain=None):
        """Sets the RF gain configuration of all inputs to "gain". If no level is given, use the defaults from the config file."""
        #tested ok corr-0.5.0 2010-07-19
        if self.config['adc_type'] != 'katadc' : raise RuntimeError("Unsupported ADC type of %s. Only katadc is supported."%self.config['adc_type'])
        for ant in range(self.config['n_ants']):
            for pol in self.config['pols']:
                self.rf_gain_set(ant,pol,gain)
        self.syslogger.info('Set RF gains on all katADCs.')

    def rf_disable(self,ant,pol):
        """Disable the RF switch on KATADC boards. pol is ['x'|'y']"""
        #tested ok corr-0.5.0 2010-08-07
        #RF switch is in MSb.
        if self.config['adc_type'] != 'katadc' : raise RuntimeError("Unsupported ADC type of %s. Only katadc is supported at this time."%self.config['adc_type'])
        ffpga_n,xfpga_n,fxaui_n,xxaui_n,feng_input = self.get_ant_location(ant,pol)
        self.ffpgas[ffpga_n].write_int('adc_ctrl%i'%feng_input,self.ffpgas[ffpga_n].read_uint('adc_ctrl%i'%feng_input)&0x7fffffff)

    def rf_enable(self,ant,pol):
        """Enable the RF switch on KATADC boards. pol is ['x'|'y']"""
        #tested ok corr-0.5.0 2010-08-07
        #RF switch is in MSb.
        if self.config['adc_type'] != 'katadc' : raise RuntimeError("Unsupported ADC type of %s. Only katadc is supported at this time."%self.config['adc_type'])
        ffpga_n,xfpga_n,fxaui_n,xxaui_n,feng_input = self.get_ant_location(ant,pol)
        self.ffpgas[ffpga_n].write_int('adc_ctrl%i'%feng_input,self.ffpgas[ffpga_n].read_uint('adc_ctrl%i'%feng_input)|0x80000000)

    def eq_set_all(self,init_poly=[],init_coeffs=[]):
        """Initialise all connected Fengines' EQs to given polynomial. If no polynomial or coefficients are given, use defaults from config file."""
        #tested ok corr-0.5.0 2010-08-07
        for ant in range(self.config['n_ants']):
            for pol in self.config['pols']:
                self.eq_spectrum_set(ant=ant,pol=pol,init_coeffs=init_coeffs,init_poly=init_poly)
        self.syslogger.info('Set all EQ gains on all Fengs.')

    def eq_default_get(self,ant,pol):
        "Fetches the default equalisation configuration from the config file and returns a list of the coefficients for a given input. pol is ['x'|'y']" 
        #tested ok corr-0.5.0 2010-08-07
        n_coeffs = self.config['n_chans']/self.config['eq_decimation']

        if self.config['eq_default'] == 'coeffs':
            equalisation = self.config['eq_coeffs_%i%c'%(ant,pol)]

        elif self.config['eq_default'] == 'poly':
            poly = self.config['eq_poly_%i%c'%(ant,pol)]
            equalisation = numpy.polyval(poly, range(self.config['n_chans']))[self.config['eq_decimation']/2::self.config['eq_decimation']]
            if self.config['eq_type']=='complex':
                equalisation = [eq+0*1j for eq in equalisation]
                
        if len(equalisation) != n_coeffs: raise RuntimeError("Something's wrong. I have %i eq coefficients when I should have %i."%(len(equalisation),n_coeffs))
        return equalisation

    #def eq_tostr(self,poly)
    #    for term,coeff in enumerate(equalisation):
    #        print '''Retrieved default EQ (%s) for antenna %i%c: '''%(ant,pol,self.config['eq_default']),
    #        if term==(len(coeffs)-1): print '%i...'%(coeff),
    #        else: print '%ix^%i +'%(coeff,len(coeffs)-term-1),
    #        sys.stdout.flush()
    #    print ''

    def eq_spectrum_get(self,ant,pol):
        """Retrieves the equaliser settings currently programmed in an F engine for the given antenna,polarisation. Assumes equaliser of 16 bits. Returns an array of length n_chans."""
        
        #tested ok corr-0.5.0 2010-08-07
        ffpga_n,xfpga_n,fxaui_n,xxaui_n,feng_input = self.get_ant_location(ant,pol)
        register_name='eq%i'%(feng_input)
        n_coeffs = self.config['n_chans']/self.config['eq_decimation']

        if self.config['eq_type'] == 'scalar':
            bd=self.ffpgas[ffpga_n].read(register_name,n_coeffs*2)
            coeffs=numpy.array(struct.unpack('>%ih'%n_coeffs,bd))
            nacexp=(numpy.reshape(coeffs,(n_coeffs,1))*numpy.ones((1,self.config['eq_decimation']))).reshape(self.config['n_chans'])
            return nacexp
            
        elif self.config['eq_type'] == 'complex':
            bd=self.ffpgas[ffpga_n].read(register_name,n_coeffs*4)
            coeffs=struct.unpack('>%ih'%(n_coeffs*2),bd)
            na=numpy.array(coeffs,dtype=numpy.float64)
            nac=na.view(dtype=numpy.complex128)
            nacexp=(numpy.reshape(nac,(n_coeffs,1))*numpy.ones((1,self.config['eq_decimation']))).reshape(self.config['n_chans'])
            return nacexp
            
        else: 
            self.syslogger.error("Unable to interpret eq_type from config file. Expecting scalar or complex.")
            raise RuntimeError("Unable to interpret eq_type from config file. Expecting scalar or complex.")

    def eq_spectrum_set(self,ant,pol,init_coeffs=[],init_poly=[]):
        """Set a given antenna and polarisation equaliser to given co-efficients. pol is 'x' or 'y'. ant is integer in range n_ants. Assumes equaliser of 16 bits. init_coeffs is list of length n_chans/decimation_factor."""
        #tested ok corr-0.5.0 2010-08-07
        ffpga_n,xfpga_n,fxaui_n,xxaui_n,feng_input = self.get_ant_location(ant,pol)
        fpga=self.ffpgas[ffpga_n]
        pol_n = self.config['pol_map'][pol]
        register_name='eq%i'%(feng_input)
        n_coeffs = self.config['n_chans']/self.config['eq_decimation']

        if init_coeffs == [] and init_poly == []: 
            coeffs = self.eq_default_get(ant,pol)
        elif len(init_coeffs) == n_coeffs:
            coeffs = init_coeffs
        elif len(init_coeffs)>0: 
            raise RuntimeError ('You specified %i coefficients, but there are %i EQ coefficients in this design.'%(len(init_coeffs),n_coeffs))
        else:
            coeffs = numpy.polyval(init_poly, range(self.config['n_chans']))[self.config['eq_decimation']/2::self.config['eq_decimation']]
        
        if self.config['eq_type'] == 'scalar':
            coeffs    = numpy.real(coeffs) 
            if numpy.max(coeffs) > ((2**16)-1) or numpy.min(coeffs)<0: 
                self.floggers[ffpga_n].error("Sorry, your EQ settings are out of range!")
                raise RuntimeError("Sorry, your EQ settings are out of range!")
            coeff_str = struct.pack('>%iH'%n_coeffs,coeffs)
        elif self.config['eq_type'] == 'complex':
            if numpy.max(coeffs) > ((2**15)-1) or numpy.min(coeffs)<-((2**15)-1): 
                self.floggers[ffpga_n].error("Sorry, your EQ settings are out of range!")
                raise RuntimeError("Sorry, your EQ settings are out of range!")
            coeffs    = numpy.array(coeffs,dtype=numpy.complex128)
            coeff_str = struct.pack('>%ih'%(2*n_coeffs),*coeffs.view(dtype=numpy.float64))
        else: 
            self.floggers[ffpga_n].error("Sorry, your EQ type is not supported. Expecting scalar or complex.")
            raise RuntimeError('EQ type not supported.')

        self.floggers[ffpga_n].info('Writing new EQ coefficient values to config file...')
        self.config.write('equalisation','eq_coeffs_%i%c'%(ant,pol),str(coeffs.tolist()))
        
        for term,coeff in enumerate(coeffs):
            self.floggers[ffpga_n].debug('''Initialising EQ for antenna %i%c, input %i on %s (register %s)'s index %i to %s.'''%(ant,pol,feng_input,self.fsrvs[ffpga_n],register_name,term,str(coeff)))

        fpga.write(register_name,coeff_str)

    def adc_amplitudes_get(self,ants=[]):
        """Gets the ADC RMS amplitudes from the F engines. If no antennas are specified, return all."""
        if ants == []:
            ants = range(self.config['n_ants'])
        rv = {}
        for ant in ants:
            for pol in self.config['pols']:
                ffpga_n,xfpga_n,fxaui_n,xxaui_n,feng_input = self.get_ant_location(ant,pol)
                rv[(ant,pol)]={}
                rv[(ant,pol)]['raw']=self.ffpgas[ffpga_n].read_uint('adc_sum_sq%i'%(feng_input))
                #here we have adc_bits -1 because the device outputs signed values in range -1 to +1, but rms range is 0 to 1(ok, sqrt(2)) so one bit is "wasted" on sign indication.
                rv[(ant,pol)]['rms_raw']=numpy.sqrt(rv[(ant,pol)]['raw']/float(self.config['adc_levels_acc_len']))/(2**(self.config['adc_bits']-1))
                if rv[(ant,pol)]['rms_raw'] == 0: rv[(ant,pol)]['bits']=0
                else: rv[(ant,pol)]['bits'] = numpy.log2(rv[(ant,pol)]['rms_raw'] * (2**(self.config['adc_bits'])))
                if rv[(ant,pol)]['bits'] < 0: rv[(ant,pol)]['bits']=0
                rv[(ant,pol)]['rms_db'] = 10*numpy.log10(rv[(ant,pol)]['raw']/float(self.config['adc_levels_acc_len'])) + self.config['adc_db_offset']# - self.rf_status_get(ant,pol)[1]
        return rv

    def spead_static_meta_issue(self):
        """ Issues the SPEAD metadata packets containing the payload and options descriptors and unpack sequences."""
        import spead
        #tested ok corr-0.5.0 2010-08-07
        tx=spead.Transmitter(spead.TransportUDPtx(self.config['rx_meta_ip_str'],self.config['rx_udp_port']))
        ig=spead.ItemGroup()

        ig.add_item(name="adc_clk",id=0x1007,
            description="Clock rate of ADC (samples per second).",
            shape=[],fmt=spead.mkfmt(('u',64)),
            init_val=self.config['adc_clk'])

        ig.add_item(name="n_bls",id=0x1008,
            description="The total number of baselines in the data product.",
            shape=[],fmt=spead.mkfmt(('u',spead.ADDRSIZE)),
            init_val=self.config['n_bls'])

        ig.add_item(name="n_chans",id=0x1009,
            description="The total number of frequency channels present in any integration.",
            shape=[], fmt=spead.mkfmt(('u',spead.ADDRSIZE)),
            init_val=self.config['n_chans'])

        ig.add_item(name="n_ants",id=0x100A,
            description="The total number of dual-pol antennas in the system.",
            shape=[],fmt=spead.mkfmt(('u',spead.ADDRSIZE)),
            init_val=self.config['n_ants'])

        ig.add_item(name="n_xengs",id=0x100B,
            description="The total number of X engines in the system.",
            shape=[],fmt=spead.mkfmt(('u',spead.ADDRSIZE)),
            init_val=self.config['n_xeng'])

        ig.add_item(name="bls_ordering",id=0x100C,
            description="The output ordering of the baselines from each X engine. Packed as a pair of unsigned integers, ant1,ant2 where ant1 < ant2.",
            shape=[self.config['n_bls'],2],fmt=spead.mkfmt(('u',16)),
            init_val=[[bl[0],bl[1]] for bl in self.get_bl_order()])

        ig.add_item(name="crosspol_ordering",id=0x100D,
            description="The output ordering of the cross-pol terms. Packed as a pair of characters, pol1,pol2.",
            shape=[self.config['n_stokes'],self.config['n_pols']],fmt=spead.mkfmt(('c',8)),
            init_val=[[bl[0],bl[1]] for bl in self.get_crosspol_order()])

        ig.add_item(name="center_freq",id=0x1011,
            description="The center frequency of the DBE in Hz, 64-bit IEEE floating-point number.",
            shape=[],fmt=spead.mkfmt(('f',64)),
            init_val=self.config['center_freq'])

        ig.add_item(name="bandwidth",id=0x1013,
            description="The analogue bandwidth of the digitally processed signal in Hz.",
            shape=[],fmt=spead.mkfmt(('f',64)),
            init_val=self.config['bandwidth'])

        
        #1015/1016 are taken (see time_metadata_issue below)

        ig.add_item(name="fft_shift",id=0x101E,
            description="The FFT bitshift pattern. F-engine correlator internals.",
            shape=[],fmt=spead.mkfmt(('u',spead.ADDRSIZE)),
            init_val=self.config['fft_shift'])

        ig.add_item(name="xeng_acc_len",id=0x101F,
            description="Number of spectra accumulated inside X engine. Determines minimum integration time and user-configurable integration time stepsize. X-engine correlator internals.",
            shape=[],fmt=spead.mkfmt(('u',spead.ADDRSIZE)),
            init_val=self.config['xeng_acc_len'])

        ig.add_item(name="requant_bits",id=0x1020,
            description="Number of bits after requantisation in the F engines (post FFT and any phasing stages).",
            shape=[],fmt=spead.mkfmt(('u',spead.ADDRSIZE)),
            init_val=self.config['feng_bits'])

        ig.add_item(name="feng_pkt_len",id=0x1021,
            description="Payload size of 10GbE packet exchange between F and X engines in 64 bit words. Usually equal to the number of spectra accumulated inside X engine. F-engine correlator internals.",
            shape=[],fmt=spead.mkfmt(('u',spead.ADDRSIZE)),
            init_val=self.config['10gbe_pkt_len'])

        ig.add_item(name="rx_udp_port",id=0x1022,
            description="Destination UDP port for X engine output.",
            shape=[],fmt=spead.mkfmt(('u',spead.ADDRSIZE)),
            init_val=self.config['rx_udp_port'])

        ig.add_item(name="feng_udp_port",id=0x1023,
            description="Destination UDP port for F engine data exchange.",
            shape=[],fmt=spead.mkfmt(('u',spead.ADDRSIZE)),
            init_val=self.config['10gbe_port'])

        ig.add_item(name="rx_udp_ip_str",id=0x1024,
            description="Destination IP address for X engine output UDP packets.",
            shape=[-1],fmt=spead.STR_FMT,
            init_val=self.config['rx_udp_ip_str'])

        ig.add_item(name="feng_start_ip",id=0x1025,
            description="F engine starting IP address.",
            shape=[],fmt=spead.mkfmt(('u',spead.ADDRSIZE)),
            init_val=self.config['10gbe_ip'])

        ig.add_item(name="xeng_rate",id=0x1026,
            description="Target clock rate of processing engines (xeng).",
            shape=[],fmt=spead.mkfmt(('u',spead.ADDRSIZE)),
            init_val=self.config['xeng_clk'])

        ig.add_item(name="n_stokes",id=0x1040,
            description="Number of Stokes parameters in output.",
            shape=[],fmt=spead.mkfmt(('u',spead.ADDRSIZE)),
            init_val=self.config['n_stokes'])

        ig.add_item(name="x_per_fpga",id=0x1041,
            description="Number of X engines per FPGA.",
            shape=[],fmt=spead.mkfmt(('u',spead.ADDRSIZE)),
            init_val=self.config['x_per_fpga'])

        ig.add_item(name="n_ants_per_xaui",id=0x1042,
            description="Number of antennas' data per XAUI link.",
            shape=[],fmt=spead.mkfmt(('u',spead.ADDRSIZE)),
            init_val=self.config['n_ants_per_xaui'])

        ig.add_item(name="ddc_mix_freq",id=0x1043,
            description="Digital downconverter mixing freqency as a fraction of the ADC sampling frequency. eg: 0.25. Set to zero if no DDC is present.",
            shape=[],fmt=spead.mkfmt(('f',64)),
            init_val=self.config['ddc_mix_freq'])

        ig.add_item(name="ddc_decimation",id=0x1044,
            description="Frequency decimation of the digital downconverter (determines how much bandwidth is processed) eg: 4",
            shape=[],fmt=spead.mkfmt(('u',spead.ADDRSIZE)),
            init_val=self.config['ddc_decimation'])

        ig.add_item(name="adc_bits",id=0x1045,
            description="ADC quantisation (bits).",
            shape=[],fmt=spead.mkfmt(('u',spead.ADDRSIZE)),
            init_val=self.config['adc_bits'])

        ig.add_item(name="xeng_out_bits_per_sample",id=0x1048,
            description="The number of bits per value of the xeng accumulator output. Note this is for a single value, not the combined complex size.",
            shape=[],fmt=spead.mkfmt(('u',spead.ADDRSIZE)),
            init_val=self.config['xeng_sample_bits'])

        tx.send_heap(ig.get_heap())
        self.syslogger.info("Issued misc SPEAD metadata to %s:%i."%(self.config['rx_meta_ip_str'],self.config['rx_udp_port']))

    def spead_time_meta_issue(self):
        """Issues a SPEAD packet to notify the receiver that we've resync'd the system, acc len has changed etc."""
        #tested ok corr-0.5.0 2010-08-07
        import spead
        tx=spead.Transmitter(spead.TransportUDPtx(self.config['rx_meta_ip_str'],self.config['rx_udp_port']))
        ig=spead.ItemGroup()

        ig.add_item(name="n_accs",id=0x1015,
            description="The number of spectra that are accumulated per integration.",
            shape=[],fmt=spead.mkfmt(('u',spead.ADDRSIZE)),
            init_val=self.config['n_accs'])

        ig.add_item(name="int_time",id=0x1016,
            description="Approximate (it's a float!) integration time per accumulation in seconds.",
            shape=[],fmt=spead.mkfmt(('f',64)),
            init_val=self.config['int_time'])

        ig.add_item(name='sync_time',id=0x1027,
            description="Time at which the system was last synchronised (armed and triggered by a 1PPS) in seconds since the Unix Epoch.",
            shape=[],fmt=spead.mkfmt(('u',spead.ADDRSIZE)),
            init_val=self.config['sync_time'])

        ig.add_item(name="scale_factor_timestamp",id=0x1046,
            description="Timestamp scaling factor. Divide the SPEAD data packet timestamp by this number to get back to seconds since last sync.",
            shape=[],fmt=spead.mkfmt(('f',64)),
            init_val=self.config['spead_timestamp_scale_factor'])


        tx.send_heap(ig.get_heap())
        self.syslogger.info("Issued SPEAD timing metadata to %s:%i."%(self.config['rx_meta_ip_str'],self.config['rx_udp_port']))

    def spead_eq_meta_issue(self):
        """Issues a SPEAD heap for the RF gain and EQ settings."""
        import spead
        tx=spead.Transmitter(spead.TransportUDPtx(self.config['rx_meta_ip_str'],self.config['rx_udp_port']))
        ig=spead.ItemGroup()

        
        if self.config['adc_type'] == 'katadc':
            for ant in range(self.config['n_ants']):
                for pn,pol in enumerate(self.config['pols']):
                    ig.add_item(name="rf_gain_%i%c"%(ant,pol),id=0x1200+ant*self.config['n_pols']+pn,
                        description="The analogue RF gain applied at the ADC for input %i%c in dB."%(ant,pol),
                        shape=[],fmt=spead.mkfmt(('f',64)),
                        init_val=self.config['rf_gain_%i%c'%(ant,pol)])

        if self.config['eq_type']=='scalar':
            for ant in range(self.config['n_ants']):
                for pn,pol in enumerate(self.config['pols']):
                    ig.add_item(name="eq_coef_%i%c"%(ant,pol),id=0x1400+ant*self.config['n_pols']+pn,
                        description="The unitless per-channel digital amplitude scaling factors implemented prior to requantisation, post-FFT, for input %i%c."%(ant,pol),
                        init_val=self.eq_spectrum_get(ant,pol))

        elif self.config['eq_type']=='complex':
            for ant in range(self.config['n_ants']):
                for pn,pol in enumerate(self.config['pols']):
                    ig.add_item(name="eq_coef_%i%c"%(ant,pol),id=0x1400+ant*self.config['n_pols']+pn,
                        description="The unitless per-channel digital scaling factors implemented prior to requantisation, post-FFT, for input %i%c. Complex number real,imag 32 bit integers."%(ant,pol),
                        shape=[self.config['n_chans'],2],fmt=spead.mkfmt(('u',32)),
                        init_val=[[numpy.real(coeff),numpy.imag(coeff)] for coeff in self.eq_spectrum_get(ant,pol)])

        else: raise RuntimeError("I don't know how to deal with your EQ type.")

        tx.send_heap(ig.get_heap())
        self.syslogger.info("Issued SPEAD EQ metadata to %s:%i."%(self.config['rx_meta_ip_str'],self.config['rx_udp_port']))


    def spead_data_descriptor_issue(self):
        """ Issues the SPEAD data descriptors for the HW 10GbE output, to enable receivers to decode the data."""
        #tested ok corr-0.5.0 2010-08-07
        import spead
        tx=spead.Transmitter(spead.TransportUDPtx(self.config['rx_meta_ip_str'],self.config['rx_udp_port']))
        ig=spead.ItemGroup()

        if self.config['xeng_sample_bits'] != 32: raise RuntimeError("Invalid bitwidth of X engine output. You specified %i, but I'm hardcoded for 32."%self.config['xeng_sample_bits'])


        if self.config['xeng_format'] == 'cont':
            ig.add_item(name=('timestamp'), id=0x1600,
                description='Timestamp of start of this integration. uint counting multiples of ADC samples since last sync (sync_time, id=0x1027). Divide this number by timestamp_scale (id=0x1046) to get back to seconds since last sync when this integration was actually started. Note that the receiver will need to figure out the centre timestamp of the accumulation (eg, by adding half of int_time, id 0x1016).',
                shape=[], fmt=spead.mkfmt(('u',spead.ADDRSIZE)),
                init_val=0)

            ig.add_item(name=("xeng_raw"),id=0x1800,
                description="Raw data for %i xengines in the system. This item represents a full spectrum (all frequency channels) assembled from lowest frequency to highest frequency. Each frequency channel contains the data for all baselines (n_bls given by SPEAD ID 0x100B). For a given baseline, -SPEAD ID 0x1040- stokes parameters are calculated (nominally 4 since xengines are natively dual-polarisation; software remapping is required for single-baseline designs). Each stokes parameter consists of a complex number (two real and imaginary unsigned integers)."%(self.config['n_xeng']),
            ndarray=(numpy.dtype(numpy.int32),(self.config['n_chans'],self.config['n_bls'],self.config['n_stokes'],2)))


        elif self.config['xeng_format'] =='iter':
            for x in range(self.config['n_xeng']):

                ig.add_item(name=('timestamp%i'%x), id=0x1600+x,
                    description='Timestamp of start of this integration. uint counting multiples of ADC samples since last sync (sync_time, id=0x1027). Divide this number by timestamp_scale (id=0x1046) to get back to seconds since last sync when this integration was actually started. Note that the receiver will need to figure out the centre timestamp of the accumulation (eg, by adding half of int_time, id 0x1016).',
                    shape=[], fmt=spead.mkfmt(('u',spead.ADDRSIZE)),init_val=0)

                ig.add_item(name=("xeng_raw%i"%x),id=(0x1800+x),
                    description="Raw data for xengine %i out of %i. Frequency channels are split amongst xengines. Frequencies are distributed to xengines in a round-robin fashion, starting with engine 0. Data from all X engines must thus be combed or interleaved together to get continuous frequencies. Each xengine calculates all baselines (n_bls given by SPEAD ID 0x100B) for a given frequency channel. For a given baseline, -SPEAD ID 0x1040- stokes parameters are calculated (nominally 4 since xengines are natively dual-polarisation; software remapping is required for single-baseline designs). Each stokes parameter consists of a complex number (two real and imaginary unsigned integers)."%(x,self.config['n_xeng']),
                    ndarray=(numpy.dtype(numpy.int32),(self.config['n_chans']/self.config['n_xeng'],self.config['n_bls'],self.config['n_stokes'],2)))

        tx.send_heap(ig.get_heap())
        self.syslogger.info("Issued SPEAD data descriptor to %s:%i."%(self.config['rx_meta_ip_str'],self.config['rx_udp_port']))

