"""
Setup and unique functionality for the wide-band correlator modes.

Revisions:
2011-07-07  PVP  Initial revision.
"""
import construct, corr_functions

# f-engine control register
register_fengine_control = construct.BitStruct('control',
    construct.Padding(32 - 20 - 1),             # 21 - 31
    construct.Flag('tvg_noise_sel'),            # 20
    construct.Flag('tvg_ffdel_sel'),            # 19
    construct.Flag('tvg_pkt_sel'),              # 18
    construct.Flag('tvg_ct_sel'),               # 17
    construct.Flag('tvg_en'),                   # 16
    construct.Padding(16 - 13 - 1),             # 14 - 15
    construct.Flag('adc_protect_disable'),      # 13
    construct.Flag('flasher_en'),               # 12
    construct.Padding(12 - 9 - 1),              # 10 - 11
    construct.Flag('gbe_enable'),               # 9
    construct.Flag('gbe_rst'),                  # 8
    construct.Padding(8 - 3 - 1),               # 4 - 7
    construct.Flag('clr_status'),               # 3
    construct.Flag('arm'),                      # 2
    construct.Flag('soft_sync'),                # 1
    construct.Flag('mrst'))                     # 0

# f-engine status
register_fengine_status = construct.BitStruct('fstatus0',
    construct.Padding(32 - 17 - 1),     # 18 - 31
    construct.Flag('xaui_lnkdn'),       # 17
    construct.Flag('xaui_over'),        # 16
    construct.Padding(16 - 5 - 1),      # 6 - 15
    construct.Flag('clk_err'),          # 5
    construct.Flag('adc_disabled'),     # 4
    construct.Flag('ct_error'),         # 3
    construct.Flag('adc_overrange'),    # 2
    construct.Flag('fft_overrange'),    # 1
    construct.Flag('quant_overrange'))  # 0

# x-engine control register
register_xengine_control = construct.BitStruct('ctrl',
    construct.Padding(32 - 16 - 1),     # 17 - 31
    construct.Flag('gbe_out_enable'),   # 16
    construct.Flag('gbe_rst'),          # 15
    construct.Padding(15 - 12 - 1),     # 13 - 14
    construct.Flag('flasher_en'),       # 12
    construct.Flag('gbe_out_rst'),      # 11
    construct.Flag('loopback_mux_rst'), # 10
    construct.Flag('gbe_enable'),       # 9
    construct.Flag('cnt_rst'),          # 8
    construct.Flag('clr_status'),       # 7
    construct.Padding(7 - 0 - 1),       # 1 - 6
    construct.Flag('vacc_rst'))         # 0

# x-engine status
register_xengine_status = construct.BitStruct('xstatus0',
    construct.Padding(32 - 18 - 1),     # 19 - 31
    construct.Flag('gbe_lnkdn'),        # 18
    construct.Flag('xeng_err'),         # 17
    construct.Padding(17 - 5 - 1),      # 6 - 16
    construct.Flag('vacc_err'),         # 5
    construct.Flag('rx_bad_pkt'),       # 4
    construct.Flag('rx_bad_frame'),     # 3
    construct.Flag('tx_over'),          # 2
    construct.Flag('pkt_reord_err'),    # 1
    construct.Flag('pack_err'))         # 0

# end
