#!/usr/bin/env python

'''
Plots time domain ADC values from a specified antenna and pol.\n
Optionally waits for an overrange condition and plots the ~200 datapoints to either side of the event. Useful for looking for glitches and transients.

Revisions:
2011/02/19  JRM Added transient (triggered by overrange) support.
2010/08/03  GSJ Initial.\n

'''
import matplotlib
import time, corr, numpy, struct, sys, logging, pylab


def exit_fail():
    print 'FAILURE DETECTED. Log entries:\n', lh.printMessages()
    print "Unexpected error:", sys.exc_info()
    try:
        c.disconnect_all()
    except:
        pass
    raise
    exit()

def exit_clean():
    try:
        c.disconnect_all()
    except:
        pass
    exit()

if __name__ == '__main__':
    from optparse import OptionParser
    p = OptionParser()
    p.set_usage('%prog [options] CONFIG FILE')
    p.add_option('-t', '--transient', dest = 'trans', action = 'store_true', help = 'Wait indefinitely for a snap block stop condition (normally an ADC overrange event), then plot the peak event.')
    p.add_option('-n', '--plotlen', dest = 'plotlen', type = 'int',default= 100, help = 'Number of data points to plot.')
    p.add_option('-a', '--antenna', dest = 'antAndPol', action = 'store', help = 'Specify an antenna and pol for which to get ADC histograms. 3x will give pol x for antenna three. 27y will give pol y for antenna 27.')
    p.set_description(__doc__)
    opts, args = p.parse_args(sys.argv[1:])
    if args==[]:
        print 'Please specify a configuration file!\nExiting.'
        exit()


# make the log handler
lh=corr.log_handlers.DebugLogHandler()

# check the specified antennae, if any
polList = []
if opts.antAndPol == None:
    print 'No antenna given for which to plot data.'
    exit_fail()

try:
    # make the correlator object
    print 'Connecting to correlator...',
    c=corr.corr_functions.Correlator(args[0], lh)
    for s,server in enumerate(c.fsrvs): c.floggers[s].setLevel(10)
    print 'done.'

    ant,pol = int(opts.antAndPol[:-1]),opts.antAndPol[-1]
    (ffpga_n,xfpga_n,fxaui_n,xxaui_n,feng_input) = c.get_ant_location(ant,pol)
    if opts.trans:
        print 'Starting snapshot capture, waiting for transient and then retrieving from BRAM...',
        sys.stdout.flush()
        snapraw1=c.ffpgas[ffpga_n].get_snap('adc_snap%i'%feng_input,['bram'],circular_capture=True,man_valid=True,man_trig=True,wait_period=-1)
    else:
        print 'Starting snapshot capture immediately and retrieving data from BRAM...',
        sys.stdout.flush()
        snapraw1=c.ffpgas[ffpga_n].get_snap('adc_snap%i'%feng_input,['bram'],man_valid=True,man_trig=True,wait_period=0.2)
    print 'done'

    if snapraw1['length'] > 0:
        unpackeddata1=struct.unpack('>%ib'%(snapraw1['length']*4),snapraw1['bram'])

        if opts.trans:
            print 'Looking for peak...'
            sys.stdout.flush()
            peak_pos=numpy.argmax(numpy.abs(unpackeddata1))
            print 'Found at index %i with value %i.'%(peak_pos,unpackeddata1[peak_pos])
            pylab.plot(unpackeddata1[max(0,peak_pos-100):min(snapraw1['length']*4,peak_pos+100)])
        else:
            pylab.plot(unpackeddata1[0:opts.plotlen])

        pylab.title('ADC_AMPLITUDE %i %s'%(ant,pol))
        pylab.xlabel('Time in adc samples')
        pylab.ylabel('Adc count')
        pylab.show()
    else:
        print 'Got no data back. Exiting.'

except KeyboardInterrupt:
    exit_clean()
except:
    exit_fail()

print 'Done with all.'
exit_clean()

# end

