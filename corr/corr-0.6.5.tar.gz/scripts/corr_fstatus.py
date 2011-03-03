#! /usr/bin/env python
"""
Reads the error counters on the correlator Xengines and reports such things as accumulated XAUI and packet errors.
\n\n
Revisions:
2010-12-11  JRM Added sync_val to lookup
                added fast scroll ability
                added clear error ability
2010-10-26  PVP Use ncurses via class scroll in scroll.py to allow scrolling around on-screen data
2010-07-22  JRM Ported for corr-0.5.5
2009-12-01  JRM Layout changes, check for loopback sync
2009/11/30  JRM Added support for gbe_rx_err_cnt for rev322e onwards.
2009/07/16  JRM Updated for x engine rev 322 with KATCP.

Todo:
print errors in RED.
"""
import corr, time, sys,struct,logging

def exit_fail():
    scroller.screenTeardown()
    print 'FAILURE DETECTED. Log entries:\n',lh.printMessages()
    print "Unexpected error:", sys.exc_info()
    try:
        c.disconnect_all()        
    except: pass
    raise
    exit()

def exit_clean():
    scroller.screenTeardown()
    try:
        c.disconnect_all()        
    except: pass
    exit()

if __name__ == '__main__':
    from optparse import OptionParser

    p = OptionParser()
    p.set_usage('%prog [options] CONFIG_FILE')
    p.set_description(__doc__)
    p.add_option('-c', '--clk_check', dest='clk_check',action='store_true', default=False,
        help='Perform clock integrity checks.')

    opts, args = p.parse_args(sys.argv[1:])

    if args==[]:
        print 'Please specify a configuration file! \nExiting.'
        exit()

lh=corr.log_handlers.DebugLogHandler()
scroller = None
screenData=[]

try:
    # set up the curses scroll screen
    scroller = corr.scroll.Scroll()
    scroller.screenSetup()
    scroller.setInstructionString("A toggles auto-clear, C to clear once.")
    scroller.clearScreen()
    scroller.drawString('Connecting...')
    autoClear = False
    clearOnce = False
    c=corr.corr_functions.Correlator(args[0],lh)
    for logger in c.floggers: logger.setLevel(10)
    scroller.drawString(' done.\n')    
    # get FPGA data
    servers = c.fsrvs
    n_ants = c.config['n_ants']
    start_t = time.time()
    if opts.clk_check:
        clk_check = c.feng_clks_get()
        scroller.drawString('Estimating clock frequencies for connected F engines...\n')
        sys.stdout.flush()
        for fn,feng in enumerate(c.fsrvs):
            scroller.drawString('\t %s (%i MHz)\n' % (feng,clk_check[fn]))
        scroller.drawString('F engine clock integrity: ')
        pps_check = c.check_feng_clks()
        scroller.drawString('%s\n' % {True : 'Pass', False: 'FAIL!'}[pps_check])
        if not pps_check:
            scroller.drawString(c.check_feng_clk_freq(verbose = True) + '\n')

    lookup = {'adc_overrange': '[ADC OVERRANGE]',
              'ct_error': '[CORNER-TURNER ERROR]',
              'fft_overrange': '[FFT OVERFLOW]',
              'sync_val': 'Sync offset in ADC clock cycles.',
              'quant_overrange': 'Quantiser overrange.',
              'xaui_lnkdn': '[XAUI LINK DOWN]',
              'xaui_over': "[XAUI TX OVERFLOW]"}

    time.sleep(2)

    # main program loop
    lastUpdate = time.time() - 3
    while True:
        # get key presses from ncurses
        keyPress = scroller.processKeyPress()
        if keyPress[0] > 0:
            if (keyPress[1] == 'a') or (keyPress[1] == 'A'):
                autoClear = not autoClear
            elif (keyPress[1] == 'c') or (keyPress[1] == 'C'):
                clearOnce = True
            scroller.drawScreen(screenData)

        if (time.time() > (lastUpdate + 1)): # or gotNewKey:
            screenData = []

            mcnts = c.mcnt_current_get()
            status = c.feng_status_get_all()
            uptime = c.feng_uptime()
            fft_shift = c.fft_shift_get_all()
            
            if c.config['adc_type'] == 'katadc' : rf_status = c.rf_status_get_all()
            if autoClear or clearOnce:
                c.rst_fstat()
                clearOnce = False
            
            for ant in range(c.config['n_ants']):
                for pol in c.config['pols']:
                    ffpga_n,xfpga_n,fxaui_n,xxaui_n,feng_input = c.get_ant_location(ant,pol)
                    screenData.append('  Input %i%s (%s input %i, mcnt %i):' % (ant,pol,c.fsrvs[ffpga_n],feng_input, mcnts[ffpga_n]))
                    if c.config['adc_type'] == 'katadc' :
                        screenData.append("    RF %8s:      gain:  %5.1f dB" % ({True: 'Enabled', False: 'Disabled'}[rf_status[(ant,pol)][0]],rf_status[(ant,pol)][1]))
                    screenData.append('    FFT shift pattern:       0x%06x' % fft_shift[(ant,pol)])
                    printString = '    Cumulative errors: '
                    for item,error in status[(ant,pol)].items():
                        if error == True: printString = printString + lookup[item]
                    screenData.append(printString)
                screenData.append('')

            screenData.append('Time: %i seconds' % (time.time() - start_t))
            if autoClear: screenData.append("Auto-clear ON.")
            else: screenData.append("Auto-clear OFF.")
            scroller.drawScreen(screenData)
            lastUpdate = time.time()

except KeyboardInterrupt:
        exit_clean()
except: 
        exit_fail()

exit_clean()

