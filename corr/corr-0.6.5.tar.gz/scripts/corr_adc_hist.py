#!/usr/bin/env python

'''
Plots a histogram of the ADC values from a specified antenna and pol. Hard-coded for 8 bit ADCs.\n

Revisions:
2010-12-11: JRM Add printout of number of bits toggling in ADC.
                Add warning for non-8bit ADCs.
2010-08-05: JRM Mods to support variable snap block length.
1.1 PVP Initial.\n

'''
import matplotlib
import time, corr, numpy, struct, sys, logging, pylab

# what format are the snap names and how many are there per antenna
snapName = 'adc_snap'
snapCount = 2
# what is the bram name inside the snap block
bramName = 'bram'

def exit_fail():
    print 'FAILURE DETECTED. Log entries:\n', lh.printMessages()
    exctype, value = sys.exc_info()[:2]
    if exctype != None: print "Unexpected error:", sys.exc_info()
    try:
        c.disconnect_all()
    except:
        pass
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
    p.add_option('-v', '--verbose', dest = 'verbose', action = 'store_true', help = 'Print raw output.')
    p.add_option('-a', '--antenna', dest = 'antAndPol', action = 'store', help = 'Specify an antenna and pol for which to get ADC histograms. 3x will give pol x for antenna three. 27y will give pol y for antenna 27. 3 on its own will give both \'x\' and \'y\' for antenna three. 3x,27y will do pol \'x\' of antenna 3 and pol \'y\' of antenna 27.')
    p.add_option('-c', '--compare', dest = 'comparePlots', action = 'store_true', help = 'Compare plots directly using the same y-axis for all plots.')
    p.set_description(__doc__)
    opts, args = p.parse_args(sys.argv[1:])
    if args==[]:
        print 'Please specify a configuration file!\nExiting.'
        exit()

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
            exit()
        antennaNumber = int(ant.replace('x', '').replace('y', ''))
        if (ant.find('x') < 0) and (ant.find('y') < 0):
            ant = ant + 'xy'
        if ant.find('x') > 0:
            plotList.append({'antenna':antennaNumber, 'pol':'x'})
        if ant.find('y') > 0:
            plotList.append({'antenna':antennaNumber, 'pol':'y'})
    return plotList

# the function that gets data given a required polarisation
def getUnpackedData(requiredPol):
    antLocation = c.get_ant_location(requiredPol['antenna'], requiredPol['pol'])
    # which fpga do we need?
    requiredFpga = antLocation[0]
    # which ADC is it on that FPGA?
    requiredFengInput = antLocation[4]
    # get the data
    #timeNow = time.time()
    packedData = c.ffpgas[requiredFpga].get_snap(snapName + str(requiredFengInput), [bramName], man_trig = True, man_valid = True, wait_period = 0.1)
    #print "Getting data took %i seconds." % (time.time() - timeNow)
    # unpack the data
    unpackedBytes = []
    bits_used=-1
    if packedData['length'] > 0:
        unpackedBytes = numpy.array(struct.unpack('>%ib'%(packedData['length'] * 4), packedData[bramName]))#/float(packedData['length']*4)
        bits_used=numpy.log2(numpy.max(unpackedBytes) - numpy.min(unpackedBytes))
        #print '%i%s: %4.2f bits toggling.'%(pol['antenna'],pol['pol'],bits_used)
    return unpackedBytes, requiredFpga, bits_used

# make the log handler
lh = corr.log_handlers.DebugLogHandler()

# check the specified antennae, if any
polList = []
if opts.antAndPol != None:
    polList = parseAntenna(opts.antAndPol)
else:
    print 'No antenna given for which to plot data.'
    exit_fail()

try:
    # make the correlator object
    print 'Connecting to correlator...',
    c = corr.corr_functions.Correlator(args[0], lh)
    for logger in c.floggers: logger.setLevel(logging.DEBUG)
    print 'done.'

    if c.config['adc_bits'] != 8: 
        print 'Sorry, this script is hard-coded for 8 bit ADCs. Your ADC has %i bits.'%c.config['adc_bits']
        exit_clean()

    # set up the figure with a subplot for each polarisation to be plotted
    fig = matplotlib.pyplot.figure()

    # create the subplots
    subplots = []
    numberOfPolarisations = len(polList)
    for p, pol in enumerate(polList):
        subPlot = fig.add_subplot(numberOfPolarisations, 1, p + 1)
        subplots.append(subPlot)

    # callback function to draw the data for all the required polarisations
    def drawDataCallback(comparePlots):
        maxY = 0
        for p, pol in enumerate(polList):
            unpackedData, ffpga, bits_used = getUnpackedData(pol)
            print '%i%s: %4.2f bits toggling.'%(pol['antenna'],pol['pol'],bits_used)
            subplots[p].cla()
            subplots[p].set_xticks(range(-130, 131, 10))
            histData, bins, patches = subplots[p].hist(unpackedData, bins = 256, range = (-128,128))
            maxY = max(maxY, max(histData))
            subplots[p].set_title('%i%s (max %i)'%(pol['antenna'],pol['pol'],max(histData)))
            if not comparePlots:
                matplotlib.pyplot.ylim(ymax = (max(histData) * 1.05))            
        if comparePlots:
            for p2, pol2 in enumerate(polList):
                matplotlib.pyplot.subplot(len(polList), 1, p2 + 1)
                matplotlib.pyplot.ylim(ymax = maxY)
        fig.canvas.draw()
        fig.canvas.manager.window.after(100, drawDataCallback, comparePlots)

    # start the process
    fig.canvas.manager.window.after(100, drawDataCallback, opts.comparePlots)
    matplotlib.pyplot.show()
    print 'Plot started.'

except KeyboardInterrupt:
    exit_clean()
except:
    exit_fail()

print 'Done with all.'
exit_clean()

# end

