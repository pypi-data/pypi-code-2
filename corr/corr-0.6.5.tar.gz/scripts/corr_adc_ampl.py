#!/usr/bin/env python

'''
Reads the values of the RMS amplitude accumulators on the ibob through the X engine's XAUI connection.\n

Revisions:
2011-01-04  JRM Moved scroller screen teardown into try statement so that it doesn't clobber real error messages in the event that it wasn't instantiated in the first place.
2010-12-11  JRM Removed bit estimate printing.
                ADC overrange now just shows flag, does not cover amplitude text.
                ncurses scroller fix to allow fast scrolling of screen.
1.32 JRM swapped corr.rst_cnt for corr.rst_fstat and swapped column for RMS levels in dB.
1.31 PVP Changed to accomodate change to corr_functions.adc_amplitudes_get() function - key in return dict changed from rms to rms_raw
1.30 PVP Change to ncurses interface with ability to clear error statuses using corr.rst_cnt 
1.21 PVP Fix filename in OptionParser section.
1.20 JRM Support any number of antennas together with F engine 305 and X engine rev 322 and later.\n
1.10 JRM Requires F engine rev 302 or later and X engine rev 308 or later.\n

'''
import corr, time, numpy, struct, sys, logging

def exit_fail():
    print 'FAILURE DETECTED. Log entries:\n', lh.printMessages()
    print "Unexpected error:", sys.exc_info()
    try:
        scroller.screenTeardown()
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
    p.set_usage(__file__ + ' [options] CONFIG FILE')
    p.add_option('-v', '--verbose', dest='verbose', action='store_true', help='Print raw output.')
    p.set_description(__doc__)
    opts, args = p.parse_args(sys.argv[1:])
    if args==[]:
        print 'Please specify a configuration file!\nExiting.'
        exit()

lh = corr.log_handlers.DebugLogHandler()

try:
    print 'Connecting to F-engines using config file %s...' % args[0],
    c = corr.corr_functions.Correlator(args[0], lh)
    for s, server in enumerate(c.fsrvs): c.floggers[s].setLevel(10)
    print 'done.'
    time.sleep(1)
    # set up the curses scroll screen
    scroller = corr.scroll.Scroll()
    scroller.screenSetup()
    scroller.setInstructionString("A toggles auto-clear, C to clear once.")
    # main program loop
    lastUpdate = time.time() - 3
    autoClear = False
    clearOnce = False
    screenData = []
    while(True):
        # get key presses from ncurses
        keyPress = scroller.processKeyPress()
        if keyPress[0] > 0:
            if (keyPress[1] == 'a') or (keyPress[1] == 'A'):
                autoClear = not autoClear
            elif (keyPress[1] == 'c') or (keyPress[1] == 'C'):
                clearOnce = True
            scroller.drawScreen(screenData)

        if (time.time() > (lastUpdate + 1)):
            screenData = []
            # get the data
            amps = c.adc_amplitudes_get()
            stats = c.feng_status_get_all()
            if autoClear or clearOnce:
                c.rst_fstat()
                clearOnce = False
            screenData.append('IBOB: ADC0 is furthest from power port, ADC1 is closest to power port.')
            screenData.append('ROACH: ADC0 is right, ADC1 is left (when viewed from front).')
            screenData.append('ADC input amplitudes averaged %i times.' % c.config['adc_levels_acc_len'])
            screenData.append('------------------------------------------------')
            for ant,pol in sorted(amps):
                ffpga_n, xfpga_n, fxaui_n, xxaui_n, feng_input = c.get_ant_location(ant,pol)
                displayString = 'Ant %i%s (%s in%i): ' % (ant, pol, c.fsrvs[ffpga_n], feng_input)
                if c.config['adc_type'] == 'katadc':
                    preamp=c.rf_status_get(ant,pol)[1]
                    displayString += ' %6.2f dBm with preamp of %5.1fdB = %6.2fdBm.' % (amps[(ant, pol)]['rms_db']+preamp,preamp,amps[(ant, pol)]['rms_db'])
                else:
                    displayString += ' %.3f' % (amps[(ant, pol)]['rms_raw'])
                if stats[(ant, pol)]['adc_overrange']:
                    displayString += ' ADC OVERRANGE!'
                screenData.append(displayString)
            screenData.append("")
            if autoClear: screenData.append("Auto-clear ON.")
            else: screenData.append("Auto-clear OFF.")
            scroller.drawScreen(screenData)
            lastUpdate = time.time()
            time.sleep(0.1)

except KeyboardInterrupt:
    exit_clean()
except:
    exit_fail()

print 'Done with all'
exit_clean()

# end

