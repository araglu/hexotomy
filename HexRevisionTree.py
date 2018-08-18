from PySide import QtCore, QtGui
import binascii
# import time


# This is the tree in the top left corner
class HexRevisionTree(QtGui.QTreeView):
    def __init__(self, parent):
        super(HexRevisionTree, self).__init__()
        self.parent = parent

        self.setSelectionBehavior(QtGui.QAbstractItemView.SelectItems)
        self.model = QtGui.QStandardItemModel()
        self.model.setHorizontalHeaderLabels(["Filename", "Timestamp", "Comment", "Diff?", "Current"])
        self.model.itemChanged.connect(self.revision_cell_changed)
        self.setModel(self.model)
        self.setUniformRowHeights(True)
        self.setColumnWidth(0, 80)  # Filename
        self.setColumnWidth(1, 100)  # Timestamp
        self.setColumnWidth(2, 100)  # Comment
        self.setColumnWidth(3, 15)  # Diff? checkbox
        self.setColumnWidth(4, 60)  # Current 4 bytes

        # self.doubleClicked.connect(self.revision_filename_clicked)
        self.clicked.connect(self.revision_filename_clicked)
        # self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        # self.customContextMenuRequested.connect(self.revision_right_click)

        self.normal_font = self.font()
        self.bold_font = self.font()
        self.bold_font.setBold(True)

    # QT really sucks occasionally
    def sizeHint(self):
        return QtCore.QSize(400, 100)

    def update(self):
        # start = time.time()
        self.model.clear()
        self.model.setHorizontalHeaderLabels(["Filename", "Timestamp", "Comment", "Diff?", "Current"])
        for i in range(0, len(self.parent.files)):
            # TODO: check for existing item and update (for speed)
            rev_filename = QtGui.QStandardItem(self.parent.files[i]["filename"])
            # rev_filename.clicked.connect(self.revision_filename_clicked)
            rev_filename.setEditable(False)
            rev_filename.setToolTip(self.parent.files[i]["fullfilename"])
            if i == self.parent.current_file:
                rev_filename.setFont(self.bold_font)

            else:
                rev_filename.setFont(self.normal_font)

            rev_timestamp = QtGui.QStandardItem(self.parent.files[i]["timestamp"])
            rev_timestamp.setEditable(False)
            rev_comment = QtGui.QStandardItem(self.parent.files[i]["comment"])
            rev_comment.setToolTip(self.parent.files[i]["comment"])
            rev_diff = QtGui.QStandardItem("")
            rev_diff.setCheckable(True)
            if self.parent.files[i]["diff"] == "true":
                rev_diff.setCheckState(QtCore.Qt.CheckState.Checked)
            else:
                rev_diff.setCheckState(QtCore.Qt.CheckState.Unchecked)
            rev_current = QtGui.QStandardItem("")
            self.model.appendRow([rev_filename, rev_timestamp, rev_comment, rev_diff, rev_current])
            # self.files[self.current_file]["row"] = rev_filename.index().row()
            # self.files[self.current_file]["key"] = self.current_file
            # print "Current_file: " + str(self.current_file)
            rev_filename.key = i

            # self.parent.file_watch.add(self.parent.files[i]["fullfilename"])

        self.update_revision_diff()
        self.resizeColumnToContents(0)
        self.resizeColumnToContents(1)
        # self.resizeColumnToContents(2)
        self.resizeColumnToContents(3)
        self.resizeColumnToContents(4)
        # print "revisionTree.update: %f" % (time.time() - start)

    @QtCore.Slot(QtGui.QStandardItem)
    def revision_cell_changed(self, item):
        # print "something changed! " + str(item.text()) + "    column: " + str(item.column())
        if item.column() is 2:
            # print "comment changed!"
            # print str(item)
            # print "row: " + str(item.row())
            # print "changing files[%d] %s" % (item.row(), self.files[item.row()]["filename"])
            self.parent.files[item.row()]["comment"] = item.text()
            item.setToolTip(self.parent.files[item.row()]["comment"])
        if item.column() is 3:
            # print "row %d check is %s" % (item.row(), str(item.checkState()))
            if item.checkState() == QtCore.Qt.CheckState.Checked:
                self.parent.files[item.row()]["diff"] = "true"
            else:
                self.parent.files[item.row()]["diff"] = "false"
            # item.setText(self.parent.files[item.row()]["diff"])
            self.parent.hex_view.redraw_background()

    @QtCore.Slot(QtCore.QModelIndex)
    def revision_filename_clicked(self, index):
        # print "OMG Clicky" + str(index)
        if index.column() is 0:
            item2 = self.model.item(index.row(), index.column())
            # print "  " + str(item2) + "  data:" + str(item2.text())
            # item3 = self.model.item(index.row(), 1)
            # print "  " + str(item3) + "  data:" + str(item3.text())
            # print item2.index()
            # print "Switching to #%d %s %s" % (item2.key, item2.text(), item3.text())
            self.parent.select_file(item2.key)


    # def revision_right_click(self, position):
    #     menu = QtGui.QMenu(self)
    #     action_delete_file = QtGui.QAction("Remove File (no undo!)", menu, triggered = self.parent.remove_file)
    #     menu.addAction(action_delete_file)
    #     menu.exec_(self.mapToGlobal(position))

    def contextMenuEvent(self, event):
        # print "A RIGHT CLICK! I caught it!"
        menu = QtGui.QMenu(self)
        action_delete_file = QtGui.QAction("Remove File (no undo!)", menu, triggered = self.parent.remove_file_rightclick)
        menu.addAction(action_delete_file)
        action_stop_file_watch = QtGui.QAction("Stop Watching File", menu, triggered = self.parent.stop_file_watch_rightclick)
        menu.addAction(action_stop_file_watch)
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
            item = self.model.item(i, 4)
            new_diff = ""
            for j in range(0, 4):
                if loc + j < len(self.parent.files[i]["rawfile"]):
                    new_diff += binascii.hexlify(self.parent.files[i]["rawfile"][loc + j]).upper() + " "
            # new_diff = binascii.hexlify(self.files[i]["rawfile"][self.last_selected:self.last_selected+4]).upper()
            # print "changing diff from %s to %s" % (item.text(), new_diff)
            item.setText(new_diff)
