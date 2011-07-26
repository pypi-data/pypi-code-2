"""
Setup and unique functionality for the narrow-band correlator modes.

Revisions:
2011-07-07  PVP  Initial revision.
"""
import construct, corr_functions

register_fengine_fstatus = construct.BitStruct('fstatus',
    construct.BitField('coarse_bits', 5),       # 
    construct.BitField('fine_bits', 5),         # 
    construct.Padding(4),                       # 
    construct.Flag('xaui_lnkdn'),               # 
    construct.Flag('xaui_over'),                # 
    construct.Padding(9),                       # 
    construct.Flag('ct_err'),                   # 6
    construct.Flag('adc1_overrange'),           # 5
    construct.Flag('adc0_overrange'),           # 4
    construct.Flag('coarse1_fft_overrange'),    # 3
    construct.Flag('coarse0_fft_overrange'),    # 2
    construct.Flag('fine_fft_overrange'),       # 1
    construct.Flag('quant_overrange'))          # 0

register_fengine_coarse_control = construct.BitStruct('coarse_ctrl',
    construct.Padding(32 - 10 - 10 - 3),        # 23 - 31
    construct.BitField('fft_shift', 10),        # 13 - 22
    construct.BitField('channel_select', 10),   # 3 - 12
    construct.Flag('mixer_select'),             # 2
    construct.Flag('snap_data_select'),         # 1
    construct.Flag('snap_pol_select'))          # 0

register_fengine_fine_control = construct.BitStruct('fine_ctrl',
    construct.Padding(32 - 13 - 1 - 2 - 1),     # 17 - 31
    construct.BitField('fft_shift', 13),        # 4 - 16
    construct.Flag('quant_snap_select'),        # 3
    construct.BitField('snap_data_select', 2),  # 1 - 2
    construct.Flag('snap_pol_select'))          # 0

register_fengine_control = construct.BitStruct('control',
    construct.Padding(9),                   # 23 - 31
    construct.Flag('snap_tx_select'),       # 22
    construct.Flag('fine_chan_tvg_post'),   # 21
    construct.Flag('adc_tvg'),              # 20
    construct.Flag('fdfs_tvg'),             # 19
    construct.Flag('packetiser_tvg'),       # 18
    construct.Flag('ct_tvg'),               # 17
    construct.Flag('tvg_en'),               # 16
    construct.Padding(6),                   # 10 - 15
    construct.Flag('gbe_enable'),           # 9
    construct.Flag('gbe_rst'),              # 8
    construct.Padding(4),                   # 4 - 7
    construct.Flag('clr_status'),           # 3
    construct.Flag('arm'),                  # 2
    construct.Flag('man_sync'),             # 1
    construct.Flag('sys_rst'))              # 0

# set the coarse FFT per-stage shift
def coarse_fft_shift_set_all(correlator, shift = -1):
    if shift < 0:
        shift = correlator.config['coarse_fft_shift']
    corr_functions.write_masked_register(correlator.ffpgas, register_fengine_coarse_control, fft_shift = shift)
    correlator.syslogger.info('Set coarse FFT shift patterns on all F-engines to 0x%x.' % shift)
#def coarse_fft_shift_get_all(correlator):
#  rv={}
#  for ant in range(correlator.config['n_ants']):
#    for pol in correlator.config['pols']:
#      ffpga_n, xfpga_n, fxaui_n, xxaui_n, feng_input = correlator.get_ant_location(ant, pol)
#      rv[(ant, pol)] = correlator.ffpgas[ffpga_n].read_uint('crs_fft_shift')
#  return rv

# set the fine FFT per-stage shift
def fine_fft_shift_set_all(correlator, shift = -1):
    if shift < 0:
        shift = correlator.config['fine_fft_shift']
    corr_functions.write_masked_register(correlator.ffpgas, register_fengine_fine_control, fft_shift = shift)
    correlator.syslogger.info('Set fine FFT shift patterns on all F-engines to 0x%x.' % shift)

# end
