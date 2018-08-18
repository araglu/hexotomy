from PySide import QtCore, QtGui
import math
import binascii
import time

class HexView(QtGui.QTableWidget):
    def __init__(self, parent):
        super(HexView, self).__init__()
        self.parent = parent

        self.select_breaking_things = False
        self.setStyleSheet("QTableWidget,QHeaderView {font-family: 'Courier New'; "
                           "font-size: 11px; text-align: center; padding: 0px; margin: 0px; border: 0px;}"
                           "QTableWidget::item:selected {background-color: #000077; color: #FFFF77;}")
                           # "QTableWidget::item {selection-background-color: green;}")
        self.setShowGrid(False)
        self.setAlternatingRowColors(True)

        # self.setFont(QtGui.QFont("Courier New", 9))
        self.setColumnCount(33)
        self.setHorizontalHeaderLabels(("0", "1", "2", "3", "4", "5", "6", "7",
                                        "8", "9", "A", "B", "C", "D", "E", "F",
                                        "", "0", "1", "2", "3", "4", "5", "6", "7",
                                        "8", "9", "A", "B", "C", "D", "E", "F"))
        for col in range(0, 16):
            self.setColumnWidth(col, 20)
        self.setColumnWidth(16, 8)
        for col in range(17, 33):
            self.setColumnWidth(col, 12)

        self.select_start = 0
        self.select_end = 0

        # last_file_length allows the set_binary function to be faster in removing gray cells
        #   it's used to skip un-graying cells that were already fine
        self.last_file_length = 0

        self.itemSelectionChanged.connect(self.selection_changed)

    def set_binary(self, file_index):
        binary_input = self.parent.files[file_index]["rawfile"]  # file_index should be self.parent.current_file
        # start = time.time()

        # Trimming rows takes too long. Instead, excess cells are turned gray.
        #self.setRowCount(math.ceil(len(binary_input) / 16)) # This will delete the last row and then re-add it
            # to remove any trailing cells
        #self.setRowCount(math.ceil(len(binary_input) / 16) + 1)

        rows_needed = math.ceil(len(binary_input) / 16) + 1
        if self.rowCount() < rows_needed:
            self.setRowCount(rows_needed)

        #print "Length of input: %d    rows: %d" % (len(binary_input), self.rowCount())
        #print "  after setRowCount: %f" % (time.time() - start)
        for y in range(0, self.rowCount()):
            self.setRowHeight(y, 18)
            #print "Row:%d  int:%d  hex:%s" % (y, y*16, hex(y*16))
            self.setVerticalHeaderItem(y, QtGui.QTableWidgetItem(hex(y * 16)[2:]))
            #self.verticalHeaderItem(y).setTextAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignTop)
            # #chops off bottom half of text
            for x in range(0, 16):
                index = y * 16 + x
                if index < len(binary_input):
                    cellhex = binascii.hexlify(binary_input[index]).upper()
                    cellascii = str(binary_input[index])

                    #print "row:%d  col:%d  index:%d  hex:%s  char:%s" % (y, x, index, cellhex, cellascii )
                    #print "type: %s" % (self.item(y, x))
                    if self.item(y, x) is None:
                        self.setItem(y, x, QtGui.QTableWidgetItem(cellhex))
                        self.setItem(y, x + 17, QtGui.QTableWidgetItem(cellascii))
                        self.item(y, x).setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
                        self.item(y, x + 17).setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
                    else:
                        self.item(y, x).setText(cellhex)
                        self.item(y, x + 17).setText(cellascii)
                    # Undo any graying out from that else down there
                    if index >= self.last_file_length:
                        self.item(y, x).setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
                        self.item(y, x + 17).setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
                        self.item(y, x + 17).setBackground(QtCore.Qt.white)

                    self.draw_background_color(index)

                    if self.item(y, 16) is None:
                        self.setItem(y, 16, QtGui.QTableWidgetItem(""))
                        self.item(y, 16).setFlags(QtCore.Qt.NoItemFlags)
                        self.item(y, 16).setBackground(QtCore.Qt.lightGray)
                    #if index >= self.last_file_length:
                    #    self.item(y, 16).setFlags(QtCore.Qt.NoItemFlags)
                    #    self.item(y, 16).setBackground(QtCore.Qt.lightGray)

                    #self.resizeColumnsToContents()
                else:
                    if self.item(y, x) is None:
                        self.setItem(y, x, QtGui.QTableWidgetItem(""))
                        self.setItem(y, x + 17, QtGui.QTableWidgetItem(""))
                        self.item(y, x).setBackground(QtCore.Qt.lightGray)
                        self.item(y, x + 17).setBackground(QtCore.Qt.lightGray)
                        self.item(y, x).setFlags(QtCore.Qt.NoItemFlags)
                        self.item(y, x + 17).setFlags(QtCore.Qt.NoItemFlags)
                    else:
                        if index <= self.last_file_length:
                            self.item(y, x).setText("")
                            self.item(y, x + 17).setText("")
                    if index <= self.last_file_length:
                        self.item(y, x).setBackground(QtCore.Qt.lightGray)
                        self.item(y, x + 17).setBackground(QtCore.Qt.lightGray)
                        self.item(y, x).setFlags(QtCore.Qt.NoItemFlags)
                        self.item(y, x + 17).setFlags(QtCore.Qt.NoItemFlags)
        #print "set_binary hidden updates: %f" % (time.time() - start)
        #self.setUpdatesEnabled(True)
        #print "set_binary after updates: %f" % (time.time() - start)

        #if self.last_file_length == 0:
        #    self.resizeColumnsToContents()
        #print "thislen: %d   lastlen: %d" % (index, self.last_file_length)
        self.last_file_length = len(binary_input)



    @QtCore.Slot()
    def selection_changed(self):
        # print "selectionChanged - breakingthings?%s" % self.select_breaking_things
        if self.select_breaking_things is False:
            self.select_breaking_things = True

            minrow = self.rowCount()  # will be top row of selection
            maxrow = 0  # will be bottom row of selection
            minrow_col = self.columnCount()  # column of the first row, aka starting point of selection
            maxrow_col = 0  # column of the last row, aka end point

            # var_dump(self.selectedRanges())
            for item in self.selectedRanges():
                # print "  minrow:%d  maxrow:%d  thisTopRow:%d  thisBottomRow:%d" %
                # (minrow, maxrow, item.topRow(), item.bottomRow())
                maxrow = max(maxrow, item.bottomRow())
                minrow = min(minrow, item.topRow())
            for item in self.selectedRanges():
                if maxrow == item.bottomRow():
                    maxrow_col = max(maxrow_col, item.rightColumn())
                if minrow == item.topRow():
                    minrow_col = min(minrow_col, item.leftColumn())
            # var_dump(self.selectedItems())
            # var_dump(self.selectedIndexes())
            # for index, item in enumerate(self.selectedIndexes()):
            # print "  Indexes - %d - row:%d  col:%d" % (index, item.row(), item.column())
            #    var_dump(item)
            #    var_dump(item.data())
            # print "    result minrow:%d,%d  maxrow:%d,%d" % (minrow, minrow_col, maxrow, maxrow_col)

            # this all gets weird for the two separate tables that aren't actually separate
            # if maxrow == minrow:
            #     # draw from start point to end point, just in case
            #     self.setRangeSelected(QtGui.QTableWidgetSelectionRange(minrow, minrow_col, maxrow, maxrow_col), True)
            # if (maxrow - minrow) > 0:
            #     # draw from start point to end of line
            #     self.setRangeSelected(
            #         QtGui.QTableWidgetSelectionRange(minrow, minrow_col, minrow, self.columnCount() - 1), True)
            #     # draw from end point to beginning of line
            #     self.setRangeSelected(QtGui.QTableWidgetSelectionRange(maxrow, 0, maxrow, maxrow_col), True)
            # if maxrow - minrow > 1:
            #     # draw big box
            #     # print "ABOUT TO setRangeSelected!!!!"
            #     self.setRangeSelected(
            #         QtGui.QTableWidgetSelectionRange(minrow + 1, 0, maxrow - 1, self.columnCount() - 1), True)

            self.select_start = minrow * 16 + minrow_col % 17
            self.select_end = maxrow * 16 + maxrow_col % 17

            self.select(self.select_start, self.select_end)

            self.select_breaking_things = False
            self.parent.inspector_table.update_inspector()

    def select(self, start, end):
        # clear any selection
        # self.setRangeSelected(QtGui.QTableWidgetSelectionRange(0, 0, self.rowCount(), self.columnCount()), False)
        self.clearSelection()

        start_row = math.floor(start / 16)
        start_column = start % 16
        end_row = math.floor(end / 16)
        end_column = end % 16
        # print "select %d-%d: start(%d,%d) end(%d,%d)" % (start, end, start_row, start_column, end_row, end_column)

        if start_row == end_row:
            # print "%d == %d" % (start_row, end_row)
            # draw from start point to end point, just in case
            self.setRangeSelected(QtGui.QTableWidgetSelectionRange(start_row, start_column, end_row, end_column), True)
        if (end_row - start_row) > 0:
            # print "(%d - %d) > 0 " % (end_row, start_row)
            # draw from start point to end of line
            self.setRangeSelected(
                QtGui.QTableWidgetSelectionRange(start_row, start_column, start_row, self.columnCount() - 1), True)
            # draw from end point to beginning of line
            self.setRangeSelected(QtGui.QTableWidgetSelectionRange(end_row, 0, end_row, end_column), True)
        if end_row - start_row > 1:
            # print "(%d - %d) > 1 " % (end_row, start_row)
            # draw big box
            # print "ABOUT TO setRangeSelected!!!!"
            self.setRangeSelected(
                QtGui.QTableWidgetSelectionRange(start_row + 1, 0, end_row - 1, self.columnCount() - 1), True)

        self.select_start = start
        self.select_end = end

    def contextMenuEvent(self, event):
        # print "A RIGHT CLICK! I caught it!"
        menu = QtGui.QMenu(self)
        action_interpreter_add = QtGui.QAction("Add to Interpret", menu,
                                               triggered = self.parent.interpreter_table.add_new)
        menu.addAction(action_interpreter_add)
        menu.exec_(event.globalPos())
        event.accept()

    # Don't let right clicks do anything besides open the above context menu (i.e. don't select anything)
    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.RightButton:
            #print "right button pressed in hex_view!"
            pass
        else:
            #print "not right button!"
            super(HexView, self).mousePressEvent(event)

    def draw_background_color(self, index):
        if index >= len(self.parent.files[self.parent.current_file]["rawfile"]):
            # simple error check - caused by increasing length of interpret beyond end of file
            # print "draw_background_color: beyond end of file (%d)" % (index)
            return
        else:
            y = math.floor(index / 16)
            x = index % 16

            # search for background colors of interpreters
            bg_colors = self.parent.interpreter_table.background_color_index
            #print "going to index %d from bg_colors (len:%d)" % (index, len(bg_colors))
            if index in bg_colors and bg_colors[index] is not None and bg_colors[index] != -1:
                # print "(intr)assigning index %d to bg color %s" % (index, bg_colors[index])
                self.item(y, x).setBackground(QtGui.QColor(bg_colors[index]))
            else:
                differences = 0
                total_diff_files = 0  # Number of files that will show up in diff color (i.e. the checked ones)

                for i in range(0, len(self.parent.files)):
                    if self.parent.files[i]["diff"] == "true" and i != self.parent.current_file:  # No need to diff myself
                        if index < len(self.parent.files[i]["rawfile"]) and \
                            self.parent.files[self.parent.current_file]["rawfile"][index] != self.parent.files[i]["rawfile"][index]:
                            differences += 1
                        total_diff_files += 1
                if total_diff_files > 0:
                    color_diff = 255.0 * ((total_diff_files - differences) / float(total_diff_files))
                else:
                    color_diff = 255.0
                #print "(diff)assigning index %d to bg color %s (files:%d, diffs:%d)" % (index, QtGui.QColor(255, color_diff, color_diff).name(), total_diff_files, differences)
                self.item(y, x).setBackground(QtGui.QColor(255, color_diff, color_diff))

    def redraw_background(self):
        #print "redrawing background"
        for i in xrange(0, len(self.parent.files[self.parent.current_file]["rawfile"])):
            self.draw_background_color(i)