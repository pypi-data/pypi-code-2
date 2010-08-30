import logging

import pomsets_app.gui.qt.application as ApplicationModule


def configLogging():
    """
    this will be called by all the main functions 
    to use the default setup for logging
    """
    # define a basic logger to write to file
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s %(levelname)-8s %(message)s',
                        datefmt='%a, %d %b %Y %H:%M:%S',
                        filename='/tmp/pomsets_app.log',
                        filemode='w')

    # end def configureLogging
    pass


def main():

    configLogging()
    app = ApplicationModule.Application()
    app.runProgram()

    return

if __name__=="__main__":
    main()

