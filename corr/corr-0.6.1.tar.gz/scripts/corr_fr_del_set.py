#! /usr/bin/env python
"""Configures CASPER correlator Fengine's Fringe rotate and delay compensation cores. 
Author: Jason Manley
Revs:
2010-11-20  JRM First release """
import corr, numpy,sys,os,time,logging

def exit_fail():
    print 'FAILURE DETECTED. Log entries:\n',lh.printMessages()
    print "Unexpected error:", sys.exc_info()
    try:
        c.disconnect_all()
    except: pass
    #raise
    exit()

def exit_clean():
    try:
        c.disconnect_all()
    except: pass
    exit()


if __name__ == '__main__':
    from optparse import OptionParser

    p = OptionParser()
    p.set_usage('%prog [options] CONFIG_FILE')
    p.set_description(__doc__)
    p.add_option('-a', '--ant', dest = 'ant_str', action = 'store', 
        help = 'Specify the antenna and pol. For example, 3x will give pol x for antenna three.')
    p.add_option('-f', '--fringe_rate', dest='fringe_rate', type='float', default=0,
        help='''Set the fringe rate in cycles per second (Hz). Defaults to zero.''')
    p.add_option('-o', '--fringe_offset', dest='fringe_offset', type='float', default=0,
        help='''Set the fringe offset in degrees. Defaults to zero''')
    p.add_option('-d', '--delay', dest='delay', type='float', default=0,
        help='''Set the delay in seconds. Defaults to zero.''')
    p.add_option('-r', '--delay_rate', dest='delay_rate', type='float', default=0,
        help='''Set the delay rate.  Unitless; eg. seconds per second. Defaults to zero.''')
    p.add_option('-t', '--ld_time', dest='ld_time', type='float', default=-1,
        help='''Load time in seconds since the unix epoch. NOTE: SYSTEM TIME MUST BE ACCURATE! If not specified, load ASAP.''')

    opts, args = p.parse_args(sys.argv[1:])

    if args==[]:
        print 'Please specify a configuration file! \nExiting.'
        exit()

lh=corr.log_handlers.DebugLogHandler()

try:
    print 'Connecting...',
    c=corr.corr_functions.Correlator(args[0],lh)
    for logger in c.floggers: logger.setLevel(logging.INFO)
    print 'done.'

    ant,pol=(int(opts.ant_str[:-1]),opts.ant_str[-1])
    if ant < 0 or ant > c.config['n_ants']:
        raise RuntimeError("Antenna index out of range (0-%i).")
    if not pol in c.config['pol_map']:
        raise RuntimeError("Bad polarisation specified.") 

    if opts.ld_time <0: trig_time = time.time()+0.1
    else: trig_time = opts.ld_time

    print "Setting input %i%c's delay to %es + %es/s with a fringe of %e + %eHz at %s local (%s UTC).... "%(
        ant,pol,opts.delay,opts.delay_rate,opts.fringe_offset,opts.fringe_rate,
        time.strftime('%H:%M:%S',time.localtime(trig_time)),time.strftime('%H:%M:%S',time.gmtime(trig_time))),
    act=c.fr_delay_set(ant=ant,pol=pol,
            delay=opts.delay,
            delay_rate=opts.delay_rate, 
            fringe_phase=opts.fringe_offset,
            fringe_rate=opts.fringe_rate)
    print 'ok.'

    print 'Closest we could get: '
    print '===================== '
    print 'Actual fringe offset: %15.10e'%act['act_fringe_offset']
    print 'Actual fringe rate:   %15.10e'%act['act_fringe_rate']
    print 'Actual delay:         %15.10e'%act['act_delay']
    print 'Actual delay rate:    %15.10e'%act['act_delay_rate']

except KeyboardInterrupt:
    exit_clean()
except:
    exit_fail()

exit_clean()

