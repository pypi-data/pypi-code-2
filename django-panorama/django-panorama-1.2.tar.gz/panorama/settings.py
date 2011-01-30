"""
   Settings for panorama display.
"""
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

#VIEWPORT_WIDTH
#  Width of the panorama window
#
#  Value: width in pixels.
#  Default: 600
VIEWPORT_WIDTH = getattr(settings, 'PANORAMA_VIEWPORT_WIDTH', 600)

#SPEED
#  Speed of the panorama rotation.
#
#  Value: number; higher values means slower :-P
#  Default: 20000
SPEED = getattr(settings, 'PANORAMA_SPEED', 20000)

#DIRECTION
#  Starting direction of the rotation.
#
#  Value: ['left','right']
#  Default: 'left'
DIRECTION = getattr(settings, 'PANORAMA_DIRECTION', 'left')

#CONTROL_DISPLAY
#  Display rotation controls?
#
#  Value: ['auto', 'yes', 'no']
#  Default: 'auto'
CONTROL_DISPLAY = getattr(settings, 'PANORAMA_CONTROL_DISPLAY', 'auto')

#START_POSITION
#  Starting position of the panorama.
#
#  Value: position in pixels.
#  Default: 0
START_POSITION = getattr(settings, 'PANORAMA_START_POSITION', 0)

#AUTO_START
#  Start rotation automatically?
#
#  Value: [True, False]
#  Default: False
AUTO_START = getattr(settings, 'PANORAMA_AUTO_START', 'false')

#MODE_360
#  Loop over the image?
#
#  Value: [True, False]
#  Default: True
MODE_360 = getattr(settings, 'PANORAMA_MODE_360', 'true')

DIRECTION_CHOICES = (
    ('left', _('left')),
    ('right', _('right')),
)

CONTROL_DISPLAY_CHOICES = (
    ('auto', _('auto')),
    ('yes', _('yes')),
    ('no', _('no')),
)
