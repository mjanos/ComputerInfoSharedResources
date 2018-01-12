from ..qt_forms.fields import TextField, IntField, MultiTextField, FileField,BooleanField
from ..qt_forms.forms import BaseForm
import os

class DynamicForm(BaseForm):
    def __init__(self,parent=None,submit_callback=None,submit_callback_kwargs={},title="",dynamicmodel=None):
        super().__init__(parent=parent,submit_callback=submit_callback,submit_callback_kwargs=submit_callback_kwargs,title=title)
        self.settings = dynamicmodel
        self.generate_fields()
    def generate_fields(self):
        for k,v in sorted(self.settings.settings_dict.items()):
            if type(v) is str:
                if os.path.isabs(v):
                    self.add_field(FileField,kwargs={'extensionsallowed':"CSV Files (*.csv)",'default_input':v,'label':k.title()})
                else:
                    self.add_field(TextField,kwargs={'label':k.title(),'default_input':v})
            elif type(v) is int:
                self.add_field(IntField,kwargs={'label':k.title(),'default_input':v})
            elif type(v) is list:
                self.add_field(MultiTextField,kwargs={'label':k.title(),'default_input':v})
            elif type(v) is bool:
                self.add_field(BooleanField,kwargs={'label':k.title(),'default_input':v})

    def run_callback(self):
        if self.is_valid():
            for f in self.fields:
                self.settings.settings_dict[f.get_name().lower()] = f.get_value()
            self.settings.save()
            self.submit_callback(**self.submit_callback_kwargs)
