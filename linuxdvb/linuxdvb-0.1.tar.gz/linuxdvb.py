# Python bindings for Linux DVB API v5.1

# Copyright (C) 1999-2010 the contributors

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# Alternatively you can redistribute this file under the terms of the
# BSD license as stated below:

# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in
#    the documentation and/or other materials provided with the
#    distribution.
# 3. The names of its contributors may not be used to endorse or promote
#    products derived from this software without specific prior written
#    permission.

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED
# TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
# PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""
Python bindings for Linux DVB API v5.1
see headers in linux/dvb/ for reference
"""
import ctypes

# the following 41 lines are copied verbatim from the python v4l2 binding

_IOC_NRBITS = 8
_IOC_TYPEBITS = 8
_IOC_SIZEBITS = 14
_IOC_DIRBITS = 2

_IOC_NRSHIFT = 0
_IOC_TYPESHIFT = _IOC_NRSHIFT + _IOC_NRBITS
_IOC_SIZESHIFT = _IOC_TYPESHIFT + _IOC_TYPEBITS
_IOC_DIRSHIFT = _IOC_SIZESHIFT + _IOC_SIZEBITS

_IOC_NONE = 0
_IOC_WRITE = 1
_IOC_READ  = 2


def _IOC(dir_, type_, nr, size):
    return (
        ctypes.c_int32(dir_ << _IOC_DIRSHIFT).value |
        ctypes.c_int32(ord(type_) << _IOC_TYPESHIFT).value |
        ctypes.c_int32(nr << _IOC_NRSHIFT).value |
        ctypes.c_int32(size << _IOC_SIZESHIFT).value)


def _IOC_TYPECHECK(t):
    return ctypes.sizeof(t)


def _IO(type_, nr):
    return _IOC(_IOC_NONE, type_, nr, 0)


def _IOW(type_, nr, size):
    return _IOC(_IOC_WRITE, type_, nr, _IOC_TYPECHECK(size))


def _IOR(type_, nr, size):
    return _IOC(_IOC_READ, type_, nr, _IOC_TYPECHECK(size))


def _IOWR(type_, nr, size):
    return _IOC(_IOC_READ | _IOC_WRITE, type_, nr, _IOC_TYPECHECK(size))

# end code cribbed from v4l2 binding

def _binrange(start, stop):
    '''returns a list of ints from start to stop in increments of one binary lshift'''
    out = list()
    out.append(start)
    if start == 0:
        start = 1
        out.append(start)
    while start < stop:
        start = start << 1
        out.append(start)
    return out


#
# frontend 
#

fe_type = list([
    'FE_QPSK',
    'FE_QAM',
    'FE_OFDM',
    'FE_ATSC'
])
for i, name in enumerate(fe_type):
    exec(name + '=' + str(i))


fe_caps = dict(zip(_binrange(0, 0x800000) + _binrange(0x10000000, 0x80000000), (
    'FE_IS_STUPID',
    'FE_CAN_INVERSION_AUTO',
    'FE_CAN_FEC_1_2',
    'FE_CAN_FEC_2_3',
    'FE_CAN_FEC_3_4',
    'FE_CAN_FEC_4_5',
    'FE_CAN_FEC_5_6',
    'FE_CAN_FEC_6_7',
    'FE_CAN_FEC_7_8',
    'FE_CAN_FEC_8_9',
    'FE_CAN_FEC_AUTO',
    'FE_CAN_QPSK',
    'FE_CAN_QAM_16',
    'FE_CAN_QAM_32',
    'FE_CAN_QAM_64',
    'FE_CAN_QAM_128',
    'FE_CAN_QAM_256',
    'FE_CAN_QAM_AUTO',
    'FE_CAN_TRANSMISSION_MODE_AUTO',
    'FE_CAN_BANDWIDTH_AUTO',
    'FE_CAN_GUARD_INTERVAL_AUTO',
    'FE_CAN_HIERARCHY_AUTO',
    'FE_CAN_8VSB',
    'FE_CAN_16VSB',
    'FE_HAS_EXTENDED_CAPS',
    'FE_CAN_2G_MODULATION',
    'FE_NEEDS_BENDING',
    'FE_CAN_RECOVER',
    'FE_CAN_MUTE_TS'
)))
for val, name in fe_caps.items():
    exec(name + '=' + str(val))


class dvb_frontend_info(ctypes.Structure):
    _fields_ = [
        ('name', ctypes.c_char * 128),
        ('type', ctypes.c_uint),
        ('frequency_min', ctypes.c_uint32),
        ('frequency_max', ctypes.c_uint32),
        ('frequency_stepsize', ctypes.c_uint32),
        ('frequency_tolerance', ctypes.c_uint32),
        ('symbol_rate_min', ctypes.c_uint32),
        ('symbol_rate_max', ctypes.c_uint32),
        ('symbol_rate_tolerance', ctypes.c_uint32),
        ('notifier_delay', ctypes.c_uint32),
        ('caps', ctypes.c_uint32)
    ]


class dvb_diseqc_master_cmd(ctypes.Structure):
    _fields_ = [
        ('msg', ctypes.c_uint8 * 6),
        ('msg_len', ctypes.c_uint8)
    ]


class dvb_diseqc_slave_reply(ctypes.Structure):
    _fields_ = [
        ('msg', ctypes.c_uint8 * 4),
        ('msg_len', ctypes.c_uint8),
        ('timeout', ctypes.c_int)
    ]


fe_sec_voltage = list([
    'SEC_VOLTAGE_13',
    'SEC_VOLTAGE_18',
    'SEC_VOLTAGE_OFF'
])
for i, name in enumerate(fe_sec_voltage):
    exec(name + '=' + str(i))


fe_sec_tone_mode = list([
    'SEC_TONE_ON',
    'SEC_TONE_OFF'
])
for i, name in enumerate(fe_sec_tone_mode):
    exec(name + '=' + str(i))


fe_sec_mini_cmd = list([
    'SEC_MINI_A',
    'SEC_MINI_B'
])
for i, name in enumerate(fe_sec_mini_cmd):
    exec(name + '=' + str(i))


fe_status = dict(zip(_binrange(0x01, 0x40), (
    'FE_HAS_SIGNAL',
    'FE_HAS_CARRIER',
    'FE_HAS_VITERBI',
    'FE_HAS_SYNC',
    'FE_HAS_LOCK',
    'FE_TIMEDOUT',
    'FE_REINIT'
)))
for val, name in fe_status.items():
    exec(name + '=' + str(val))


fe_spectral_inversion = list([
    'INVERSION_OFF',
    'INVERSION_ON',
    'INVERSION_AUTO'
])
for i, name in enumerate(fe_spectral_inversion):
    exec(name + '=' + str(i))


fe_code_rate = list([
    'FEC_NONE',
    'FEC_1_2',
    'FEC_2_3',
    'FEC_3_4',
    'FEC_4_5',
    'FEC_5_6',
    'FEC_6_7',
    'FEC_7_8',
    'FEC_8_9',
    'FEC_AUTO',
    'FEC_3_5',
    'FEC_9_10'
])
for i, name in enumerate(fe_code_rate):
    exec(name + '=' + str(i))


fe_modulation = list([
    'QPSK',
    'QAM_16',
    'QAM_32',
    'QAM_64',
    'QAM_128',
    'QAM_256',
    'QAM_AUTO',
    'VSB_8',
    'VSB_16',
    'PSK_8',
    'APSK_16',
    'APSK_32',
    'DQPSK'
])
for i, name in enumerate(fe_modulation):
    exec(name + '=' + str(i))


fe_transmit_mode = list([
    'TRANSMISSION_MODE_2K',
    'TRANSMISSION_MODE_8K',
    'TRANSMISSION_MODE_AUTO',
    'TRANSMISSION_MODE_4K'
])
for i, name in enumerate(fe_transmit_mode):
    exec(name + '=' + str(i))


fe_bandwidth = list([
    'BANDWIDTH_8_MHZ',
    'BANDWIDTH_7_MHZ',
    'BANDWIDTH_6_MHZ',
    'BANDWIDTH_AUTO'
])
for i, name in enumerate(fe_bandwidth):
    exec(name + '=' + str(i))


fe_guard_interval = list([
    'GUARD_INTERVAL_1_32',
    'GUARD_INTERVAL_1_16',
    'GUARD_INTERVAL_1_8',
    'GUARD_INTERVAL_1_4',
    'GUARD_INTERVAL_AUTO'
])
for i, name in enumerate(fe_guard_interval):
    exec(name + '=' + str(i))


fe_hierarchy = list([
    'HIERARCHY_NONE',
    'HIERARCHY_1',
    'HIERARCHY_2',
    'HIERARCHY_4',
    'HIERARCHY_AUTO'
])
for i, name in enumerate(fe_hierarchy):
    exec(name + '=' + str(i))


class dvb_qpsk_parameters(ctypes.Structure):
    _fields_ = [
        ('symbol_rate', ctypes.c_uint32),
        ('fec_inner', ctypes.c_uint)
    ]


class dvb_qam_parameters(ctypes.Structure):
    _fields_ = [
        ('symbol_rate', ctypes.c_uint32),
        ('fec_inner', ctypes.c_uint),
        ('modulation', ctypes.c_uint)
    ]


class dvb_vsb_parameters(ctypes.Structure):
    _fields_ = [
        ('modulation', ctypes.c_uint)
    ]


class dvb_ofdm_parameters(ctypes.Structure):
    _fields_ = [
        ('bandwidth', ctypes.c_uint),
        ('code_rate_HP', ctypes.c_uint),
        ('code_rate_LP', ctypes.c_uint),
        ('constellation', ctypes.c_uint),
        ('transmission_mode', ctypes.c_uint),
        ('guard_interval', ctypes.c_uint),
        ('hierarchy_information', ctypes.c_uint)
    ]


class dvb_frontend_parameters(ctypes.Structure):
    class _u(ctypes.Union):
        _fields_ = [
            ('qpsk', dvb_qpsk_parameters),
            ('qam', dvb_qam_parameters),
            ('ofdm', dvb_ofdm_parameters),
            ('vsb', dvb_vsb_parameters)
        ]

    _fields_ = [
        ('frequency', ctypes.c_uint32),
        ('inversion', ctypes.c_uint),
        ('u', _u)
    ]


class dvb_frontend_event(ctypes.Structure):
    _fields_ = [
        ('status', ctypes.c_uint),
        ('parameters', dvb_frontend_parameters)
    ]


s2api_commands = list([
    'DTV_UNDEFINED',
    'DTV_TUNE',
    'DTV_CLEAR',
    'DTV_FREQUENCY',
    'DTV_MODULATION',
    'DTV_BANDWIDTH_HZ',
    'DTV_INVERSION',
    'DTV_DISEQC_MASTER',
    'DTV_SYMBOL_RATE',
    'DTV_INNER_FEC',
    'DTV_VOLTAGE',
    'DTV_TONE',
    'DTV_PILOT',
    'DTV_ROLLOFF',
    'DTV_DISEQC_SLAVE_REPLY',
    'DTV_FE_CAPABILITY_COUNT',
    'DTV_FE_CAPABILITY',
    'DTV_DELIVERY_SYSTEM',
    'DTV_ISDBT_PARTIAL_RECEPTION',
    'DTV_ISDBT_SOUND_BROADCASTING',
    'DTV_ISDBT_SB_SUBCHANNEL_ID',
    'DTV_ISDBT_SB_SEGMENT_IDX',
    'DTV_ISDBT_SB_SEGMENT_COUNT',
    'DTV_ISDBT_LAYERA_FEC',
    'DTV_ISDBT_LAYERA_MODULATION',
    'DTV_ISDBT_LAYERA_SEGMENT_COUNT',
    'DTV_ISDBT_LAYERA_TIME_INTERLEAVING',
    'DTV_ISDBT_LAYERB_FEC',
    'DTV_ISDBT_LAYERB_MODULATION',
    'DTV_ISDBT_LAYERB_SEGMENT_COUNT',
    'DTV_ISDBT_LAYERB_TIME_INTERLEAVING',
    'DTV_ISDBT_LAYERC_FEC',
    'DTV_ISDBT_LAYERC_MODULATION',
    'DTV_ISDBT_LAYERC_SEGMENT_COUNT',
    'DTV_ISDBT_LAYERC_TIME_INTERLEAVING',
    'DTV_API_VERSION',
    'DTV_CODE_RATE_HP',
    'DTV_CODE_RATE_LP',
    'DTV_GUARD_INTERVAL',
    'DTV_TRANSMISSION_MODE',
    'DTV_HIERARCHY',
    'DTV_ISDBT_LAYER_ENABLED',
    'DTV_ISDBS_TS_ID'
])
for i, name in enumerate(s2api_commands):
    exec(name + '=' + str(i))
DTV_MAX_COMMAND = DTV_ISDBS_TS_ID


fe_pilot = list([
    'PILOT_ON',
    'PILOT_OFF',
    'PILOT_AUTO'
])
for i, name in enumerate(fe_pilot):
    exec(name + '=' + str(i))


fe_rolloff = list([
    'ROLLOFF_35',
    'ROLLOFF_20',
    'ROLLOFF_25',
    'ROLLOFF_AUTO'
])
for i, name in enumerate(fe_rolloff):
    exec(name + '=' + str(i))


fe_delivery_system = list([
    'SYS_UNDEFINED',
    'SYS_DVBC_ANNEX_AC',
    'SYS_DVBC_ANNEX_B',
    'SYS_DVBT',
    'SYS_DSS',
    'SYS_DVBS',
    'SYS_DVBS2',
    'SYS_DVBH',
    'SYS_ISDBT',
    'SYS_ISDBS',
    'SYS_ISDBC',
    'SYS_ATSC',
    'SYS_ATSCMH',
    'SYS_DMBTH',
    'SYS_CMMB',
    'SYS_DAB',
    'SYS_DCII_C_QPSK',
    'SYS_DCII_I_QPSK',
    'SYS_DCII_Q_QPSK',
    'SYS_DCII_C_OQPSK'
])
for i, name in enumerate(fe_delivery_system):
    exec(name + '=' + str(i))


class dtv_cmds_h(ctypes.Structure):
    _fields_ = [
        ('name', ctypes.c_char_p),
        ('cmd', ctypes.c_uint32),
        ('set', ctypes.c_uint32),
        ('buffer', ctypes.c_uint32),
        ('reserved', ctypes.c_uint32)
    ]


class dtv_property(ctypes.Structure):
    class _u(ctypes.Union):
        class _s(ctypes.Structure):
            _fields_ = [
                ('data', ctypes.c_uint8 * 32),
                ('len', ctypes.c_uint32),
                ('reserved1', ctypes.c_uint32 * 3),
                ('reserved2', ctypes.c_void_p)
            ]


        _fields_ = [
            ('data', ctypes.c_uint32),
            ('buffer', _s)
        ]


    _fields_ = [
        ('cmd', ctypes.c_uint32),
        ('reserved', ctypes.c_uint32 * 3),
        ('u', _u),
        ('result', ctypes.c_int)
    ]

    _pack_ = True


class dtv_properties(ctypes.Structure):
    _fields_ = [
        ('num', ctypes.c_uint32),
        ('props', ctypes.POINTER(dtv_property))
    ]


FE_SET_PROPERTY = _IOW('o', 82, dtv_properties)
FE_GET_PROPERTY = _IOR('o', 83, dtv_properties)

DTV_IOCTL_MAX_MSGS = 64
FE_TUNE_MODE_ONESHOT = 0x01

FE_GET_INFO = _IOR('o', 61, dvb_frontend_info)

FE_DISEQC_RESET_OVERLOAD = _IO('o', 62)
FE_DISEQC_SEND_MASTER_CMD = _IOW('o', 63, dvb_diseqc_master_cmd)
FE_DISEQC_RECV_SLAVE_REPLY = _IOR('o', 64, dvb_diseqc_slave_reply)
FE_DISEQC_SEND_BURST = _IO('o', 65)

FE_SET_TONE = _IO('o', 66)
FE_SET_VOLTAGE = _IO('o', 67)
FE_ENABLE_HIGH_LNB_VOLTAGE = _IO('o', 68)

FE_READ_STATUS = _IOR('o', 69, ctypes.c_uint)
FE_READ_BER = _IOR('o', 70, ctypes.c_uint32)
FE_READ_SIGNAL_STRENGTH = _IOR('o', 71, ctypes.c_uint16)
FE_READ_SNR = _IOR('o', 72, ctypes.c_uint16)
FE_READ_UNCORRECTED_BLOCKS = _IOR('o', 73, ctypes.c_uint32)

FE_SET_FRONTEND = _IOW('o', 76, dvb_frontend_parameters)
FE_GET_FRONTEND = _IOR('o', 77, dvb_frontend_parameters)
FE_SET_FRONTEND_TUNE_MODE = _IO('o', 81)
FE_GET_EVENT = _IOR('o', 78, dvb_frontend_event)

FE_DISHNETWORK_SEND_LEGACY_CMD = _IO('o', 80)


#
# demux
#


DMX_FILTER_SIZE = 16


dmx_output = list([
    'DMX_OUT_DECODER',
    'DMX_OUT_TAP',
    'DMX_OUT_TS_TAP',
    'DMX_OUT_TSDEMUX_TAP'
])
for i, name in enumerate(dmx_output):
    exec(name + '=' + str(i))


dmx_input = list([
    'DMX_IN_FRONTEND',
    'DMX_IN_DVR'
])
for i, name in enumerate(dmx_input):
    exec(name + '=' + str(i))


dmx_pes_type = list([
    'DMX_PES_AUDIO0',
    'DMX_PES_VIDEO0',
    'DMX_PES_TELETEXT0',
    'DMX_PES_SUBTITLE0',
    'DMX_PES_PCR0',
    'DMX_PES_AUDIO1',
    'DMX_PES_VIDEO1',
    'DMX_PES_TELETEXT1',
    'DMX_PES_SUBTITLE1',
    'DMX_PES_PCR1',
    'DMX_PES_AUDIO2',
    'DMX_PES_VIDEO2',
    'DMX_PES_TELETEXT2',
    'DMX_PES_SUBTITLE2',
    'DMX_PES_PCR2',
    'DMX_PES_AUDIO3',
    'DMX_PES_VIDEO3',
    'DMX_PES_TELETEXT3',
    'DMX_PES_SUBTITLE3',
    'DMX_PES_PCR3',
    'DMX_PES_OTHER'
])
for i, name in enumerate(dmx_pes_type):
    exec(name + '=' + str(i))


DMX_PES_AUDIO = DMX_PES_AUDIO0
DMX_PES_VIDEO =  DMX_PES_VIDEO0
DMX_PES_TELETEXT = DMX_PES_TELETEXT0
DMX_PES_SUBTITLE = DMX_PES_SUBTITLE0
DMX_PES_PCR = DMX_PES_PCR0


class dmx_filter(ctypes.Structure):
    _fields_ = [
        ('filter', ctypes.c_uint8 * DMX_FILTER_SIZE),
        ('mask', ctypes.c_uint8 * DMX_FILTER_SIZE),
        ('mode', ctypes.c_uint8 * DMX_FILTER_SIZE)
    ]


class dmx_sct_filter_params(ctypes.Structure):
    _fields_ = [
        ('pid', ctypes.c_uint16),
        ('filter', dmx_filter),
        ('timeout', ctypes.c_uint32),
        ('flags', ctypes.c_uint32)
    ]


DMX_CHECK_CRC = 0x01
DMX_ONESHOT = 0x02
DMX_IMMEDIATE_START = 0x04
DMX_KERNEL_CLIENT = 0x8000


class dmx_pes_filter_params(ctypes.Structure):
    _fields_ = [
        ('pid', ctypes.c_uint16),
        ('input', ctypes.c_uint),
        ('output', ctypes.c_uint),
        ('pes_type', ctypes.c_uint),
        ('flags', ctypes.c_uint32)
    ]


class dmx_caps(ctypes.Structure):
    _fields_ = [
        ('caps', ctypes.c_uint32),
        ('num_decoders', ctypes.c_uint)
    ]


dmx_source = dict(zip(list(range(0, 4)) + list(range(16, 20)), (
    'DMX_SOURCE_FRONT0',
    'DMX_SOURCE_FRONT1',
    'DMX_SOURCE_FRONT2',
    'DMX_SOURCE_FRONT3',
    'DMX_SOURCE_DVR0',
    'DMX_SOURCE_DVR1',
    'DMX_SOURCE_DVR2',
    'DMX_SOURCE_DVR3'
)))
for val, name in dmx_source.items():
    exec(name + '=' + str(val))


class dmx_stc(ctypes.Structure):
    _fields_ = [
        ('num', ctypes.c_uint),
        ('base', ctypes.c_uint),
        ('stc', ctypes.c_uint64)
    ]


DMX_START = _IO('o', 41)
DMX_STOP = _IO('o', 42)
DMX_SET_FILTER = _IOW('o', 43, dmx_sct_filter_params)
DMX_SET_PES_FILTER = _IOW('o', 44, dmx_pes_filter_params)
DMX_SET_BUFFER_SIZE = _IO('o', 45)
DMX_GET_PES_PIDS = _IOR('o', 47, ctypes.c_uint16 * 5)
DMX_GET_CAPS = _IOR('o', 48, dmx_caps)
DMX_SET_SOURCE = _IOW('o', 49, ctypes.c_uint)
DMX_GET_STC = _IOWR('o', 50, dmx_stc)
DMX_ADD_PID = _IOW('o', 51, ctypes.c_uint16)
DMX_REMOVE_PID = _IOW('o', 52, ctypes.c_uint16)


#
# audio
#


audio_stream_source = list([
    'AUDIO_SOURCE_DEMUX',
    'AUDIO_SOURCE_MEMORY'
])
for i, name in enumerate(audio_stream_source):
    exec(name + '=' + str(i))


audio_play_state = list([
    'AUDIO_STOPPED',
    'AUDIO_PLAYING',
    'AUDIO_PAUSED'
])
for i, name in enumerate(audio_play_state):
    exec(name + '=' + str(i))


audio_channel_select = list([
    'AUDIO_STEREO',
    'AUDIO_MONO_LEFT',
    'AUDIO_MONO_RIGHT',
    'AUDIO_MONO',
    'AUDIO_STEREO_SWAPPED'
])
for i, name in enumerate(audio_channel_select):
    exec(name + '=' + str(i))


class audio_mixer(ctypes.Structure):
    _fields_ = [
        ('volume_left', ctypes.c_uint),
        ('volume_right', ctypes.c_uint)
    ]


class audio_status(ctypes.Structure):
    _fields_ = [
        ('AV_sync_state', ctypes.c_int),
        ('mute_state', ctypes.c_int),
        ('play_state', ctypes.c_uint),
        ('stream_source', ctypes.c_uint),
        ('channel_select', ctypes.c_uint),
        ('bypass_mode', ctypes.c_int),
        ('mixer_state', ctypes.c_uint)
    ]


class audio_karaoke(ctypes.Structure):
    _fields_ = [
        ('vocal1', ctypes.c_int),
        ('vocal2', ctypes.c_int),
        ('melody', ctypes.c_int)
    ]


audio_caps = dict(zip(_binrange(0x01, 0x100), (
    'AUDIO_CAP_DTS',
    'AUDIO_CAP_LPCM',
    'AUDIO_CAP_MP1',
    'AUDIO_CAP_MP2',
    'AUDIO_CAP_MP3',
    'AUDIO_CAP_AAC',
    'AUDIO_CAP_OGG',
    'AUDIO_CAP_SDDS',
    'AUDIO_CAP_AC3'
)))
for val, name in audio_caps.items():
    exec(name + '=' + str(val))


AUDIO_STOP = _IO('o', 1)
AUDIO_PLAY = _IO('o', 2)
AUDIO_PAUSE = _IO('o', 3)
AUDIO_CONTINUE = _IO('o', 4)
AUDIO_SELECT_SOURCE = _IO('o', 5)
AUDIO_SET_MUTE = _IO('o', 6)
AUDIO_SET_AV_SYNC = _IO('o', 7)
AUDIO_SET_BYPASS_MODE = _IO('o', 8)
AUDIO_CHANNEL_SELECT = _IO('o', 9)
AUDIO_GET_STATUS = _IOR('o', 10, audio_status)

AUDIO_GET_CAPABILITIES = _IOR('o', 11, ctypes.c_uint)
AUDIO_CLEAR_BUFFER = _IO('o',  12)
AUDIO_SET_ID = _IO('o', 13)
AUDIO_SET_MIXER = _IOW('o', 14, audio_mixer)
AUDIO_SET_STREAMTYPE = _IO('o', 15)
AUDIO_SET_EXT_ID = _IO('o', 16)
AUDIO_SET_ATTRIBUTES = _IOW('o', 17, ctypes.c_uint16)
AUDIO_SET_KARAOKE = _IOW('o', 18, audio_karaoke)

AUDIO_GET_PTS = _IOR('o', 19, ctypes.c_uint64)
AUDIO_BILINGUAL_CHANNEL_SELECT = _IO('o', 20)


#
# ca
#


ca_slot_type = dict(zip([1, 2, 4, 8, 128], (
    'CA_CI',
    'CA_CI_LINK',
    'CA_CI_PHYS',
    'CA_DESCR',
    'CA_SC'
)))
for val, name in ca_slot_type.items():
    exec(name + '=' + str(val))


ca_slot_flags = list([
    'CA_CI_MODULE_PRESENT',
    'CA_CI_MODULE_READY'
])
for i, name in enumerate(ca_slot_flags):
    exec(name + '=' + str(i))


ca_descr_type = dict(zip([1, 2, 4], (
    'CA_ECD',
    'CA_NDS',
    'CA_DSS'
)))
for val, name in ca_descr_type.items():
    exec(name + '=' + str(val))


class ca_slot_info(ctypes.Structure):
    _fields_ = [
        ('num', ctypes.c_int),
        ('type', ctypes.c_int),
        ('flags', ctypes.c_uint)
    ]


class ca_descr_info(ctypes.Structure):
    _fields_ = [
        ('num', ctypes.c_uint),
        ('type', ctypes.c_uint)
    ]


class ca_caps(ctypes.Structure):
    _fields_ = [
        ('slot_num', ctypes.c_uint),
        ('slot_type', ctypes.c_uint),
        ('descr_num', ctypes.c_uint),
        ('descr_type', ctypes.c_uint)
    ]


class ca_msg(ctypes.Structure):
    _fields_ = [
        ('index', ctypes.c_uint),
        ('type', ctypes.c_uint),
        ('length', ctypes.c_uint),
        ('msg', ctypes.c_char * 256)
    ]


class ca_descr(ctypes.Structure):
    _fields_ = [
        ('index', ctypes.c_uint),
        ('parity', ctypes.c_uint),
        ('cw', ctypes.c_char * 256)
    ]


class ca_pid(ctypes.Structure):
    _fields_ = [
        ('pid', ctypes.c_uint),
        ('index', ctypes.c_int)
    ]


CA_RESET = _IO('o', 128)
CA_GET_CAP = _IOR('o', 129, ca_caps)
CA_GET_SLOT_INFO = _IOR('o', 130, ca_slot_info)
CA_GET_DESCR_INFO = _IOR('o', 131, ca_descr_info)
CA_GET_MSG = _IOR('o', 132, ca_msg)
CA_SEND_MSG = _IOW('o', 133, ca_msg)
CA_SET_DESCR = _IOW('o', 134, ca_descr)
CA_SET_PID = _IOW('o', 135, ca_pid)


#
# net
#


dvb_net_feedtype = list([
    'DVB_NET_FEEDTYPE_MPE',
    'DVB_NET_FEEDTYPE_ULE'
])
for i, name in enumerate(dvb_net_feedtype):
    exec(name + '=' + str(i))


class dvb_net_if(ctypes.Structure):
    _fields_ = [
        ('pid', ctypes.c_uint16),
        ('if_num', ctypes.c_uint16),
        ('feedtype', ctypes.c_uint8)
    ]


NET_ADD_IF = _IOWR('o', 52, dvb_net_if)
NET_REMOVE_IF = _IO('o', 53)
NET_GET_IF = _IOWR('o', 54, dvb_net_if)


#
# osd
#


OSD_Command = list([
    'OSD_Placeholder',
    'OSD_Close',
    'OSD_Open',
    'OSD_Show',
    'OSD_Hide',
    'OSD_Clear',
    'OSD_Fill',
    'OSD_SetColor',
    'OSD_SetPalette',
    'OSD_SetTrans',
    'OSD_SetPixel',
    'OSD_GetPixel',
    'OSD_SetRow',
    'OSD_SetBlock',
    'OSD_FillRow',
    'OSD_FillBlock',
    'OSD_Line',
    'OSD_Query',
    'OSD_Test',
    'OSD_Text',
    'OSD_SetWindow',
    'OSD_MoveWindow',
    'OSD_OpenRaw'
])
for i, name in enumerate(OSD_Command):
    exec(name + '=' + str(i))


class osd_cmd(ctypes.Structure):
    _fields_ = [
        ('cmd', ctypes.c_uint),
        ('x0', ctypes.c_int),
        ('y0', ctypes.c_int),
        ('x1', ctypes.c_int),
        ('y1', ctypes.c_int),
        ('color', ctypes.c_int),
        ('data', ctypes.c_void_p)
    ]


osd_raw_window = list([
    'OSD_BITMAP1',
    'OSD_BITMAP2',
    'OSD_BITMAP4',
    'OSD_BITMAP8',
    'OSD_BITMAP1HR',
    'OSD_BITMAP2HR',
    'OSD_BITMAP4HR',
    'OSD_BITMAP8HR',
    'OSD_YCRCB422',
    'OSD_YCRCB444',
    'OSD_YCRCB444HR',
    'OSD_VIDEOTSIZE',
    'OSD_VIDEOHSIZE',
    'OSD_VIDEOQSIZE',
    'OSD_VIDEODSIZE',
    'OSD_VIDEOTHSIZE',
    'OSD_VIDEOTQSIZE',
    'OSD_VIDEOTDSIZE',
    'OSD_VIDEONSIZE',
    'OSD_CURSOR'
])
for i, name in enumerate(osd_raw_window):
    exec(name + '=' + str(i))


class osd_cap(ctypes.Structure):
    _fields_ = [
        ('cmd', ctypes.c_int),
        ('val', ctypes.c_long)
    ]


OSD_SEND_CMD = _IOW('o', 160, osd_cmd)
OSD_GET_CAPABILITY = _IOR('o', 161, osd_cap)


#
# video
#


video_format = list([
    'VIDEO_FORMAT_4_3',
    'VIDEO_FORMAT_16_9',
    'VIDEO_FORMAT_221_1'
])
for i, name in enumerate(video_format):
    exec(name + '=' + str(i))


video_system = list([
    'VIDEO_SYSTEM_PAL',
    'VIDEO_SYSTEM_NTSC',
    'VIDEO_SYSTEM_PALN',
    'VIDEO_SYSTEM_PALNc',
    'VIDEO_SYSTEM_PALM',
    'VIDEO_SYSTEM_NTSC60',
    'VIDEO_SYSTEM_PAL60',
    'VIDEO_SYSTEM_PALM60'
])
for i, name in enumerate(video_system):
    exec(name + '=' + str(i))


video_displayformat = list([
    'VIDEO_PAN_SCAN',
    'VIDEO_LETTER_BOX',
    'VIDEO_CENTER_CUT_OUT'
])
for i, name in enumerate(video_displayformat):
    exec(name + '=' + str(i))


class video_size(ctypes.Structure):
    _fields_ = [
        ('w', ctypes.c_int),
        ('h', ctypes.c_int),
        ('aspect_ratio', ctypes.c_uint)
    ]


video_stream_source = list([
    'VIDEO_SOURCE_DEMUX',
    'VIDEO_SOURCE_MEMORY'
])
for i, name in enumerate(video_stream_source):
    exec(name + '=' + str(i))


video_play_state = list([
    'VIDEO_STOPPED',
    'VIDEO_PLAYING',
    'VIDEO_FREEZED'
])
for i, name in enumerate(video_play_state):
    exec(name + '=' + str(i))


video_decoder_commands = list([
    'VIDEO_CMD_PLAY',
    'VIDEO_CMD_STOP',
    'VIDEO_CMD_FREEZE',
    'VIDEO_CMD_CONTINUE'
])
for i, name in enumerate(video_decoder_commands):
    exec(name + '=' + str(i))


VIDEO_CMD_FREEZE_TO_BLACK = 1

VIDEO_CMD_STOP_TO_BLACK = 1
VIDEO_CMD_STOP_IMMEDIATELY = 2

VIDEO_PLAY_FMT_NONE = 0
VIDEO_PLAY_FMT_GOP = 1


class video_command(ctypes.Structure):
    class _u(ctypes.Union):
        class _s1(ctypes.Structure):
            _fields_ = [('pts', ctypes.c_uint64)]
        class _s2(ctypes.Structure):
            _fields_ = [
                ('speed', ctypes.c_int32),
                ('format', ctypes.c_uint32)
            ]
        class _s3(ctypes.Structure):
            _fields_ = [('data', ctypes.c_uint32 * 16)]
        
        _fields_ = [
            ('stop', _s1),
            ('play', _s2),
            ('raw', _s3)
        ]
    
    _fields_ = [
        ('cmd', ctypes.c_uint32),
        ('flags', ctypes.c_uint32),
        ('u', _u)
    ]


video_vsync_field = list([
    'VIDEO_VSYNC_FIELD_UNKNOWN',
    'VIDEO_VSYNC_FIELD_ODD',
    'VIDEO_VSYNC_FIELD_EVEN',
    'VIDEO_VSYNC_FIELD_PROGRESSIVE'
])
for i, name in enumerate(video_vsync_field):
    exec(name + '=' + str(i))


video_event_type = list([
    'VIDEO_EVENT_PLACEHOLDER',
    'VIDEO_EVENT_SIZE_CHANGED',
    'VIDEO_EVENT_FRAME_RATE_CHANGED',
    'VIDEO_EVENT_DECODER_STOPPED',
    'VIDEO_EVENT_VSYNC'
])
for i, name in enumerate(video_event_type):
    exec(name + '=' + str(i))


class video_event(ctypes.Structure):
    class _u(ctypes.Union):
        _fields_ = [
            ('size', video_size),
            ('frame_rate', ctypes.c_uint),
            ('vsync_field', ctypes.c_char)
        ]
    
    _fields_ = [
        ('type', ctypes.c_int32),
        ('timestamp', ctypes.c_long),
        ('u', _u)
    ]


class video_status(ctypes.Structure):
    _fields_ = [
        ('video_blank', ctypes.c_int),
        ('play_state', ctypes.c_int),
        ('stream_source', ctypes.c_int),
        ('video_format', ctypes.c_int),
        ('display_format', ctypes.c_int)
    ]


class video_still_picture(ctypes.Structure):
    _fields_ = [
        ('iFrame', ctypes.c_char_p),
        ('size', ctypes.c_int32)
    ]


class video_highlight(ctypes.Structure):
    _fields_ = [
        ('active', ctypes.c_int),
        ('contrast1', ctypes.c_uint8),
        ('contrast2', ctypes.c_uint8),
        ('color1', ctypes.c_uint8),
        ('color2', ctypes.c_uint8),
        ('ypos', ctypes.c_uint32),
        ('xpos', ctypes.c_uint32)
    ]


class video_spu(ctypes.Structure):
    _fields_ = [
        ('active', ctypes.c_int),
        ('stream_id', ctypes.c_int)
    ]


class video_spu_palette(ctypes.Structure):
    _fields_ = [
        ('length', ctypes.c_int),
        ('palette', ctypes.POINTER(ctypes.c_uint8))
    ]


class video_navi_pack(ctypes.Structure):
    _fields_ = [
        ('length', ctypes.c_int),
        ('data', ctypes.c_uint8 * 1024)
    ]


video_attributes = ctypes.c_uint16


video_caps = dict(zip(_binrange(0x01, 0x40), (
    'VIDEO_CAP_MPEG1',
    'VIDEO_CAP_MPEG2',
    'VIDEO_CAP_SYS',
    'VIDEO_CAP_PROG',
    'VIDEO_CAP_SPU',
    'VIDEO_CAP_NAVI',
    'VIDEO_CAP_CSS'
)))
for val, name in video_caps.items():
    exec(name + '=' + str(val))


VIDEO_STOP = _IO('o', 21)
VIDEO_PLAY = _IO('o', 22)
VIDEO_FREEZE = _IO('o', 23)
VIDEO_CONTINUE = _IO('o', 24)
VIDEO_SELECT_SOURCE = _IO('o', 25)
VIDEO_SET_BLANK = _IO('o', 26)
VIDEO_GET_STATUS = _IOR('o', 27, video_status)
VIDEO_GET_EVENT = _IOR('o', 28, video_event)
VIDEO_SET_DISPLAY_FORMAT = _IO('o', 29)
VIDEO_STILLPICTURE = _IOW('o', 30, video_still_picture)
VIDEO_FAST_FORWARD = _IO('o', 31)
VIDEO_SLOWMOTION = _IO('o', 32)
VIDEO_GET_CAPABILITIES = _IOR('o', 33, ctypes.c_uint)
VIDEO_CLEAR_BUFFER = _IO('o',  34)
VIDEO_SET_ID = _IO('o', 35)
VIDEO_SET_STREAMTYPE = _IO('o', 36)
VIDEO_SET_FORMAT = _IO('o', 37)
VIDEO_SET_SYSTEM = _IO('o', 38)
VIDEO_SET_HIGHLIGHT = _IOW('o', 39, video_highlight)
VIDEO_SET_SPU = _IOW('o', 50, video_spu)
VIDEO_SET_SPU_PALETTE = _IOW('o', 51, video_spu_palette)
VIDEO_GET_NAVI = _IOR('o', 52, video_navi_pack)
VIDEO_SET_ATTRIBUTES = _IO('o', 53)
VIDEO_GET_SIZE = _IOR('o', 55, video_size)
VIDEO_GET_FRAME_RATE = _IOR('o', 56, ctypes.c_uint)
VIDEO_GET_PTS = _IOR('o', 57, ctypes.c_uint64)
VIDEO_GET_FRAME_COUNT = _IOR('o', 58, ctypes.c_uint64)
VIDEO_COMMAND = _IOWR('o', 59, video_command)
VIDEO_TRY_COMMAND = _IOWR('o', 60, video_command)
