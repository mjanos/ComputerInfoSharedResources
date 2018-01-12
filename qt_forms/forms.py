from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QAction, QLabel, QBoxLayout, QVBoxLayout, QHBoxLayout, QLineEdit, QTextEdit, QPushButton, QProgressBar, QTabWidget, QFileDialog, QMessageBox, QScrollArea, QStatusBar
from PyQt5.QtGui import QFont
from PyQt5.QtCore import *


class BaseForm(QWidget):
    def __init__(self,parent=None,submit_callback=None,submit_callback_kwargs={},title="",clear_btn=False,default_btn=False):
        super().__init__(parent)
        self.title = title
        self.submit_callback = submit_callback
        self.submit_callback_kwargs = submit_callback_kwargs
        if title:
            self.title_label = QLabel(self.title,self)
            self.title_label.setSizePolicy(1,0)
            self.title_label.setAlignment(Qt.AlignCenter)
        self.fields = []

        self.field_frame = QWidget(self)
        self.field_frame.setSizePolicy(1,0)
        self.submit_btn = QPushButton("Submit",self)
        self.submit_btn.clicked.connect(lambda:self.run_callback())
        self.submit_btn.setSizePolicy(1,0)
        self.layout = QVBoxLayout()
        self.field_layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.field_frame.setLayout(self.field_layout)
        if title:
            self.layout.addWidget(self.title_label)
        self.layout.addWidget(self.field_frame)
        self.layout.addWidget(self.submit_btn)
        self.setSizePolicy(1,0)

    def add_field(self,field_callback,kwargs=None):
        self.fields.append(field_callback(self.field_frame,**kwargs))
        self.field_layout.addWidget(self.fields[-1])
        self.min_label_width = max([f.get_label_size() for f in self.fields])
        for f in self.fields:
            f.resize_label(self.min_label_width)
        return self.fields[-1]

    def is_valid(self):
        valid = True
        for f in self.fields:
            valid = f.is_valid()
        return valid

    def run_callback(self):
        if self.is_valid():
            self.submit_callback(**self.submit_callback_kwargs)

    def reset_fields(self):
        for f in self.fields:
            f.reset_defaults()

    def clear_fields(self):
        for f in self.fields:
            f.clear()
