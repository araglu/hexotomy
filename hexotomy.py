#!/usr/bin/python2
from PySide import QtGui
from HMainWindow import HMainWindow

# from objbrowser import browse

if __name__ == '__main__':
    import sys
    app = QtGui.QApplication(sys.argv)
    mainwin = HMainWindow()
    mainwin.show()
    app.exec_()
    # sys.exit(app.exec_())
