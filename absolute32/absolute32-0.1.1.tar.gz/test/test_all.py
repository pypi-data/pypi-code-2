# -*- coding:utf-8 -*-

import absolute32 as a

assert a.hash('copyright') == -174803930

assert a.hash(u'赖勇浩') == -1178905243

assert a.hash('Python 2.6.5 (r265:79063, Apr 16 2010, 13:09:56)') == 2085310411


