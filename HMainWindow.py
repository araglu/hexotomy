# pylint: disable=W0201
from PySide import QtCore, QtGui
import binascii
import cPickle
import os
from HexView import HexView
from HexInterpreterTable import HexInterpreterTable
from HexInterpreterDetail import HexInterpreterDetail
from HexInspectorTable import HexInspectorTable
from HexFileWatch import HexFileWatch
from HexRevisionTree import HexRevisionTree
#from var_dump import var_dump
import time


class HMainWindow(QtGui.QMainWindow):
    def __init__(self):
        super(HMainWindow,
              self).__init__()  # does something magical about inheritance and preventing infinite recursion?

        self.files = []
        self.current_file = None

        # self.last_selected = 0

        # QtCore.QCoreApplication.setOrganizationName("L-3Com")
        # QtCore.QCoreApplication.setOrganizationName("l-3com.com")
        # QtCore.QCoreApplication.setApplicationName("Hexotomy")
        self.setWindowTitle("Hexotomy")

        QtCore.QSettings.setPath(QtCore.QSettings.IniFormat, QtCore.QSettings.UserScope, ".")
        self.read_settings()

        self.show()
        # self.showMaximized()
        self.setAcceptDrops(True)

        # self.file_watcher = QtCore.QFileSystemWatcher()
        # self.file_watcher.fileChanged.connect(self.file_changed)
        self.file_watch = HexFileWatch(self)

        self.hex_view = HexView(self)
        self.setCentralWidget(self.hex_view)

        self.create_actions()
        self.create_menus()
        self.create_toolbars()
        self.create_statusbar()
        self.create_dock_windows()

        self.load_project(self.project_file)

        self.save_timer = QtCore.QTimer()
        self.save_timer.timeout.connect(self.save_project)
        self.save_timer.start(30000)

    # Create:
    def create_actions(self):
        self.openAction = QtGui.QAction(QtGui.QIcon('document-open.png'), "&Open...", self,
                                        shortcut=QtGui.QKeySequence.Open, statusTip="Open an existing file",
                                        triggered=self.open_file)
        self.projectAction = QtGui.QAction(QtGui.QIcon('system-file-manager.png'), "&Load Project File...", self,
                                           shortcut=QtGui.QKeySequence.Open,
                                           statusTip="Load a Project file where all work will be saved",
                                           triggered=self.choose_project)
        self.exitAction = QtGui.QAction("E&xit", self, shortcut="Ctrl-Q", statusTip="Exit Hexotomy",
                                        triggered=self.close)
        self.aboutAction = QtGui.QAction("&About", self, statusTip="Show the application's About box",
                                         triggered=self.about)

    def create_menus(self):
        self.fileMenu = self.menuBar().addMenu("&File")
        self.fileMenu.addAction(self.projectAction)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.openAction)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.exitAction)

        self.menuBar().addSeparator()

        self.helpMenu = self.menuBar().addMenu("&Help")
        self.helpMenu.addAction(self.aboutAction)

    def create_toolbars(self):
        self.fileToolBar = self.addToolBar("File")
        self.fileToolBar.setObjectName("fileToolBar")
        self.fileToolBar.addAction(self.projectAction)
        self.fileToolBar.addSeparator()
        self.fileToolBar.addAction(self.openAction)

    def create_statusbar(self):
        self.statusBar().showMessage("")

    def create_dock_windows(self):
        self.revision_dock = QtGui.QDockWidget("Files/Revisions", self)
        self.revision_dock.setObjectName("revision_dock")
        # self.self().self.selfie.self() = self.selfy.self%self().selfself
        self.revision_dock.setFeatures(QtGui.QDockWidget.DockWidgetFloatable | QtGui.QDockWidget.DockWidgetMovable)
        self.revision_tree = HexRevisionTree(self)
        self.revision_dock.setWidget(self.revision_tree)
        # self.revision_dock.setGeometry(0, 0, 400, 600)
        self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, self.revision_dock)

        self.inspector_dock = QtGui.QDockWidget("Inspector Gadget", self)
        self.inspector_dock.setObjectName("inspector_dock")
        self.inspector_dock.setFeatures(QtGui.QDockWidget.DockWidgetFloatable | QtGui.QDockWidget.DockWidgetMovable)
        # self.inspector_table = QtGui.QTableWidget(self.inspector_dock)
        self.inspector_table = HexInspectorTable(self)
        self.inspector_dock.setWidget(self.inspector_table)
        # self.inspector_dock.setGeometry(0, 0, 400, 600)  # useless
        self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, self.inspector_dock)

        self.interpreter_dock = QtGui.QDockWidget("Interpreter", self)
        self.interpreter_dock.setObjectName("interpreter_dock")
        self.interpreter_dock.setFeatures(QtGui.QDockWidget.DockWidgetFloatable | QtGui.QDockWidget.DockWidgetMovable)
        self.interpreter_table = HexInterpreterTable(self)
        self.interpreter_dock.setWidget(self.interpreter_table)
        # self.inspector_dock.setGeometry(0, 0, 400, 600)  # useless
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.interpreter_dock)

        self.interpreter_detail_dock = QtGui.QDockWidget("Interpret Detail", self)
        self.interpreter_detail_dock.setObjectName("interpreter_detail_dock")
        self.interpreter_detail_dock.setFeatures(QtGui.QDockWidget.DockWidgetFloatable | QtGui.QDockWidget.DockWidgetMovable)
        self.interpreter_table.detail = HexInterpreterDetail(self.interpreter_table)
        self.interpreter_detail_dock.setWidget(self.interpreter_table.detail)
        # self.inspector_dock.setGeometry(0, 0, 400, 600)  # useless
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.interpreter_detail_dock)

    # Do stuff:
    def about(self):
        QtGui.QMessageBox.about(self, "About Hexotomy",
                                "Hexotomy is a tool to help understand small binary files.<p>"
                                "Uses PySide (LGPL) and Tango Icons (Public Domain)")

    def read_settings(self):
        settings = QtCore.QSettings(QtCore.QSettings.IniFormat, QtCore.QSettings.UserScope, "L-3com", "Hexotomy")
        self.project_file = settings.value("project", "default.hxt")
        print "project_file: " + self.project_file
        #print "GRRR: isfile-%s getsize-%d" % (str(os.path.isfile(self.project_file)), os.path.getsize(self.project_file))
        if not os.path.isfile(self.project_file) or os.path.getsize(self.project_file) < 20:
            print "read_settings: '%s' is not a real project file. Defaulting to default.hxt" % (self.project_file)
            self.project_file = "default.hxt"
        self.restoreGeometry(settings.value("geometry"))
        #if not self.restoreState(settings.value("windowState")):
            #self.showMaximized()

    def write_settings(self):
        settings = QtCore.QSettings(QtCore.QSettings.IniFormat, QtCore.QSettings.UserScope, "L-3com", "Hexotomy")
        settings.setValue("project", self.project_file)
        settings.setValue("geometry", self.saveGeometry())
        settings.setValue("windowState", self.saveState())

    def choose_project(self):
        filename, _ = QtGui.QFileDialog.getSaveFileName(self, caption="Load Project File",
                                                        filter="Hexotomy Project (*.hxt);;All Files (*)",
                                                        options="QFileDialog.DontConfirmOverwrite")
        if filename:
            self.save_project()
            self.load_project(filename)

    def load_project(self, filename):
        if not filename:
            print "empty db filename"
            return

        if os.path.isfile(filename) and os.path.getsize(filename) > 0:
            try:
                project_file = open(str(filename), "rb")
                self.files = cPickle.load(project_file)
                self.interpreter_table.interprets = cPickle.load(project_file)
            except IOError as err:
				# TODO: I should really use some variable with the app name here
                QtGui.QMessageBox.warning(self, "Hexotomy",
                                          "Cannot load project %s:\n%s." % (filename, err.strerror))
                return
            except EOFError as err:
                QtGui.QMessageBox.warning(self, "Hexotomy",
                                          "Corrupted project file %s." % (filename))
            finally:
                project_file.close()

        self.project_file = os.path.abspath(filename)
        self.revision_tree.update()
        self.select_file(0)
        self.interpreter_table.update_interpreter()

        for i in range(0, len(self.files)):
            self.file_watch.add(self.files[i]["fullfilename"])

        print "really loaded db!"
        self.setWindowTitle("Hexotomy (%s)" % os.path.basename(filename))
        print "loaded db! " + str(self.project_file)

    def save_project(self):
        # print "trying to save project: " + self.project_file
        if self.project_file:
            try:
                project_file = open(str(self.project_file), "w+b")
                cPickle.dump(self.files, project_file)
                cPickle.dump(self.interpreter_table.interprets, project_file)
                project_file.close()
            except IOError as err:
                QtGui.QMessageBox.warning(self, "Application?",
                                          "Cannot save project %s:\n%s." % (self.project_file, err.strerror))
                return False
            # print "saved db!"
            return True

    def open_file(self):
        filename, _ = QtGui.QFileDialog.getOpenFileName(self)
        if filename:
            self.load_file(filename)

    def load_file(self, filename):
        rawfile = QtCore.QFile(filename)
        rawfileinfo = QtCore.QFileInfo(rawfile)
        if not rawfile.open(QtCore.QFile.ReadOnly):
            QtGui.QMessageBox.warning(self, "Application?",
                                      "Cannot read file %s:\n%s." % (filename, rawfile.errorString()))
            return

        QtGui.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
        rawbinary = rawfile.readAll().data()
        self.files.append({"filename": rawfileinfo.fileName(),
                           "timestamp": rawfileinfo.lastModified().toString("yyyy-MM-dd hh:mm:ss"),
                           "comment": "",
                           "fullfilename": rawfileinfo.canonicalFilePath(),
                           "rawfile": rawbinary,
                           "diff": "true"})
        file_index = len(self.files) - 1

        self.statusBar().showMessage("File Loaded", 2000)

        self.revision_tree.update()

        self.select_file(file_index)

        QtGui.QApplication.restoreOverrideCursor()

        self.file_watch.add(rawfileinfo.canonicalFilePath())
        # print "Currently watched files: "
        # self.file_watch.list()

    def remove_file_rightclick(self):
        # find file in files
        selected = self.revision_tree.selectedIndexes()[0]
        row = self.revision_tree.model.itemFromIndex(selected).row()

        self.remove_file(row)

    def remove_file(self, index):
        # remove filewatch
        self.file_watch.remove(self.files[index]["fullfilename"], 1)
        # statusbar message
        self.statusBar().showMessage("Removed file '%s'" % self.files[index]["fullfilename"], 5000)
        # delete from files
        del self.files[index]
        # select a different file if necessary
        if self.current_file == index:
            if index < len(self.files):
                self.select_file(index)
            elif index != 0:
                self.select_file(index - 1)
            else:
                # I don't want to handle empty :(
                pass
        else:
            # current_file needs to be relocated!
            if self.current_file > index:
                self.select_file(index)
        # remove from HexRevisionTree
        self.revision_tree.update()
        # print "Currently watched files: "
        # self.file_watch.list()

    def stop_file_watch_rightclick(self):
        # find file in files
        selected = self.revision_tree.selectedIndexes()[0]
        row = self.revision_tree.model.itemFromIndex(selected).row()

        self.stop_file_watch(row)

    def stop_file_watch(self, index):
        # remove filewatch
        # print "removing file watch for %d  %s" % (index, self.files[index]["fullfilename"])
        self.file_watch.remove(self.files[index]["fullfilename"], 99999)
        # print "Currently watched files: "
        # self.file_watch.list()

    def select_file(self, index):
        if index < len(self.files):
            self.current_file = index
            # start = time.time()
            self.hex_view.set_binary(self.current_file)
            # print "hex_view.set_binary(%d): %f" % (index, time.time() - start)
            #start = time.time()
            self.inspector_table.update_inspector()  # Inspector Gadget will show info at loc
            #print "inspector_table.update_inspector: %f" % (time.time() - start)
            #start = time.time()
            self.interpreter_table.update_interpreter()
            #print "interpreter_table.update_interpreter: %f" % (time.time() - start)
            self.statusBar().showMessage("selected file %s" % self.files[self.current_file]["fullfilename"])

        else:
            print "somebody tried to call select_file(%d), but there are only %d files loaded (ok on init)" \
                  % (index, len(self.files))

    # Handle stuff
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dragMoveEvent(self, event):
        event.acceptProposedAction()

    def dropEvent(self, event):
        # print "got a dropEvent!"
        event.acceptProposedAction()
        # print "mime: " + str(event.mimeData().formats())
        # print "text: " + str(event.mimeData().text())
        # print "urls: " + str(event.mimeData().urls())
        # print "name: " + str(event.mimeData().data("FileName"))
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                # print "attempting to load: " + str(url)
                self.load_file(url.toLocalFile())

    def dragLeaveEvent(self, event):
        event.acceptProposedAction()

    def closeEvent(self, event):
        self.write_settings()
        if self.save_project():
            event.accept()
