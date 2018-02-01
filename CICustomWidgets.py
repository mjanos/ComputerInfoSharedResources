from PyQt5.QtWidgets import QLabel, QTableWidget, QDialog, QHBoxLayout, QLineEdit
from PyQt5.QtCore import Qt, QEvent, pyqtSignal

"""Label that acts more like a link with color and cursor"""
class LinkLabel(QLabel):
    def __init__(self,text,parent,link_color):
        super().__init__(text,parent)
        if link_color:
            self.setStyleSheet("color:%s" % link_color)
        self.setCursor(Qt.PointingHandCursor)

"""Table used in popout windows"""
class DialogTable(QTableWidget):
    def __init__(self,parent=None,table_headers=[]):
        super().__init__(parent)
        self.verticalHeader().setVisible(False)
        self.setColumnCount(len(table_headers))
        self.setHorizontalHeaderLabels(table_headers)
        self.setCursor(Qt.PointingHandCursor)

"""Dialog that matches parent size with custom window flags and resize grips"""
class CustomDialog(QDialog):
    def __init__(self,parent=None):
        super().__init__(parent)
        self.setWindowFlags(self.windowFlags() | Qt.WindowMaximizeButtonHint)
        self.setSizeGripEnabled(True)
        self.setMinimumSize(parent.width(),parent.height())

"""Label that has context options for left and right click"""
class CustomDataLabel(QHBoxLayout):
    def __init__(self,parent,label_title,data,width,linklabel_callback=None,callback_title=None,link_color=None):
        super().__init__()
        self.parent = parent
        self.titlelabel = QLabel(label_title,parent)
        self.titlelabel.setFixedWidth(width)
        if link_color:
            self.datalabel = LinkLabel(data,parent,link_color)
        else:
            self.datalabel = QLabel(data,parent)
        if linklabel_callback:
            self.datalabel.mouseReleaseEvent = lambda e:parent.check_mouse_btn(e,textdata=data,leftcallback=linklabel_callback,callback_label=callback_title)
        else:
            self.datalabel.mouseReleaseEvent = lambda e:parent.check_mouse_btn(e,textdata=data)
        self.addWidget(self.titlelabel)
        self.addWidget(self.datalabel)
        self.setAlignment(self.datalabel,Qt.AlignLeft)

class CustomLineEdit(QLineEdit):
    keyPressed = pyqtSignal(QEvent)
    def __init__(self,*args,**kwargs):
        self.scroll_list = kwargs.pop('scroll_list',None)
        self.active_list_element = -1
        self.initial_value = ""
        super().__init__(*args,**kwargs)
        self.keyPressed.connect(self.arrow)

    def keyPressEvent(self,event):
        super().keyPressEvent(event)
        self.keyPressed.emit(event)

    def arrow(self, event):
        if self.initial_value == "":
            self.initial_value = self.text()
        if event.key() == Qt.Key_Up:
            if self.active_list_element < len(self.scroll_list)-1:
                self.active_list_element += 1
            if self.active_list_element >= 0 and self.active_list_element < len(self.scroll_list):
                if self.scroll_list[self.active_list_element] == self.initial_value and self.active_list_element < len(self.scroll_list)-1:
                    self.active_list_element += 1
                self.setText(self.scroll_list[self.active_list_element])
                self.selectAll()
        elif event.key() == Qt.Key_Down:
            if self.active_list_element >= 0:
                self.active_list_element -= 1
            if self.active_list_element >= 0 and self.active_list_element < len(self.scroll_list):
                self.setText(self.scroll_list[self.active_list_element])
                self.selectAll()

    def update_list(self,input_list):
        self.scroll_list = input_list
