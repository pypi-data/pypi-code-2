import nose.tools as nt
import hiatus

@hiatus.set_timeout(0.50)
def forewarn():
    print ""
    print "Keep in mind: This test takes about 6 seconds."
    print "Nose is lying to you when it says they're done."
    print "This is because nose doesn't expect multithreading."
    print ""

successes = []

def success():
    successes.append("HUGE SUCCESS")
glados = hiatus.set_interval(success, 1.000)

@hiatus.set_timeout(5.50)
def count():
    hiatus.clear_interval(glados)
    nt.assert_equal(len(successes), 5)

@hiatus.set_timeout(6.00)
def message():
    print "Test complete."
