#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

def determine_wm():
    if 'kde' in os.environ.get('DESKTOP_SESSION', '').lower():
        from linux_kde import Clip2ZeusKDE
        return Clip2ZeusKDE
    else:
        from linux_gtk import Clip2ZeusGTK
        return Clip2ZeusGTK

