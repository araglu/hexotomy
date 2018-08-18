from PySide import QtCore, QtGui
import traceback
import math
import pprint
import binascii
import re
import struct

# how about HexAssimilate?
class HexInterpreterTable(QtGui.QTableWidget):
    def __init__(self, parent):
        super(HexInterpreterTable, self).__init__()
        self.parent = parent
        self.detail = None # will be a real class instantiated by HMainWindow since it adds it to the dock

        self.setColumnCount(5)
        self.verticalHeader().hide()
        self.setHorizontalHeaderLabels(("Color", "Name", "Result", "Start", "Len"))
        self.setColumnWidth(0, 40)
        self.setColumnWidth(1, 150)
        self.setColumnWidth(2, 70)
        self.setColumnWidth(3, 40)
        self.setColumnWidth(4, 40)

        self.setAlternatingRowColors(True)
        # TODO: make Color selection invisible, otherwise it is hidden by the whole row blue selection
        # or make it a button
        #self.setSelectionBehavior(QtGui.QTableWidget.SelectRows)

        self.interprets = []
        self.results = {}
        self.background_color_index = {}

        self.currentCellChanged.connect(self.current_cell_changed)
        self.cellChanged.connect(self.cell_changed)
        # self.itemClicked.connect(self.cell_clicked)

        # self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        # self.customContextMenuRequested.connect(self.revision_right_click)

    # QT really ...
    def sizeHint(self):
        return QtCore.QSize(350, 300)
    # but at least I get to create my own class now!

    def add_new(self):
        self.interprets.append({"name": "-new-%d-" % (len(self.interprets)),
                                "code": "result = binascii.hexlify(input)",
                                "start": self.parent.hex_view.select_start,
                                "length": self.parent.hex_view.select_end - self.parent.hex_view.select_start + 1,
                                "result": "",
                                "traceback": "",
                                "color": "#00FF00",
                                "color_shown": "true"})

        self.update_interpreter()
        # print "I wish I could add a new interpret. start:%d end:%d" % (self.hex_view.select_start, self.hex_view.select_end)

    def remove_interpret_right_click(self):
        # get all selected rows
        # print "removing %d indexes" % (len(self.selectedIndexes()))
        for i in sorted(self.selectedIndexes(), reverse=True):
            # Do it backwards and sorted because deleting stuff messes with the index, noob!
            self.remove_interpret(i.row())
        # Redraw hexview
        # TODO: speed this up by selectively redrawing just the cells that need to be colored
        self.parent.select_file(self.parent.current_file)

    def remove_interpret(self, index):
        # print "removing index %d (name:%s, start,%s)" % (index, self.interprets[index]["name"], hex(self.interprets[index]["start"]))
        del self.interprets[index]
        self.update_interpreter()

    def update_interpreter(self):
        self.results = {}
        self.setRowCount(len(self.interprets))
        if self.parent.current_file is None:
            # Bad news on fresh start
            return
        # rawbinary = self.parent.files[self.parent.current_file]["rawfile"]
        # Initialize the background_color_table
        for i in xrange(0, len(self.parent.files[self.parent.current_file]["rawfile"])):
            self.background_color_index[i] = -1

        # print "Before sort:"
        # for index,interpret in enumerate(self.interprets):
        #    print "%d-  st:%d  len:%d  name:%s  result:%s" % (index, interpret["start"], interpret["length"],
        #                                                      interpret["name"], interpret["result"])
        self.interprets.sort(key=lambda x: x["start"])

        for i,_ in enumerate(self.interprets):
            self.update_interpreter_line(i)

    def update_interpreter_line(self, i):
        self.cellChanged.disconnect(self.cell_changed)

        if i >= len(self.interprets):
            print "(HexInterpreterTable->update_interpreter_line) Tried to use index %s which doesn't exist." % (str(i))

        self.setRowHeight(i, 18)
        self.calc_result(i)

        interpret = self.interprets[i]
        # TODO: optimize this to not create new items all day long
        self.setItem(i, 0, QtGui.QTableWidgetItem(""))
        self.item(i, 0).setBackground(QtGui.QColor(interpret["color"]))
        self.item(i, 0).setFlags(QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled)
        # print "%d (%s) color_shown is %s" % (i, interpret["name"], interpret["color_shown"])
        if interpret["color_shown"] == "true":
            self.item(i, 0).setCheckState(QtCore.Qt.Checked)
        else:
            self.item(i, 0).setCheckState(QtCore.Qt.Unchecked)

        self.setItem(i, 1, QtGui.QTableWidgetItem(interpret["name"]))
        self.setItem(i, 2, QtGui.QTableWidgetItem(interpret["result"]))
        self.item(i, 2).setToolTip(interpret["result"])
        self.item(i, 2).setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)  # No edits allowed here
        self.setItem(i, 3, QtGui.QTableWidgetItem(hex(interpret["start"])))
        self.setItem(i, 4, QtGui.QTableWidgetItem(str(interpret["length"])))

        for j in xrange(interpret["start"], interpret["start"] + interpret["length"]):
            if interpret["color_shown"] == "true":
                self.background_color_index[j] = interpret["color"]
            else:
                self.background_color_index[j] = -1
            self.parent.hex_view.draw_background_color(j)
            # x = j % 16
            # y = math.floor(j / 16)
            # # print "update_interpret of %s: x %d   y %d" % (interpret["name"], x, y)
            # if j < len(self.parent.files[self.parent.current_file]["rawfile"]) and self.parent.hex_view.item(y, x) is not None:
            #     self.parent.hex_view.item(y, x).setBackground(QtGui.QColor(interpret["color"]))
                # if i % 2 == 0:
                #     # Alternate colors: even is lighter
                #     self.parent.hex_view.item(y, x).setBackground(QtGui.QColor(160, 160, 255))
                # else:
                #     self.parent.hex_view.item(y, x).setBackground(QtGui.QColor(128, 128, 255))

        self.cellChanged.connect(self.cell_changed)

    def calc_result(self, i):
        rawbinary = self.parent.files[self.parent.current_file]["rawfile"]
        # interpret = self.interprets[i]
        # print " calculating", self.interprets[i]["name"]

        result = ""
        length = self.interprets[i]["length"]
        allresults = self.results
        try:
            input = rawbinary[self.interprets[i]["start"]:self.interprets[i]["start"]+self.interprets[i]["length"]]
            exec self.interprets[i]["code"]
        except KeyError as e:
            # 99% of the time this is caused by using allresults[] before that key has been calculated
            # This could result in a recursive loop
            key = e.args[0]
            # print "KeyError: (%s) this: (%s)" % (key, self.interprets[i]["name"])
            for j,_ in enumerate(self.interprets):
                if self.interprets[j]["name"] == key:
                    # print "  recalc i:", i, " j:", j
                    self.calc_result(j)
                    self.calc_result(i)
                    return
        except:
            result = "*ERR*"
            trace = traceback.format_exc()
            self.interprets[i]["traceback"] = ''.join(trace.splitlines(True)[3:] )# remove first three lines
            print "ERROR in user code:"
            print self.interprets[i]["traceback"]
        else:
            self.interprets[i]["traceback"] = ""
        self.interprets[i]["result"] = result
        self.interprets[i]["length"] = length
        self.results[self.interprets[i]["name"]] = result

    @QtCore.Slot(int, int, int, int)
    # Any cell selection change: just updates detail forms
    def current_cell_changed(self, row, col):
        # print "current_cell_changed (r%d, c%d)" % (row, col)
        if col != 0:
            # Don't let color clicks change anything
            self.detail.fill(row)

    @QtCore.Slot(int, int, int, int)
    # cell contents change
    def cell_changed(self, row, col):
        # print "just cell_changed (r%d, c%d)" % (row, col)
        interpret = self.interprets[row]
        if col is 0:
            # Color checkbox
            if self.item(row, col).checkState() == QtCore.Qt.Checked:
                interpret["color_shown"] = "true"
            else:
                interpret["color_shown"] = "false"
            # pprint.pprint(interpret)
            for i in xrange(0, interpret["length"]):
                if interpret["color_shown"] == "true":
                    self.background_color_index[interpret["start"] + i] = interpret["color"]
                else:
                    self.background_color_index[interpret["start"] + i] = -1
                self.parent.hex_view.draw_background_color(interpret["start"] + i)
        elif col is 1:
            # Name
            interpret["name"] = self.item(row, col).text()
            self.detail.fill(row)
        elif col is 3:
            # Name
            interpret["start"] = int(self.item(row, col).text(), 0)
            self.detail.fill(row)
        elif col is 4:
            # Name
            interpret["length"] = int(self.item(row, col).text(), 0)
            self.detail.fill(row)


    # @QtCore.Slot(int, int, int, int)
    # # This only deals with clicks on the far left Color column
    # def cell_clicked(self, item):
    #     if item.column() == 0: # Color
    #         # print "Color column clicked for row %d" % item.row()
    # nevermind. i'll do all of this in Detail


    def contextMenuEvent(self, event):
        # print "A RIGHT CLICK! I caught it!"
        menu = QtGui.QMenu(self)
        action_interpreter_remove = QtGui.QAction("Remove this Interpret", menu,
                                               triggered = self.remove_interpret_right_click)
        menu.addAction(action_interpreter_remove)
        menu.exec_(event.globalPos())
        event.accept()

    # Don't let right clicks do anything besides open the above context menu (i.e. don't select anything)
    def mousePressEvent(self, event):
        if event.button() != QtCore.Qt.RightButton:
            super(HexInterpreterTable, self).mousePressEvent(event)