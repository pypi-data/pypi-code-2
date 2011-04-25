import os
import sys

sys.path.append("../..")
import dbtex

def ti_set(paths):
    os.environ["TEXINPUTS"] = paths

def ti_get():
    return os.getenv("TEXINPUTS")


d = dbtex.DbTex()

# Added paths
d.texinputs = [ "p1", "p2", "p3:p4:p5", "p6" ]

# Priority path
d.texlocal = "/path/local"

# Where style is
d.texdir = "/path/texdir"

# Expected (provided TEXINPUTS=/tmp/::tmp before calling the test
#
# /tmp/::tmp
# /path/local//:/tmp/::p1:p2:p3:p4:p5:p6:/path/texdir//:tmp
# /path/local//::p1:p2:p3:p4:p5:p6:/path/texdir//:/path/append1:/path/append2
# /path/local//:/path/prepend1:/path/prepend2::p1:p2:p3:p4:p5:p6:/path/texdir//
# /path/local//:/path/prepend1::p1:p2:p3:p4:p5:p6:/path/texdir//:/path/append1:

# No TEXINPUTS
print ti_get()
d.update_texinputs()
p = ti_get()
print p

# Something already appended
ti_set(":/path/append1:/path/append2")
d.update_texinputs()
p = ti_get()
print p

# Something prepended
ti_set("/path/prepend1:/path/prepend2:")
d.update_texinputs()
p = ti_get()
print p

# System in between
ti_set("/path/prepend1::/path/append1:")
d.update_texinputs()
p = ti_get()
print p

