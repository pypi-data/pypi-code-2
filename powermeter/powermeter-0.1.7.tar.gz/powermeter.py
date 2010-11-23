#!/usr/bin/env python

import serial
import time
import google_meter
import units
from optparse import OptionParser
import ConfigParser
import sys
import os
import logging
import logging.handlers


def firstRun():
    print '**********************************************************************'
    print 'Welcome to Powermeter. I will try to create a personal configuration file where you can customize Powermeter\'s presets:\n'
    cfg_device = raw_input('Device port name ? [/dev/term/0]:\n')
    if not cfg_device:
        cfg_device = '/dev/term/0'
        
    cfg_token = raw_input('Google power Meter Token ?:\n')
    while not cfg_token:
        print 'Token Error'
        cfg_token = raw_input('Please retype Google power Meter Token ?:\n')
    
    cfg_path = raw_input('Google Power Meter Device Path ?:\n')
    while not cfg_path:
        print 'Path Error'
        cfg_path = raw_input('Please retype Google Power Meter Device Path ?:\n')
    
    cfg_log = raw_input('Log file name ? [/var/log/powermeter.log]:\n')
    if not cfg_log:
        cfg_log = '/var/log/powermeter.log'
    
    print 'Initializing file from configuration => ',
    print os.path.expanduser('~/.powermeter.cfg')
    
    config = ConfigParser.RawConfigParser()
    
    config.add_section('main')
    config.set('main', 'device', cfg_device)
    config.set('main', 'token', cfg_token)
    config.set('main', 'path', cfg_path)
    config.set('main', 'log', cfg_log)
    
    with open(os.path.expanduser('~/.powermeter.cfg'), 'wb') as configfile:
        config.write(configfile)
    
    print 'Successful Creation!'
   

def core(opts,token,path,device,log):
    service = 'https://www.google.com/powermeter/feeds'
    
    logger = logging.getLogger('powermeter')
    hdlr = logging.handlers.RotatingFileHandler(log, maxBytes=1000000, backupCount=5)
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    hdlr.setFormatter(formatter)
    logger.addHandler(hdlr)
    logger.setLevel(logging.INFO)

    initial = opts.init
    
    if opts.port:
        device = port
    
    try:
        ser = serial.Serial(device,9600, timeout=25)
    except:
        print('Serial port %s unavailable' % device)
        sys.exit()
    
    service = google_meter.Service(token,service)

    
    while (1):
        line = ser.readline().strip()
        logger.info('Packet: %s' % line)
        try:
            (millis,tarif,iHP,iHC,conso,vide) = line.split(':')
        except:
            logger.info('Bad packet received !')
        else:
            ctime = int(time.time())
            cconso = (float(iHP) + float(iHC))/ 1000.0
            
            
            if not opts.test:
                measure = google_meter.InstMeasurement(path,ctime,cconso * units.KILOWATT_HOUR,0.1,0.0001 * units.KILOWATT_HOUR,initial)
                try:
                    service.PostEvent(measure)
                except:
                    logger.info('Conso: %s Kwh => sending error' % cconso)
                else:
                    logger.info('Conso: %s Kwh => sent to Google OK' % cconso)
            if initial:
                initial = False

    ser.close()
    
    
    
    

def main():
    parser = OptionParser(usage='%prog [options] \n%prog -h for full list of options')
    
    parser.add_option(  '-v', '--verbose', action='store_true', dest='verbose', help='Will provide some feedback [default]')    
    parser.add_option(  '-f', '--foreground', action='store_false', dest='daemon', help='Doesn\'t fork the daemon [default]')
    parser.add_option(  '-d', '--daemon', action='store_true', dest='daemon', help='Enable cleaning name for tvtags & movietags')
    parser.add_option(  '-n', '--no-initmeasure', action='store_false', dest='init', help='Don\'t send init measure packet')
    parser.add_option(  '-p', '--port', action='store', type='string', dest='port', metavar='Serial Port', help='Change default serial port')
    parser.add_option(  '-t', '--test', action='store_true', dest='test', help='Don\'t send measure to Google Power Meter')
    parser.add_option(  '--version', action='store_true', dest='version', help='Show  version information for iencode')
    parser.set_defaults( daemon=0, verbose=1, port='', version=False, test=False, init=True )
    
    opts, args = parser.parse_args()
    
    config = ConfigParser.RawConfigParser()
    
    if  not config.read(['/etc/powermeter.cfg', os.path.expanduser('~/.powermeter.cfg')]):
        sys.exit(firstRun())
    
    try:
        token = config.get('main', 'token')
        path = config.get('main', 'path')
        device = config.get('main', 'device')
        log = config.get('main','log')
    except:
        print "Configuration file incomplete !"
        sys.exit()
    
    
    if opts.daemon:
        import daemon
        
        print "Launch powermeter in background"
        with daemon.DaemonContext():
            core(opts,token,path,device,log)
        
    else:
        try:
            core(opts,token,path,device,log)
        except KeyboardInterrupt:
            print " received, exiting"
            sys.exit(1)



if __name__ == '__main__': 
    sys.exit(main())
