import os
import sys
import mx.DateTime
from time import sleep

pauseLen = 0  # 2

class ProvideScript(object):

    def __init__(self, statements=[]):
        self.run(statements)

    def run(self, statements):
        startTime = mx.DateTime.now()
        statements = [s.split('#')[0].strip() for s in statements]
        inError = False
        errorStatement = ''
        splitStatement = ''
        outstandingStatements = []
        failedStatements = []
        for statement in statements:
            isHumourous = False
            if not statement:
                continue
            if statement[-1] == '\\':
                splitStatement += statement[:-1]
                continue
            elif splitStatement:
                statement = splitStatement + statement
                splitStatement = ''
            if statement[0:4] == ':-) ':
                isHumourous = True
                statement = statement[4:]
            statement = sys.argv[0] + " " + statement + ' -v'
            if not inError:
                print statement
                if os.system(statement):
                    if isHumourous:
                        failedStatements.append(statement)
                        msg = "\nThat didn't work, but we don't care! :-)\n"
                        print msg
                        sleep(pauseLen)
                    else:
                        inError = True
                        errorStatement = statement

            else:
                outstandingStatements.append(statement)
        if inError:
            print ""
            print "The last quant step didn't work out (see above):"
            print ""
            print errorStatement
            print ""
            if failedStatements:
                print "Other quant steps which didn't go so well:"
                print ""
                print "\n".join(failedStatements)
                print ""
            if outstandingStatements:
                print "Provide steps remaining:"
                print ""
                print "\n".join(outstandingStatements)
                print ""
        else:
            print ""
            print "All quant steps completed OK."
            print ""
        endTime = mx.DateTime.now()
        duration = endTime - startTime
        durationString = duration.strftime('%Hh %Mm %Ss')
        print ""
        print "Provide script duration: ", durationString
        print ""
        if inError:
            sys.exit(1)

