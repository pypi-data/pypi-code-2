#
# Copyright 2010 Corporation of Balclutha (http://www.balclutha.org)
# 
#                All Rights Reserved
# 
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
#
# Corporation of Balclutha DISCLAIMS ALL WARRANTIES WITH REGARD TO THIS
# SOFTWARE, INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY
# AND FITNESS, IN NO EVENT SHALL Corporation of Balclutha BE LIABLE FOR
# ANY SPECIAL, INDIRECT OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS,
# WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS
# ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR
# PERFORMANCE OF THIS SOFTWARE. 
#

PROJECTNAME = "ZenPacks.lbn.ZopeMonitor"
SKINS_DIR = 'skins'
SKINNAME = PROJECTNAME
GLOBALS = globals()

#
# these are the tag-names written by the munin-based zope-agent plugins
#
MUNIN_THREADS = ('total_threads', 'free_threads')
MUNIN_CACHE = ('total_objs', 'total_objs_memory', 'target_number')
MUNIN_ZODB = ('total_load_count', 'total_store_count', 'total_connections')
MUNIN_MEMORY = ('VmPeak', 'VmSize', 'VmLck', 'VmHWM', 'VmRSS', 'VmData', 'VmStk', 'VmExe', 'VmLib', 'VmPTE')
