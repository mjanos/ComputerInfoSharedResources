import copy
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QAction, QLabel, QBoxLayout, QVBoxLayout, QHBoxLayout, QLineEdit, QTextEdit, QPushButton, QProgressBar, QGroupBox, QFormLayout, QFileDialog, QCheckBox
from PyQt5.QtCore import *

"""Custom Forms for Single/Multiple Computer Info"""

class AuthenticationForm(QWidget):
    """
    QWidget form class that includes a usernamefield and password
    Has 'all_btns' parameter that determines if buttons are rendered. Useful for bulk installs.
    """
    def __init__(self, parent=None, title="Authentication",default_username=None, default_password=None, columnspan=1,all_btns=True,save_callback=None):
        super().__init__(parent)
        self.title = title
        self.input_username = default_username
        self.input_password = default_password
        self.all_btns = all_btns
        self.save_callback = save_callback
        self.createWidgets()
    def createWidgets(self):
        self.userrow = QWidget()
        self.userlabel = QLabel('Username',self.userrow)
        self.usernamefield = QLineEdit(self.userrow)

        if self.input_username and not str(self.usernamefield.text()):
            #self.usernamefield.delete(0,END)
            self.usernamefield.setText(self.input_username)

        self.passrow = QWidget()
        self.passlabel = QLabel("Password",self.passrow)
        self.passwordfield = QLineEdit(self.passrow)
        self.passwordfield.setEchoMode(2)

        if self.input_password and not str(self.passwordfield.get()):
            #self.passwordfield.clear()
            self.passwordfield.setText(self.input_password)

        if self.all_btns:
            self.submit = QPushButton("Submit",self)
            self.submit.clicked.connect(self.alt_user_save)
            self.discard = QPushButton("Clear User",self)
            self.discard.clicked.connect(self.alt_user_clear)

        self.groupbox = QGroupBox(self.title)
        self.layout = QFormLayout()

        self.userrow_layout = QHBoxLayout()
        self.userrow_layout.addWidget(self.userlabel)
        self.userrow_layout.addWidget(self.usernamefield)
        self.userrow.setLayout(self.userrow_layout)

        self.passrow_layout = QHBoxLayout()
        self.passrow_layout.addWidget(self.passlabel)
        self.passrow_layout.addWidget(self.passwordfield)
        self.passrow.setLayout(self.passrow_layout)

        if self.all_btns:
            self.btnrow_layout = QHBoxLayout()
            self.btnrow_layout.addWidget(self.submit)
            self.btnrow_layout.addWidget(self.discard)

        self.layout.addRow(self.userrow)
        self.layout.addRow(self.passrow)
        if self.all_btns:
            self.layout.addRow(self.btnrow_layout)

        self.groupbox.setLayout(self.layout)
        self.mainlayout = QVBoxLayout()
        self.mainlayout.addWidget(self.groupbox)
        self.setLayout(self.mainlayout)

    def alt_user_save(self,event=None,skip_check=False):
        self.username = self.usernamefield.text()
        self.password = self.passwordfield.text()
        valid = True
        if not skip_check:
            if not self.username:
                valid = False
                self.userlabel.setStyleSheet("QLabel {color:red;}")
            else:
                self.userlabel.setStyleSheet("QLabel {color:black;}")
            if not self.password:
                valid = False
                self.passlabel.setStyleSheet("QLabel {color:red;}")
            else:
                self.passlabel.setStyleSheet("QLabel {color:black;}")

        if valid:
            if self.save_callback:
                self.save_callback()
            try: self.master.bubbleuplabel()
            except: pass
    def alt_user_clear(self,event=None):
        self.usernamefield.clear()
        self.passwordfield.clear()
        self.alt_user_save(skip_check=True)
    def form_disable(self):
        self.usernamefield.setEnabled(False)
        self.passwordfield.setEnabled(False)
    def form_enable(self):
        self.usernamefield.setEnabled(True)
        self.passwordfield.setEnabled(True)

class FileForm(QWidget):
    """
    QWidget form class that generates file picker and handles getting the filename
    """

    form_change = pyqtSignal(str)

    def __init__(self, parent=None, extensionsallowed=None, title="Pick File",input_filename=None):
        super().__init__(parent)
        self.extensionsallowed = extensionsallowed
        self.title = title
        self.extra_fields = []
        self.extra_labels = []
        self.filename = None
        if not input_filename is None:
            self.setFilename(input_filename)
        self.createWidgets()
    def createWidgets(self):
        self.filelabel = QLineEdit(self)
        self.filelabel.setText("No file selected")
        self.filelabel.setEnabled(False)
        self.filelabel.setFixedHeight(25)
        self.filelabel.setSizePolicy(0,1)
        self.filebtn = QPushButton("Browse",self)
        self.filebtn.clicked.connect(self.getFilename)

        self.groupbox = QGroupBox(self.title)
        self.layout = QHBoxLayout()
        self.layout.addWidget(self.filelabel)
        self.layout.addWidget(self.filebtn)
        self.groupbox.setLayout(self.layout)
        self.mainlayout = QVBoxLayout()
        self.mainlayout.addWidget(self.groupbox)
        self.setLayout(self.mainlayout)

    def getFilename(self):
        self.filename, _ = QFileDialog.getOpenFileName(self,"Pick File","",self.extensionsallowed)
        if self.filename != '':
            self.filelabel.setText(self.filename)
            self.form_change.emit(self.filename)
    def setFilename(self,input_filename):
        self.filename = input_filename
        self.filelabel.text(self.filename)

    def form_disable(self):
        print("disabling...")
        self.filebtn.setEnabled(False)
        for f in self.extra_fields:
            f.setEnabled(False)
    def form_enable(self):
        self.filebtn.setEnabled(True)
        for f in self.extra_fields:
            f.setEnabled(True)

    def add_field(self,field_name):
        self.extra_fields.append(QLineEdit())
        self.extra_labels.append(QLabel(field_name))
        self.mainlayout.addWidget(self.extra_labels[-1])
        self.mainlayout.addWidget(self.extra_fields[-1])

    def get_field_list(self):
        field_values = []
        for field in self.extra_fields:
            field_values.append(field.text())
        return field_values

    def remove_fields(self):
        for f in self.extra_fields:
            self.mainlayout.removeWidget(f)
        for l in self.extra_labels:
            self.mainlayout.removeWidget(l)
        self.extra_fields = []
        self.extra_labels = []

class ShortcutCheckboxForm(QWidget):
    """
    QWidget form class that generates the checkboxes for copying icons
    """
    def __init__(self, parent=None, title="Select Choices"):
        super().__init__(parent=parent)
        self.title = title
        self.createWidgets()
    def createWidgets(self):

        self.check1 = QPushButton('Public Desktop',self)
        self.check1.setCheckable(True)

        self.check2 = QPushButton('Other Profiles Desktops',self)
        self.check2.setCheckable(True)

        self.check3 = QPushButton('Startup Folder',self)
        self.check3.setCheckable(True)

        self.check1.setChecked(True)
        self.check2.setChecked(True)

        self.groupbox = QGroupBox(self.title)
        self.layout = QFormLayout()
        self.layout.addRow(self.check1)
        self.layout.addRow(self.check2)
        self.layout.addRow(self.check3)
        self.groupbox.setLayout(self.layout)
        self.mainlayout = QVBoxLayout()
        self.mainlayout.addWidget(self.groupbox)
        self.setLayout(self.mainlayout)

    def form_disable(self):
        self.check1.setEnabled(False)
        self.check2.setEnabled(False)
        self.check3.setEnabled(False)
    def form_enable(self):
        self.check1.setEnabled(True)
        self.check2.setEnabled(True)
        self.check3.setEnabled(True)

class AppsCheckForm(QWidget):
    def __init__(self,parent=None,text=None,sub_text="Install if DNE",sub_text_bool=False):
        super().__init__(parent)
        self.text = text
        self.sub_text = sub_text
        self.sub_text_bool = sub_text_bool
        self.create_widgets()
    def create_widgets(self):
        self.main_check = QCheckBox(self.text,self)
        self.main_check.toggled.connect(self.main_toggled)
        self.mainlayout = QVBoxLayout()
        self.mainlayout.addWidget(self.main_check)
        if self.sub_text_bool:
            self.sub_frame = QWidget(self)
            self.sub_check = QCheckBox(self.sub_text,self.sub_frame)
            self.sub_frame_layout = QHBoxLayout()
            self.sub_frame_layout.addWidget(self.sub_check)
            self.sub_frame.setLayout(self.sub_frame_layout)

            if not self.main_check.isChecked():
                self.sub_check.setEnabled(False)
            self.mainlayout.addWidget(self.sub_frame)
            self.mainlayout.setContentsMargins(10,0,0,0)
            self.mainlayout.setSpacing(0)
        else:
            self.sub_check = None
        self.setLayout(self.mainlayout)
    def set(self,num):
        self.main_check.setChecked(num)
        if not self.main_check.isChecked():
            self.sub_set(False)
        self.main_toggled()
    def sub_set(self,num):
        if self.sub_text_bool:
            self.sub_check.setChecked(num)
    def get(self):
        return self.main_check.isChecked()
    def sub_get(self):
        if self.sub_check:
            return self.sub_check.isChecked()
        else:
            return False
    def main_toggled(self):
        if self.sub_text_bool:
            if self.main_check.isChecked():
                self.sub_check.setEnabled(True)
            else:
                self.sub_set(False)
                self.sub_check.setEnabled(False)

    def enable(self):
        self.main_check.setEnabled(True)
        if self.sub_text_bool:
            self.sub_check.setEnabled(True)
    def disable(self):
        self.main_check.setEnabled(False)
        if self.sub_text_bool:
            self.sub_check.setEnabled(False)

class AppsForm(QWidget):
    def __init__(self,parent=None,programs_obj=None,title="Find Apps"):
        super().__init__(parent)
        self.title = title
        self.programs_obj = programs_obj
        self.widget_list = []
        self.create_widgets()
    def create_widgets(self):
        def select_all():
            [w.set(True) for w in self.widget_list]
        def select_none():
            [w.set(False) for w in self.widget_list]

        self.groupbox = QGroupBox(self.title)
        self.layout = QFormLayout()
        for i,app in enumerate(sorted(self.programs_obj.dict_list,key=lambda k: k['title'])):
            if 'script_path' in app:
                self.widget_list.append(AppsCheckForm(self,text=app['title'].title(),sub_text_bool=True))
            else:
                self.widget_list.append(AppsCheckForm(self,text=app['title'].title()))
            self.layout.addRow(self.widget_list[-1])
        self.btnframe = QWidget()
        self.btnframe_layout = QHBoxLayout()
        self.btnframe.setLayout(self.btnframe_layout)
        self.all_btn = QPushButton("Select All",self.btnframe)
        self.all_btn.clicked.connect(select_all)
        self.none_btn = QPushButton("Select None",self.btnframe)
        self.none_btn.clicked.connect(select_none)

        self.btnframe_layout.addWidget(self.all_btn)
        self.btnframe_layout.addWidget(self.none_btn)

        self.layout.addRow(self.btnframe)
        self.groupbox.setLayout(self.layout)
        self.mainlayout = QVBoxLayout()
        self.mainlayout.addWidget(self.groupbox)
        self.setLayout(self.mainlayout)

    def form_disable(self):
        self.all_btn.setEnabled(False)
        self.none_btn.setEnabled(False)
        for w in self.widget_list:
            w.disable()
    def form_enable(self):
        self.all_btn.setEnabled(True)
        self.none_btn.setEnabled(True)
        for w in self.widget_list:
            w.enable()
