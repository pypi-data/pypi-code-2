#-*- coding: utf-8 -*-
from django import template
from blocktext import blocktext
from blockimage import blockimage
from unusedblocks import unusedblocks

register = template.Library()

blocktext = register.tag('blocktext', blocktext)
blockimage = register.tag('blockimage', blockimage)
unusedblocks = register.tag('unusedblocks', unusedblocks)
