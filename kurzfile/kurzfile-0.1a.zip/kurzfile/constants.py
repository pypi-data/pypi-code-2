# -*- coding:utf-8 -*-
#
# kurzfile/constants.py
#
"""Constants for the kurzfile package."""

KNOWN_FILETYPES = ('PRAM', 'SROM')
OBJECT_TYPES = {
    0x90: 'Program', # 144
    0x94: 'Keymap', # 148
    0x98: 'Sample Header', # 152
    0x9C: 'Setup (K2000)', # 156
    0xA4: 'Setup (K2500)', # 164
    0xB0: 'KDFX Studio', # 176
    0xB4: 'KDFX Preset', # 180
    0xBC: 'KDFX Algorithm', # 188
    0x64: 'Table', # 100
    0x67: 'Intonation Table', # 103
    0x68: 'Velocity Map', # 104
    0x69: 'Pressure Map', # 105
    0x6F: 'QA-Bank', # 111
    0x70: 'Song', # 112
    0x71: 'Effect', # 113
}
