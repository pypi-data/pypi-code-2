#!/usr/bin/env python
"""This script receives data from interleaved X engines assembles a complete integration and then stores to disk (in h5 format) and forwards to the signal displays.
Original Author: Simon Ratcliffe"""
import numpy as np, spead, logging, sys, time, h5py, corr

logging.basicConfig(level=logging.WARN)
#logging.basicConfig(level=logging.INFO)



if __name__ == '__main__':
    from optparse import OptionParser
    p = OptionParser()
    p.set_usage('%prog [options] CONFIG_FILE')
    p.set_description(__doc__)
    p.add_option('-a', '--disable_autoscale', dest='acc_scale',action='store_false', default=True,
       help='Do not autoscale the data by dividing down by the number of accumulations.  Default: Scale back by n_accs.')
    opts, args = p.parse_args(sys.argv[1:])
    if args==[]:
        print 'Please specify a configuration file! \nExiting.'
        exit()
    else:
        acc_scale=opts.acc_scale
        config=corr.cn_conf.CorrConf(args[0])
        data_port = config['rx_udp_port']
        sd_ip = config['sig_disp_ip_str']
        sd_port = config['sig_disp_port']


print 'Initalising SPEAD transports...'
print "Data reception on port",data_port
sys.stdout.flush()
rx = spead.TransportUDPrx(data_port, pkt_count=1024, buffer_size=51200000)
print "Sending Signal Display data to",sd_ip
tx_sd = spead.Transmitter(spead.TransportUDPtx(sd_ip, sd_port))
ig = spead.ItemGroup()
ig_sd = spead.ItemGroup()
f = h5py.File(str(int(time.time())) + ".synth.h5", mode="w")
data_ds = None
ts_ds = None
idx = 0
dump_size = 0
datasets = {}
datasets_index = {}
meta_required = ['n_chans','n_bls','n_stokes','n_xengs','sync_time']
 # we need these bits of meta data before being able to assemble and transmit signal display data
meta = {}
sd_frame = None
sd_slots = None
timestamp = None
write_enabled = True

try:
    for heap in spead.iterheaps(rx):
        ig.update(heap)
        for name in ig.keys():
            item = ig.get_item(name)
            if not item._changed and datasets.has_key(name): continue #the item has not changed and we already have a record of it.
            if name in meta_required:
                meta_required.pop(meta_required.index(name))
                if len(meta_required) == 0:
                    sd_frame = np.zeros((ig['n_chans'],ig['n_bls'],ig['n_stokes'],2),dtype=np.int32)
                    print "Got the required metadata. Initialised sd frame to shape",sd_frame.shape
                    sd_slots = np.zeros(ig['n_xengs']) #create an SD slot for each X engine. This keeps track of which engines' data have been received for this integration.
                    ig_sd.add_item(name=('sd_data'),id=(0x3501), description="Combined raw data from all x engines.",
            ndarray=(sd_frame.dtype,sd_frame.shape))

                    ig_sd.add_item(name=('sd_timestamp'), id=0x3502, description='Timestamp of this sd frame in centiseconds since epoch (40 bit limitation).', shape=[], fmt=spead.mkfmt(('u',spead.ADDRSIZE)))


            if not datasets.has_key(name):
             # check to see if we have encountered this type before
                shape = ig[name].shape if item.shape == -1 else item.shape
                dtype = np.dtype(type(ig[name])) if shape == [] else item.dtype                 
                if dtype is None: dtype = ig[name].dtype
                # if we can't get a dtype from the descriptor try and get one from the value
                print "Creating dataset for name:",name,", shape:",shape,", dtype:",dtype
                f.create_dataset(name,[1] + ([] if list(shape) == [1] else list(shape)), maxshape=[None] + ([] if list(shape) == [1] else list(shape)), dtype=dtype)
                dump_size += np.multiply.reduce(shape) * dtype.itemsize
                datasets[name] = f[name]
                datasets_index[name] = 0
                if not item._changed:
                    continue
            else:
                print "Adding",name,"to dataset. New size is",datasets_index[name]+1
                f[name].resize(datasets_index[name]+1, axis=0)

            #whatever SPEAD data we received, store it anyway:
            #This appending scheme is dangerous... if an X engine drops out and then reappears, it will have mis-aligned data.
            f[name][datasets_index[name]] = ig[name]
            datasets_index[name] += 1
            item._changed = False


            #deal with special cases:

            if sd_frame is not None and name.startswith("xeng_raw"):
                #now we store this x engine's data for sending sd data.
                xeng_id = int(name[8:])
                sd_frame[xeng_id::ig['n_xengs']] = ig[name]

            if sd_frame is not None and name.startswith("timestamp"):
                #we got a timestamp. 
                #We Need to check all the X engines are issuing the same timestamp.
                # for now, just assume they're all correct and the same. BAD!
                xeng_id = int(name[9:])
                timestamp = ig['sync_time'] + (ig['timestamp0'] / ig['scale_factor_timestamp']) #in seconds since unix epoch
                print "Decoded timestamp:", timestamp," (",time.ctime(timestamp),")"
                sd_slots[xeng_id] = timestamp 
                #sd_slots[xeng_id] = int(timestamp) #record that this xengine's data was received. Round to nearest second. Don't care about Signal displays misaligned by less than 1s.

            if timestamp is not None and sd_frame is not None and sd_slots is not None and (np.min(sd_slots)==np.max(sd_slots)):
                #figure out if we've received an entire integration, and if so, send the SD frame
                # send a signal display frame which should hopefully be full...
                print "Sending signal display frame, %s, with timestamp %i. Max: %i, Mean: %i" % (
                   "Unscaled" if not acc_scale else "Scaled by %i" %(ig['n_accs']),
                    timestamp,np.max(ig[name]),np.mean(ig[name]))
                ig_sd['sd_data'] = sd_frame if not acc_scale else (sd_frame / float(ig['n_accs'])).astype(sd_frame.dtype)
                ig_sd['sd_timestamp'] = int(timestamp * 100)
                tx_sd.send_heap(ig_sd.get_heap())
                timestamp = None
                sd_slots = np.zeros(len(sd_slots))
                sd_frame = np.zeros((ig['n_chans'],ig['n_bls'],ig['n_stokes'],2),dtype=sd_frame.dtype)

except KeyboardInterrupt:
    print "Closing file."
    for (name,idx) in datasets_index.iteritems():
        if idx == 1:
            print "Repacking dataset",name,"as an attribute as it is singular."
            f['/'].attrs[name] = f[name].value[0]
            f.__delitem__(name)

    f.flush()
    f.close()

