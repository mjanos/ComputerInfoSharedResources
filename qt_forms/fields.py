import os

from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QAction, QLabel, QBoxLayout, QVBoxLayout, QHBoxLayout, QLineEdit, QTextEdit, QPushButton, QProgressBar, QTabWidget, QFileDialog, QMessageBox, QScrollArea, QStatusBar, QSizePolicy, QCheckBox
from PyQt5.QtGui import QFont
from PyQt5.QtCore import *

class TextField(QWidget):
    def __init__(self,parent,placeholder="",label=None,required=False,default_input=None,no_label=False,min_label=0):
        super().__init__(parent)
        self.default_input = default_input
        self.placeholder = placeholder
        self.required = required
        self.label = None
        self.layout = QHBoxLayout()
        if not no_label:
            self.label = QLabel(label,self)
            self.label.setMinimumWidth(min_label)
            self.label.setMaximumWidth(min_label)
            self.layout.addWidget(self.label)
            self.layout.setAlignment(self.label,Qt.AlignLeft)
        self.entry = QLineEdit(self)
        self.layout.addWidget(self.entry)
        self.setLayout(self.layout)
        self.layout.setContentsMargins(0,0,0,0)

        if self.placeholder:
            self.has_placeholder = True
            self.entry.setPlaceholderText(self.placeholder)
        else:
            self.has_placeholder = False
        self.set_default_input()

    def resize_label(self,val):
        try:
            self.label.setMinimumWidth(val)
        except:
            pass

    def get_label_size(self):
        if self.label:
            return self.label.sizeHint().width()
        else:
            return 0

    def reset_defaults(self):
        self.set_default_input()

    def clear(self):
        self.entry.setText("")

    def set_default_input(self):
        if self.default_input:
            self.entry.setText(self.default_input)

    def is_valid(self):
        valid = True
        if self.required:
            if not self.label.text():
                valid = False
        if not valid: self.invalid()
        return valid

    def has_content(self):
        if self.entry.text():
            return True
        else:
            return False

    def invalid(self):
        pass

    def get_name(self):
        return self.label.text()

    def get_value(self):
        if self.has_placeholder:
            return ""
        else:
            return self.entry.text()

class IntField(QWidget):
    def __init__(self,parent,label=None,default_input=0,low_value=-10000,high_value=10000,min_label=0):
        super().__init__(parent)
        self.label = QLabel(label,self)
        self.label.setMinimumWidth(min_label)
        self.label.setAlignment(Qt.AlignLeft)
        self.entry = QSpinBox(self)
        self.default_input = default_input
        if low_value: self.entry.setMinimum(low_value)
        if high_value: self.entry.setMaximum(high_value)
        if default_input < high_value and default_input > low_value:
            self.entry.setValue(self.default_input)
        else:
            self.entry.setValue(low_value)
        self.layout = QHBoxLayout()
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.entry)
        self.setLayout(self.layout)

    def resize_label(self,val):
        try:
            self.label.setMinimumWidth(val)
        except:
            pass

    def get_label_size(self):
        if self.label:
            return self.label.sizeHint().width()
        else:
            return 0

    def is_valid(self):
        valid = True
        try:
            int(self.entry.value())
        except ValueError:
            valid = False
        return valid
    def reset_defaults(self):
        self.entry.setValue(self.default_input)
    def clear(self):
        self.reset_defaults()

    def get_name(self):
        return self.label.text()

    def get_value(self):
        return self.entry.value()

class MultiTextField(QWidget):
    def __init__(self,parent,label=None,default_input=[],required=False,num_required=1,min_label=0):
        super().__init__(parent)
        self.required = required
        self.num_required = num_required
        self.entrys = []
        self.layout = QHBoxLayout()
        self.layout.setContentsMargins(0,0,0,0)
        self.entry_layout = QVBoxLayout()
        if label:
            self.label = QLabel(label,self)
            self.label.setMinimumWidth(min_label)
            self.label.setMaximumWidth(min_label)
            self.layout.addWidget(self.label)
        self.add_btn = QPushButton("+",self)
        self.add_btn.setMaximumWidth(25)
        self.add_btn.setMaximumHeight(25)


        self.add_btn.clicked.connect(self.add_field)
        self.layout.addLayout(self.entry_layout)


        for row,d in enumerate(default_input):
            self.entrys.append(TextField(self,default_input=d,no_label=True))
            self.entry_layout.addWidget(self.entrys[-1])
        self.entrys.append(TextField(self,no_label=True))
        self.entry_layout.addWidget(self.entrys[-1])
        self.setLayout(self.layout)
        self.layout.addWidget(self.add_btn)
        self.layout.setAlignment(self.add_btn,Qt.AlignTop)
        self.layout.setAlignment(self.label,Qt.AlignTop)
        self.layout.setAlignment(self.entry_layout,Qt.AlignTop)
        #self.entry_layout.setContentsMargins(0,0,0,0)
        #self.setContentsMargins(0,0,0,0)

    def resize_label(self,val):
        try:
            self.label.setMinimumWidth(val)
        except:
            pass

    def get_label_size(self):
        self.setSizePolicy(QSizePolicy.MinimumExpanding,QSizePolicy.MinimumExpanding)
        if self.label:
            return self.label.sizeHint().width()
        else:
            return 0


    def add_field(self):
        self.entrys.append(TextField(self,no_label=True))
        self.entry_layout.addWidget(self.entrys[-1])

    def is_valid(self):
        valid = True
        for e in self.entrys:
            if e.is_valid() == False:
                valid = False
        non_blank_fields = 0
        if self.required:
            for e in self.entrys:
                if e.has_content():
                    non_blank_fields += 1
            if non_blank_fields < self.num_required:
                valid = False
        return valid

    def reset_defaults(self):
        for e in self.entrys:
            e.reset_defaults()

    def clear(self):
        for e in self.entrys:
            e.clear()

    def get_name(self):
        if self.label:
            return self.label.text()
        else:
            return self.label

    def get_value(self):
        val_list = []
        for e in self.entrys:
            if e.get_value():
                val_list.append(e.get_value())
        return val_list

class BooleanField(QWidget):
    def __init__(self,parent,label="",default_input=False):
        super().__init__(parent)
        self.default_input = default_input
        self.check = QCheckBox(label,self)
        self.check.setCheckable(True)
        self.layout = QHBoxLayout()
        if self.default_input == True:
            self.check.setChecked(True)
        else:
            self.check.setChecked(False)
        self.label = QLabel(label,self)
        sp = self.label.sizePolicy()
        sp.setRetainSizeWhenHidden(True)
        self.label.setSizePolicy(sp)


        self.layout.addWidget(self.label)
        self.layout.addWidget(self.check)
        self.setLayout(self.layout)
        self.label.hide()

    def is_valid(self):
        return True

    def reset_defaults(self):
        if self.default_input:
            self.check.setChecked(True)
        else:
            self.check.setChecked(False)

    def clear(self):
        self.check.setChecked(True)

    def get_name(self):
        return self.check.text()

    def get_value(self):
        return self.check.isChecked()

    def resize_label(self,val):
        self.label.setMinimumWidth(val)

    def get_label_size(self):
        if self.label:
            return self.label.sizeHint().width()
        else:
            return 0

class FileField(QWidget):
    def __init__(self, parent=None, extensionsallowed=None,default_input="",required=False,label=None,min_label=0):
        super().__init__(parent)
        self.extensionsallowed = extensionsallowed
        self.required = required
        self.filename = None
        self.default_input = default_input
        self.label_text = label
        self.min_label = min_label
        self.createWidgets()
        if self.default_input:
            self.setFilename(self.default_input)
    def resize_label(self,val):
        self.label.setMinimumWidth(val)

    def get_label_size(self):
        if self.label:
            return self.label.sizeHint().width()
        else:
            return 0

    def createWidgets(self):
        self.label = QLabel(self.label_text,self)
        self.setMinimumWidth(self.min_label)
        self.filelabel = QLineEdit(self)
        self.filelabel.setText("No file selected")
        self.filelabel.setEnabled(False)
        self.filelabel.setFixedHeight(25)
        self.filelabel.setMinimumWidth(0)
        self.filebtn = QPushButton("Browse",self)
        self.filebtn.clicked.connect(self.getFilename)

        self.layout = QHBoxLayout()
        self.layout.setContentsMargins(0,0,0,0)
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.filelabel)
        self.layout.addWidget(self.filebtn)
        self.setLayout(self.layout)
        self.layout.setAlignment(self.label,Qt.AlignLeft)

    def clear(self):
        self.filename = None

    def is_valid(self):
        valid = True
        if self.filename:
            if not os.path.exists(self.filename):
                valid = False
        else:
            if self.required == True:
                valid = False
        return valid

    def getFilename(self):
        self.filename, _ = QFileDialog.getOpenFileName(self,"Pick File","",self.extensionsallowed)
        if self.filename != '':
            self.filelabel.setText(self.filename)
    def setFilename(self,input_filename):
        self.filename = input_filename
        self.filelabel.setText(self.filename)

    def reset_defaults(self):
        self.clear()
        if self.default_input:
            self.value.set(self.default_input)
            self.filename = self.default_input

    def get_name(self):
        return self.label.text()

    def get_value(self):
        return self.filename.replace("/","\\")

    def form_disable(self):
        self.filebtn.setEnabled(False)
    def form_enable(self):
        self.filebtn.setEnabled(True)
