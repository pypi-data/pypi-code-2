import openTMM.tests.logFile as LF
import openTMM.tests.testReciprocity as testReciprocity
import openTMM.tests.testEnergy as testEnergy
import openTMM.tests.testFIM as testFIM
import openTMM.tests.testWeston as testWeston

def run():
    print "Testing will take about 45 minutes.\n"
    print "Coffee time?  \n\n"
    logfile = LF.LogFile()

    testReciprocity.run(logfile)
    print '--------------------------------\n\n'
    testEnergy.run(logfile)
    print '--------------------------------\n\n'
    testFIM.run(logfile)
    print '--------------------------------\n\n'
    testWeston.run(logfile)
    print '--------------------------------\n\n'

    if logfile.saveFile:
        msg = "At least one test failed.  If the number of the failed tests \n"
        msg += "is 'small' then everything should be fine.  Some tests \n"
        msg += "may have failed due to subtraction cancellation or \n"
        msg += "numerical swamping and there is no reason to be concerned.\n\n"

        msg += "If you feel that the number of the failed tests exceeds a 'reasonable'\n"
        msg += "amount then please email " + str(logfile.filename) + " to \n"
        msg += "ayuffa@gmail.com.  The file may be large so please zip it: \n"
        msg += "   $ gzip " + str(logfile.filename) + "\n"
        msg += "Thank you, \n    Alex J. Yuffa"

        print msg

    logfile.cleanUp()

if __name__ == '__main__':
    run()
