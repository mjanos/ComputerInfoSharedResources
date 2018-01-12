import os
from collections import OrderedDict
import json

class DynamicModel(object):
    settings_dict = {}
    read_error = None
    other_error = None
    max_key_len = 0
    read_error = ""

    def __init__(self,master_file,user_file,**kwargs):
        self.master_file = master_file
        self.user_file = user_file

        if os.path.exists(self.user_file):
            self.read(self.user_file)
        else:
            self.read(self.master_file)
            self.save()

    def read(self,file_to_read):
        """Reads from files and loads settings into dict"""
        try:
            with open(file_to_read,'r') as read_file:
                self.settings_dict = json.loads(read_file.read())
        except Exception as e: self.read_error = e
    def save(self):
        """writes settings to file"""
        with open(self.user_file,'w') as write_file:
            json.dump(self.settings_dict,write_file, indent = 4,ensure_ascii=False)
