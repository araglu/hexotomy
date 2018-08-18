from PySide import QtCore, QtGui


# how about HexAssimilate?
class HexInterpreterDetail(QtGui.QWidget):
    def __init__(self, parent):
        super(HexInterpreterDetail, self).__init__()
        self.parent = parent # parent is HexInterpreterTable!

        self.current_index = 0

        self.layout = QtGui.QVBoxLayout()
        self.setLayout(self.layout)

        self.form_layout = QtGui.QFormLayout()
        self.layout.addLayout(self.form_layout)

        self.color = QtGui.QPushButton("Change Color", self)
        self.form_layout.addRow(self.color)
        self.color.clicked.connect(self.color_clicked)

        self.name = QtGui.QLineEdit()
        self.form_layout.addRow("Name:", self.name)
        self.name.textEdited.connect(self.name_changed)

        self.start = QtGui.QSpinBox()
        self.form_layout.addRow("Start:", self.start)
        self.start.valueChanged.connect(self.start_changed)
        self.start.setMaximum(9999999)

        self.length = QtGui.QSpinBox()
        self.form_layout.addRow("Length:", self.length)
        self.length.valueChanged.connect(self.length_changed)
        self.length.setMaximum(9999999)

        self.code = QtGui.QTextEdit()
        self.form_layout.addRow("Code:", self.code)
        self.code.textChanged.connect(self.code_changed)
        self.code.policy = self.code.sizePolicy()
        self.code.policy.setVerticalStretch(1)
        self.code.setSizePolicy(self.code.policy)
        self.code.setStyleSheet("QTextEdit {font-family: 'Courier New'; font-size: 11px}")

        self.run = QtGui.QPushButton("Run", self)
        self.form_layout.addRow(self.run)
        self.run.clicked.connect(self.run_clicked)

        self.result = QtGui.QLabel()
        self.form_layout.addRow("Result:", self.result)
        # self.result.setTextInteractionFlags(QtCore.Qt.TextSelectableByKeyboard | QtCore.Qt.TextSelectableByMouse)

        self.traceback = QtGui.QTextEdit()
        self.form_layout.addRow("Traceback:", self.traceback)
        self.traceback.setTextInteractionFlags(QtCore.Qt.TextSelectableByKeyboard | QtCore.Qt.TextSelectableByMouse)
        self.traceback.setStyleSheet("QTextEdit {font-family: 'Courier New'; font-size: 11px}")

    # <sigh>
    def sizeHint(self):
        return QtCore.QSize(350, 500)
    # moo

    def fill(self, index):
        if index >= len(self.parent.interprets):
            print "(HexInterpreterDetail->fill) Tried to use index %d which doesn't exist." % (index)
        this_interpret = self.parent.interprets[index]
        self.current_index = index
        self.color.setStyleSheet("background-color: %s" % this_interpret["color"])
        self.name.setText(this_interpret["name"])
        self.start.setValue(this_interpret["start"])
        self.length.setValue(this_interpret["length"])
        self.code.setText(this_interpret["code"])
        if len(this_interpret["result"]) > 30:
            self.result.setText(this_interpret["result"][0:30] + "...") # Don't show an enormous result
        else:
            self.result.setText(this_interpret["result"])
        self.traceback.setText(this_interpret["traceback"])

        # also highlight hexview
        self.parent.parent.hex_view.select(this_interpret["start"], this_interpret["start"] + this_interpret["length"] - 1)


    def update_result(self):
        self.parent.update_interpreter_line(self.current_index)
        self.result.setText(self.parent.interprets[self.current_index]["result"])
        self.length.setValue(self.parent.interprets[self.current_index]["length"])
        self.traceback.setText(self.parent.interprets[self.current_index]["traceback"])

    @QtCore.Slot(str)
    def name_changed(self, text):
        self.parent.interprets[self.current_index]["name"] = text
        self.parent.update_interpreter_line(self.current_index)

    @QtCore.Slot(int)
    def start_changed(self, value):
        self.parent.interprets[self.current_index]["start"] = value
        self.update_result()
        this_interpret = self.parent.interprets[self.current_index]
        if (self.current_index != 0
                and self.parent.interprets[self.current_index - 1]["start"] > this_interpret["start"]):
            print "Start changed too much~ Sorting..."
            self.parent.interprets[self.current_index], self.parent.interprets[self.current_index - 1] = \
                self.parent.interprets[self.current_index - 1], self.parent.interprets[self.current_index]
            self.current_index -= 1
            self.parent.update_interpreter()
        elif (self.current_index != len(self.parent.interprets) - 1
                and self.parent.interprets[self.current_index + 1]["start"] < this_interpret["start"]):
            print "Start changed too much! Sorting..."
            self.parent.interprets[self.current_index], self.parent.interprets[self.current_index + 1] = \
                self.parent.interprets[self.current_index + 1], self.parent.interprets[self.current_index]
            self.current_index += 1
            self.parent.update_interpreter()


    @QtCore.Slot(int)
    def length_changed(self, value):
        self.parent.interprets[self.current_index]["length"] = value
        self.update_result()

    @QtCore.Slot()
    def code_changed(self):
        self.parent.interprets[self.current_index]["code"] = self.code.toPlainText()

    @QtCore.Slot()
    def run_clicked(self):
        self.update_result()

    @QtCore.Slot()
    def color_clicked(self):
        color_object = QtGui.QColorDialog.getColor(
            QtGui.QColor(self.parent.interprets[self.current_index]["color"]))
        self.parent.interprets[self.current_index]["color"] = color_object.name()
        #print "color updated to: %s" % self.parent.interprets[self.current_index]["color"]
        self.color.setStyleSheet("background-color: %s" % self.parent.interprets[self.current_index]["color"])
        self.parent.update_interpreter_line(self.current_index)
