# -*- coding: utf-8 -*-
import sys
import StringIO
import codecs
import os

base = os.path.dirname(os.path.abspath(os.path.join(__file__, "../../..")))

sys.path.append(base)

from codec import XetexCodec
from fsencoder import FontSpecEncoder
from fcmanager import FcManager


conf = '''
<fonts>
  <fontspec default="1" id="default" fallback="fontconfig">
    <enter>
      <font type="main">DejaVu Serif</font>
      <font type="sans">DejaVu Sans</font>
    </enter>
  </fontspec>
  <fontspec id="latin1">
    <enter>
      <font type="main">DejaVu Serif</font>
    </enter>
  </fontspec>
  <fontspec id="cyrillic">
    <enter>
      <font type="main">FreeSerif</font>
    </enter>
  </fontspec>
  <!--
  -->
  <!-- Chinese range (but very limite) -->
  <!--
  <fontspec range="U04E2A" id="chinese">
    <enter>
      <font type="main sans">Kochi Mincho</font>
    </enter>
  </fontspec>
  -->
</fonts>
'''

encoder = FontSpecEncoder(StringIO.StringIO(conf))
sys.stdout = codecs.lookup('utf-8')[-1](sys.stdout)

input = ''
input += u'参\u4E2A考卡片'
input += u'Памятка по Debian полезный совет при работе с'

m = FcManager()
m.build_fonts()
fonts = m.get_font_handling(unichr(1055), all=True)
for f in fonts:
    print f.family

print "UUUU"
fonts = m.get_font_handling(unichr(21345), all=True)
for f in fonts:
    print f.family

print "UUUU"

c = XetexCodec(StringIO.StringIO(conf))
s = c.encode(input)
print s.decode("utf8")
