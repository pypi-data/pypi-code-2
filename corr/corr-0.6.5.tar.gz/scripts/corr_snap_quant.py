#!/usr/bin/env python

'''
Grabs the contents of "snap_xaui" for a given antenna and plots successive accumulations.
Does not use the standard 'corr_functions' error checking.
Assumes 4 bit values for power calculations.
Assumes the correlator is already initialsed and running etc.

Author: Jason Manley
Date: 2009-07-01

Revisions:
2010-11-24  PP  Fix to plotting
                Ability to plot multiple antennas
2010-07-22: JRM Mods to support ROACH based F engines (corr-0.5.0)
2010-02-01: JRM Added facility to offset capture point.
                Added RMS printing and peak bits used.
2009-07-01: JRM Ported to use corr_functions connectivity
                Fixed number of bits calculation

'''
import corr, time, numpy, struct, sys, logging, pylab, matplotlib

polList = []

def exit_fail():
    print 'FAILURE DETECTED. Log entries:\n', lh.printMessages()
    print "Unexpected error:", sys.exc_info()
    try:
        c.disconnect_all()
    except: pass
    raise
    exit()

def exit_clean():
    try:
        c.disconnect_all()
    except: pass
    exit()

def drawDataCallback():
    for p, pol in enumerate(polList):
        get_data(pol)
        pol['plot'].cla()
        pol['plot'].set_xlim(0, c.config['n_chans'] + 1)
        pol['plot'].set_title('Quantiser amplitude output for input %i %s, averaged over %i spectra.' % (pol['antenna'], pol['pol'], pol['num_accs']))
        pol['plot'].set_xlabel('Frequency channel')
        pol['plot'].set_ylabel('Average level')
        pol['plot'].plot(numpy.divide(pol['accumulations'], pol['num_accs']))
        fig.canvas.draw()
        fig.canvas.manager.window.after(100, drawDataCallback)

# parse the antenna argument passed to the program
def parseAntenna(antArg):
    import re
    regExp = re.compile('^[0-9]{1,4}[xy]{0,2}$')
    ants = antArg.lower().replace(' ','').split(',')
    plotList = []
    for ant in ants:
        # is it valid?
        if not regExp.search(ant):
            print '\'' + ant + '\' is not a valid -a argument!\nExiting.'
            exit_fail()
        antennaNumber = int(ant.replace('x', '').replace('y', ''))
        if (ant.find('x') < 0) and (ant.find('y') < 0):
            ant = ant + 'xy'
        if ant.find('x') > 0:
            plotList.append({'antenna': antennaNumber, 'pol':'x'})
        if ant.find('y') > 0:
            plotList.append({'antenna': antennaNumber, 'pol':'y'})
    return plotList

def get_data(pol):
    ffpga_n, xfpga_n, fxaui_n, xxaui_n, feng_input = c.get_ant_location(pol['antenna'], pol['pol'])
    dev_name = 'quant_snap%i' % feng_input    
    print 'Integrating data %i from input %i on %s:' % (pol['num_accs'], feng_input, c.fsrvs[ffpga_n])
    print ' Grabbing data off snap blocks...',
    bram_dmp = c.ffpgas[ffpga_n].get_snap(dev_name,['bram'], man_trig = man_trigger, wait_period = 2)
    print 'done.'
    print ' Unpacking bram contents...',
    sys.stdout.flush()
    pckd_8bit = struct.unpack('>%iB' % (bram_dmp['length']*4), bram_dmp['bram'])
    unpacked_vals = []
    for val in pckd_8bit:
        pol_r_bits = (val & ((2**8) - (2**4))) >> 4
        pol_i_bits = (val & ((2**4) - (2**0)))
        unpacked_vals.append(float(((numpy.int8(pol_r_bits << 4)>> 4)))/(2**binary_point) + 1j * float(((numpy.int8(pol_i_bits << 4)>> 4)))/(2**binary_point))
    print 'done.'
    print ' Accumulating...', 
    for i, val in enumerate(unpacked_vals):
        freq = i % c.config['n_chans']
        pol['accumulations'][freq] += abs(val)
        if opts.verbose:
            print '[%5i] [Freq %4i] %2.2f + %2.2f (summed amplitude %3.2f)' % (i, freq, val.real, val.imag, pol['accumulations'][freq])
    pol['num_accs'] += (len(unpacked_vals)/c.config['n_chans'])
    print 'done.'
    return

if __name__ == '__main__':
    from optparse import OptionParser
    p = OptionParser()
    p.set_usage('%prog [options] CONFIG_FILE')
    p.set_description(__doc__)
    p.add_option('-t', '--man_trigger', dest='man_trigger', action='store_true',
        help='Trigger the snap block manually')   
    p.add_option('-v', '--verbose', dest='verbose', action='store_true',
        help='Print raw output.')  
    p.add_option('-p', '--noplot', dest='noplot', action='store_true',
        help='Do not plot averaged spectrum.')  
    p.add_option('-a', '--ant', dest='ant', type='str', default='0x',
        help='Select antenna to query. Default: 0x')
    opts, args = p.parse_args(sys.argv[1:])
    if args == []:
        print 'Please specify a configuration file! \nExiting.'
        exit()
    if opts.man_trigger: man_trigger = True
    else: man_trigger = False

report = []
lh = corr.log_handlers.DebugLogHandler()

# check the specified antennae, if any
polList = []
if opts.ant != None:
    polList = parseAntenna(opts.ant)
else:
    print 'No antenna given for which to plot data.'
    exit_fail()

try:
    print 'Connecting...',
    c = corr.corr_functions.Correlator(args[0], lh)
    for logger in c.xloggers: logger.setLevel(10)
    print 'done.'

    binary_point = c.config['feng_fix_pnt_pos']
    packet_len = c.config['10gbe_pkt_len']
    n_chans = c.config['n_chans']
    num_bits = c.config['feng_bits']
    adc_bits = c.config['adc_bits']
    adc_levels_acc_len = c.config['adc_levels_acc_len']

    if num_bits != 4:
        print 'This script is only written to work with 4 bit quantised values.'
        exit_fail()

    # set up the figure with a subplot for each polarisation to be plotted
    fig = matplotlib.pyplot.figure()

    # check the supplied antennas and populate the array of integration data
    numberOfPolarisations = len(polList)
    for p, pol in enumerate(polList):
        if not pol['pol'] in c.config['pols']:
            print 'Unrecognised polarisation (%s). Must be in ' % pol['pol'], c.config['pols']
            exit_fail()
        if pol['antenna'] > c.config['n_ants']:
            print 'Invalid antenna (%i). There are %i antennas in this design.' % (pol['antenna'], c.config['n_ants'])
            exit_fail()
        pol['accumulations'] = numpy.zeros(c.config['n_chans'])
        pol['num_accs'] = 0
        pol['plot'] = fig.add_subplot(numberOfPolarisations, 1, p + 1)

    # start the process    
    fig.canvas.manager.window.after(100, drawDataCallback)
    print 'Plot started.'
    matplotlib.pyplot.show()

except KeyboardInterrupt:
    exit_clean()
except:
    exit_fail()

exit_clean()

#end

