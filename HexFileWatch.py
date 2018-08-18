from PySide import QtCore, QtGui
import os
import pprint

class HexFileWatch():
    def __init__(self, parent):
        self.parent = parent

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.watch)
        self.timer.start(1000)

        self.files = {}
        self.filecount = {}

    def watch(self):
        for name, mod in self.files.iteritems():
            # print "Looking for changes in " + name
            if os.path.isfile(name):
                fileinfo = QtCore.QFileInfo(name)
                last_mod = fileinfo.lastModified()
                if last_mod != mod:
                    print "   FILE CHANGED! old:" + str(mod) + "    new:" + str(last_mod)
                    self.parent.load_file(name)


    def add(self, filename):
        #print "Adding watch: " + filename
        if os.path.isfile(filename):
            fileinfo = QtCore.QFileInfo(filename)
            self.files[fileinfo.canonicalFilePath()] = fileinfo.lastModified()
            if fileinfo.canonicalFilePath() in self.filecount:
                self.filecount[fileinfo.canonicalFilePath()] += 1
            else:
                self.filecount[fileinfo.canonicalFilePath()] = 1

    def remove(self, filename, count):
        # Typically called with 1
        # will remove the filewatch if filecount-count <= 0
        if os.path.isfile(filename):
            fileinfo = QtCore.QFileInfo(filename)
            if fileinfo.canonicalFilePath() in self.filecount:
                # Prevent errors if called many times by BOFH
                self.filecount[fileinfo.canonicalFilePath()] -= count
                if self.filecount[fileinfo.canonicalFilePath()] <= 0:
                    del self.filecount[fileinfo.canonicalFilePath()]
                    del self.files[fileinfo.canonicalFilePath()]

    def list(self):
        for name, mod in self.files.iteritems():
            print "%s (tstamp:%s) (count:%d)" % (name, mod, self.filecount[name])