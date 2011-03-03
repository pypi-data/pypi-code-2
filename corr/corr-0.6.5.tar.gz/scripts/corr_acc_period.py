#! /usr/bin/env python
"""Configures the vector accumulators' period on all X engines.
Revs:
2010-11-13: JRM Pause output before changing acc time.
"""
import corr, time, sys, numpy, os, logging

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
    p.set_usage('%prog CONFIG_FILE')
    p.set_description(__doc__)
    p.add_option('-t', '--time', dest='acc_time', type='float', default=-1,
        help="Specify the how long you'd like to accumulate (in seconds). Default: from config")
    p.add_option('-s', '--no_restart', dest='no_restart',action='store_true', default=False,
        help='Do not restart output after reconfiguring the VACC.')

    opts, args = p.parse_args(sys.argv[1:])

    if args==[]:
        print 'Please specify a configuration file! \nExiting.'
        exit()

lh=corr.log_handlers.DebugLogHandler()

try:
    print 'Connecting...',
    c=corr.corr_functions.Correlator(args[0],lh)
    for logger in c.floggers: logger.setLevel(10)
    print 'done.'

    if opts.acc_time>0:
        acc_time=opts.acc_time
    else:
        acc_time=c.config['int_time']

    print ('''Pausing output...'''),
    c.tx_stop()
    print 'done.'

    print (''' Setting the accumulation period to %2.2f seconds...'''%(acc_time)),
    sys.stdout.flush()
    c.acc_time_set(acc_time)
    print 'done, wrote %i into acc_len (%5.3fs).'%(c.config['acc_len'],c.config['int_time'])

    print ('''Restarting output...'''),
    if opts.no_restart == False: 
        c.tx_start()
        print 'done.'
    else: print 'skipped.'

except KeyboardInterrupt:
    exit_clean()
except:
    exit_fail()
exit()
