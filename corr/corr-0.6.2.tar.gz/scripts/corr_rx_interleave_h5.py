#!/usr/bin/python
"""This script receives data from interleaved X engines assembles a complete integration and then stores to disk (in h5 format) and forwards to the signal displays.
Original Author: Simon Ratcliffe"""
import numpy as np, spead, logging, sys, time, h5py, corr

logging.basicConfig(level=logging.INFO)

config=corr.cn_conf.CorrConf(sys.argv[-1])

data_port = config['rx_udp_port']
sd_ip = config['sig_disp_ip_str']
sd_port = config['sig_disp_port']

print 'Initalising SPEAD transports...'
print "Data reception on port",data_port
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
meta_required = ['n_chans','n_bls','n_stokes']
 # we need these bits of meta data before being able to assemble and transmit signal display data
meta = {}
sd_frame = None
sd_slots = None
sd_timestamp = None
write_enabled = True

for heap in spead.iterheaps(rx):
    ig.update(heap)
    for name in ig.keys():
        item = ig.get_item(name)
        if not item._changed: continue
        if name in meta_required:
            meta[name] = ig[name]
            meta_required.pop(meta_required.index(name))
            if len(meta_required) == 0:
                sd_frame = np.zeros((meta['n_chans'],meta['n_bls'],meta['n_stokes'],2),dtype=np.uint32)
                print "Initialised sd frame to shape",sd_frame.shape
        if not datasets.has_key(name):
         # check to see if we have encountered this type before
            shape = item.shape
            dtype = np.dtype(type(ig[name])) if shape == [] else ig[name].dtype
            print "Creating dataset for name:",name,", shape:",shape,", dtype:",dtype
            f.create_dataset(name,[1] + ([] if list(shape) == [1] else list(shape)), maxshape=[None] + ([] if list(shape) == [1] else list(shape)), dtype=dtype)
            dump_size += np.multiply.reduce(shape) * dtype.itemsize
            datasets[name] = f[name]
            datasets_index[name] = 0
        else:
            print "Adding",name,"to dataset. New size is",datasets_index[name]+1
            f[name].resize(datasets_index[name]+1, axis=0)
        if sd_frame is not None and name.startswith("xeng_raw"):
            if sd_slots is None:
                sd_frame.dtype = ig[name].dtype
                 # make sure we have the right dtype for the sd data
                sd_slots = np.zeros(meta['n_chans']/ig[name].shape[0])
                n_xeng = len(sd_slots)
                 # this is the first time we know how many x engines there are
                f['/'].attrs['n_xeng'] = n_xeng
                ig_sd.add_item(name=('sd_data'),id=(0x3501), description="Combined raw data from all x engines.", ndarray=(ig[name].dtype,sd_frame.shape))
                ig_sd.add_item(name=('sd_timestamp'), id=0x3502, description='Timestamp of this sd frame.', shape=[], fmt=spead.mkfmt(('u',spead.ADDRSIZE)))
                t_it = ig_sd.get_item('sd_data')
                print "Added SD frame dtype",t_it.dtype,"and shape",t_it.shape
                tx_sd.send_heap(ig_sd.get_heap())
            xeng_id = int(name[8:])
            sd_frame[xeng_id::len(sd_slots)] = ig[name]
            sd_slots[xeng_id] = 1
        if name == 'timestamp0':
            sd_timestamp = ig[name]
         # base our frame checking on the increment of xeng id 0
        f[name][datasets_index[name]] = ig[name]
        datasets_index[name] += 1
        item._changed = False
          # we have dealt with this item so continue...
    if sd_timestamp is not None and sd_frame is not None and sd_slots is not None:
        # send a signal display frame which should hopefully be full...
        print "Sending signal display frame with timestamp %i. (%i slots full out of %i available)." % (sd_timestamp, sum(sd_slots),len(sd_slots))
        ig_sd['sd_data'] = sd_frame
        ig_sd['sd_timestamp'] = sd_timestamp
        tx_sd.send_heap(ig_sd.get_heap())
        sd_timestamp = None
        sd_slots = np.zeros(len(sd_slots))
        sd_frame = np.zeros((meta['n_chans'],meta['n_bls'],meta['n_stokes'],2),dtype=sd_frame.dtype)
    idx+=1
for (name,idx) in datasets_index.iteritems():
    if idx == 1:
        print "Repacking dataset",name,"as an attribute as it is singular."
        f['/'].attrs[name] = f[name].value[0]
        f.__delitem__(name)
f.flush()
f.close()
