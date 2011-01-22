import sys
import logging

from PyQt4.QtGui import QApplication, qApp, QIcon
from bbicon import Settings, BuildBotIcon

def main(argv=sys.argv):
    import bbicon_qrc

    a = QApplication(argv) if qApp.startingUp() else qApp
    a.setQuitOnLastWindowClosed(False)
    a.setWindowIcon(QIcon(':/buildboticon-success.png'))

    logging.basicConfig()
    logging.getLogger().setLevel(logging.DEBUG)

    settings = Settings()
    if not settings.configure(argv):
        return 1
    else:
        bbi = BuildBotIcon(settings)
        bbi.start()
        return a.exec_()

if __name__ == '__main__':
    sys.exit(main(sys.argv))
