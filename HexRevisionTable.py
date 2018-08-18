from PySide import QtCore, QtGui
import binascii
# import time


# This is the tree in the top left corner
class HexRevisionTable(QtGui.QTableWidget):
    def __init__(self, parent):
        super(HexRevisionTable, self).__init__()
        self.parent = parent

        # self.setSelectionBehavior(QtGui.QAbstractItemView.SelectItems)
        # self.setUniformRowHeights(True)
        self.verticalHeader().hide()
        self.setColumnCount(5)
        self.setHorizontalHeaderLabels(("Filename", "Timestamp", "Comment", "Diff", "Current"))
        self.setColumnWidth(0, 60)  # Filename
        self.setColumnWidth(1, 30)  # Timestamp
        self.setColumnWidth(2, 140)  # Comment
        self.setColumnWidth(3, 25)  # Diff? checkbox
        self.setColumnWidth(4, 80)  # Current 4 bytes

        self.setAlternatingRowColors(True)
        # self.doubleClicked.connect(self.revision_filename_clicked)
        self.cellChanged.connect(self.revision_cell_changed)  # Content change
        self.currentCellChanged.connect(self.revision_filename_clicked)  # New selection
        # self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        # self.customContextMenuRequested.connect(self.revision_right_click)

        self.normal_font = self.font()
        self.bold_font = self.font()
        self.bold_font.setBold(True)

    # QT really sucks occasionally
    def sizeHint(self):
        return QtCore.QSize(340, 100)

    def update(self):
        # start = time.time()
        self.cellChanged.disconnect(self.revision_cell_changed)
        self.setRowCount(len(self.parent.files))

        for i in range(0, len(self.parent.files)):
            self.setRowHeight(i, 18)

            # TODO: check for existing item and update (for speed)
            # filename
            self.setItem(i, 0, QtGui.QTableWidgetItem(self.parent.files[i]["filename"]))
            self.item(i, 0).setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)  # No edits allowed here
            self.item(i, 0).setToolTip(self.parent.files[i]["fullfilename"])
            if i == self.parent.current_file:
                self.item(i, 0).setFont(self.bold_font)
            else:
                self.item(i, 0).setFont(self.normal_font)

            # timestamp
            self.setItem(i, 1, QtGui.QTableWidgetItem(self.parent.files[i]["timestamp"]))
            self.item(i, 1).setToolTip(self.parent.files[i]["timestamp"])
            self.item(i, 1).setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)  # No edits allowed here

            # comment
            self.setItem(i, 2, QtGui.QTableWidgetItem(self.parent.files[i]["comment"]))
            self.item(i, 2).setToolTip(self.parent.files[i]["comment"])

            # Diff? checkbox
            self.setItem(i, 3, QtGui.QTableWidgetItem(""))
            self.item(i, 3).setFlags(QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled)
            if self.parent.files[i]["diff"] == "true":
                self.item(i, 3).setCheckState(QtCore.Qt.Checked)
            else:
                self.item(i, 3).setCheckState(QtCore.Qt.Unchecked)

            # Current hex view of 4 bytes
            self.setItem(i, 4, QtGui.QTableWidgetItem(""))
            self.item(i, 4).setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)  # No edits allowed here

            # self.files[self.current_file]["row"] = rev_filename.index().row()
            # self.files[self.current_file]["key"] = self.current_file
            # print "Current_file: " + str(self.current_file)

            # self.parent.file_watch.add(self.parent.files[i]["fullfilename"])

        self.update_revision_diff()
        # self.resizeColumnToContents(0)
        # self.resizeColumnToContents(1)
        # self.resizeColumnToContents(2)
        # self.resizeColumnToContents(3)
        # self.resizeColumnToContents(4)
        # print "revisionTree.update: %f" % (time.time() - start)
        self.cellChanged.connect(self.revision_cell_changed)

    @QtCore.Slot(int, int, int, int)
    # Content change
    def revision_cell_changed(self, row, col):
        # print "something changed! " + str(self.item(row, col).text()) + "    column: " + str(col)
        if col is 2:
            # print "comment changed!"
            # print str(item)
            # print "row: " + str(item.row())
            # print "changing files[%d] %s" % (item.row(), self.files[item.row()]["filename"])
            self.parent.files[row]["comment"] = self.item(row, col).text()
            self.item(row, col).setToolTip(self.parent.files[row]["comment"])
        if col is 3:
            # print "row %d check is %s" % (row, str(self.item(row, col).checkState()))
            if self.item(row, col).checkState() == QtCore.Qt.Checked:
                self.parent.files[row]["diff"] = "true"
            else:
                self.parent.files[row]["diff"] = "false"
            # item.setText(self.parent.files[item.row()]["diff"])
            self.parent.hex_view.redraw_background()

    @QtCore.Slot(int, int, int, int)
    # Newly selected cell
    def revision_filename_clicked(self, row, col):
        # print "OMG Clicky" + str(index)
        # if col is 0:
        item2 = self.item(row, col)
        # print "  " + str(item2) + "  data:" + str(item2.text())
        # item3 = self.model.item(index.row(), 1)
        # print "  " + str(item3) + "  data:" + str(item3.text())
        # print item2.index()
        # print "Switching to #%d %s %s" % (item2.key, item2.text(), item3.text())
        self.parent.select_file(row)


    # def revision_right_click(self, position):
    #     menu = QtGui.QMenu(self)
    #     action_delete_file = QtGui.QAction("Remove File (no undo!)", menu, triggered = self.parent.remove_file)
    #     menu.addAction(action_delete_file)
    #     menu.exec_(self.mapToGlobal(position))

    def contextMenuEvent(self, event):
        # print "A RIGHT CLICK! I caught it!"
        menu = QtGui.QMenu(self)
        action_delete_file = QtGui.QAction("&Remove File (no undo!)", menu, triggered = self.parent.remove_file_rightclick)
        menu.addAction(action_delete_file)
        action_stop_file_watch = QtGui.QAction("&Stop Watching File", menu, triggered = self.parent.stop_file_watch_rightclick)
        menu.addAction(action_stop_file_watch)
        action_check_all_diffs = QtGui.QAction("&Check all diffs", menu,
                                               triggered = self.check_all_diffs)
        menu.addAction(action_check_all_diffs)
        action_uncheck_all_diffs = QtGui.QAction("&Uncheck all diffs", menu,
                                               triggered = self.uncheck_all_diffs)
        menu.addAction(action_uncheck_all_diffs)
        menu.exec_(event.globalPos())
        event.accept()

    # Don't let right clicks do anything besides open the above context menu (i.e. don't select anything)
    # def mousePressEvent(self, event):
    #     if event.button() != QtCore.Qt.RightButton:
    #         super(HexRevisionTree, self).mousePressEvent(event)
    # Actually this tree doesn't select very well, so I'll leave right-click select in

    def update_revision_diff(self):
        loc = self.parent.hex_view.select_start
        # loc = self.last_selected
        for i in range(0, len(self.parent.files)):
            item = self.item(i, 4)
            new_diff = ""
            for j in range(0, 4):
                if loc + j < len(self.parent.files[i]["rawfile"]):
                    new_diff += binascii.hexlify(self.parent.files[i]["rawfile"][loc + j]).upper() + " "
            # new_diff = binascii.hexlify(self.files[i]["rawfile"][self.last_selected:self.last_selected+4]).upper()
            # print "changing diff from %s to %s" % (item.text(), new_diff)
            item.setText(new_diff)

    def check_all_diffs(self):
        self.cellChanged.disconnect(self.revision_cell_changed)

        for i in range(0, len(self.parent.files)):
            self.item(i, 3).setCheckState(QtCore.Qt.Checked)
            self.parent.files[i]["diff"] = "true"

        self.cellChanged.connect(self.revision_cell_changed)
        self.parent.hex_view.redraw_background()

    def uncheck_all_diffs(self):
        self.cellChanged.disconnect(self.revision_cell_changed)

        for i in range(0, len(self.parent.files)):
            self.item(i, 3).setCheckState(QtCore.Qt.Unchecked)
            self.parent.files[i]["diff"] = "false"

        self.cellChanged.connect(self.revision_cell_changed)
        self.parent.hex_view.redraw_background()

