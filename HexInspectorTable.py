from PySide import QtCore, QtGui
import binascii
import struct

class HexInspectorTable(QtGui.QTableWidget):
    def __init__(self, parent):
        super(HexInspectorTable, self).__init__()
        self.parent = parent

        self.right_click_pos = None

        self.setColumnCount(2)
        self.verticalHeader().hide()
        # self.inspector_table.setGeometry(0, 0, 400, 600)

        # self.inspector_table.setMinimumSize(400,600)
        # self.inspector_table.setSizePolicy(QtGui.QSizePolicy.Expanding)

    # QT really sucks sometimes
    def sizeHint(self):
        return QtCore.QSize(400, 600)
        # and height still doesn't work right if I have 2 dockwidgets

    def update_inspector(self):
        start = self.parent.hex_view.select_start
        # end = self.parent.hex_view.select_end
        self.clear()
        self.setHorizontalHeaderLabels(("Type", "Value"))
        self.setRowCount(0)

        rawbinary = self.parent.files[self.parent.current_file]["rawfile"]

        if start < 0:
            start = 0
        if start >= len(rawbinary):
            start = len(rawbinary) - 1

        input = rawbinary[start]
        self.update_inspector_add_row(start, "location", 'hex(input)')
        self.update_inspector_add_row(input, "char", 'str(input)')
        self.update_inspector_add_row(input, "binary", 'bin(int(binascii.hexlify(input), 16))[2:]')
        self.update_inspector_add_row(input, "signed char", 'str(struct.unpack("b", input)[0])')
        self.update_inspector_add_row(input, "unsigned char", 'str(struct.unpack("B", input)[0])')
        self.update_inspector_add_row(input, "signed octal", 'str(oct(struct.unpack("b", input)[0]))')
        self.update_inspector_add_row(input, "unsigned octal", 'str(oct(struct.unpack("B", input)[0]))')

        if start + 1 < len(rawbinary):
            input = rawbinary[start:start + 2]
            self.update_inspector_add_separator()
            self.update_inspector_add_row(input, "char 2bytes", 'str(input)')
            self.update_inspector_add_row(input, "short, LittleE", 'str(struct.unpack("<h", input)[0])')
            self.update_inspector_add_row(input, "unsigned short, LittleE", 'str(struct.unpack("<H", input)[0])')
            self.update_inspector_add_row(input, "short, BigE", 'str(struct.unpack(">h", input)[0])')
            self.update_inspector_add_row(input, "unsigned short, BigE", 'str(struct.unpack(">H", input)[0])')

        if start + 3 < len(rawbinary):
            input = rawbinary[start:start + 4]
            self.update_inspector_add_separator()
            self.update_inspector_add_row(input, "char 4bytes", 'str(input)')
            self.update_inspector_add_row(input, "int, LittleE", 'str(struct.unpack("<i", input)[0])')
            self.update_inspector_add_row(input, "unsigned int, LittleE", 'str(struct.unpack("<I", input)[0])')
            self.update_inspector_add_row(input, "float, LittleE", 'str(struct.unpack("<f", input)[0])')
            self.update_inspector_add_row(input, "int, BigE", 'str(struct.unpack(">i", input)[0])')
            self.update_inspector_add_row(input, "unsigned int, BigE", 'str(struct.unpack(">I", input)[0])')
            self.update_inspector_add_row(input, "float, BigE", 'str(struct.unpack(">f", input)[0])')

        if start + 7 < len(rawbinary):
            input = rawbinary[start:start + 8]
            self.update_inspector_add_separator()
            self.update_inspector_add_row(input, "char 8bytes", 'str(input)')
            self.update_inspector_add_row(input, "longlong, LittleE", 'str(struct.unpack("<q", input)[0])')
            self.update_inspector_add_row(input, "unsigned longlong, LittleE", 'str(struct.unpack("<Q", input)[0])')
            self.update_inspector_add_row(input, "double, LittleE", 'str(struct.unpack("<d", input)[0])')
            self.update_inspector_add_row(input, "longlong, BigE", 'str(struct.unpack(">q", input)[0])')
            self.update_inspector_add_row(input, "unsigned longlong, BigE", 'str(struct.unpack(">Q", input)[0])')
            self.update_inspector_add_row(input, "double, BigE", 'str(struct.unpack(">d", input)[0])')

        self.resizeColumnsToContents()
        # self.last_selected = loc

        self.parent.revision_tree.update()

    def update_inspector_add_row(self, input, typestr, valuestr):
        row = self.rowCount()
        self.setRowCount(row + 1)
        self.setRowHeight(row, 18)
        self.setItem(row, 0, QtGui.QTableWidgetItem(typestr))
        item = QtGui.QTableWidgetItem(eval(valuestr))
        item.code = valuestr
        self.setItem(row, 1, item)

    def update_inspector_add_separator(self):
        row = self.rowCount()
        self.setRowCount(row + 1)
        self.setRowHeight(row, 8)

        item = QtGui.QTableWidgetItem()
        item.setFlags(QtCore.Qt.NoItemFlags)
        item.setBackground(QtCore.Qt.lightGray)
        self.setItem(row, 0, item)

        item = QtGui.QTableWidgetItem()
        item.setFlags(QtCore.Qt.NoItemFlags)
        item.setBackground(QtCore.Qt.lightGray)
        self.setItem(row, 1, item)

    def contextMenuEvent(self, event):
        # print "A RIGHT CLICK! I caught it!"
        self.right_click_pos = event.pos()
        menu = QtGui.QMenu(self)
        action_copy_code = QtGui.QAction("Copy Python Code", menu, triggered = self.code_to_clipboard)
        menu.addAction(action_copy_code)
        menu.exec_(event.globalPos())
        event.accept()

    # Don't let right clicks do anything besides open the above context menu (i.e. don't select anything)
    def mousePressEvent(self, event):
        if event.button() != QtCore.Qt.RightButton:
            super(HexInspectorTable, self).mousePressEvent(event)

    def code_to_clipboard(self):
        item = self.itemAt(self.right_click_pos)
        item = self.item(item.row(), 1) # always copy Value column
        clipboard = QtGui.QApplication.clipboard()
        clipboard.setText(item.code)
        self.parent.statusBar().showMessage("Code copied to clipboard.", 5000)

