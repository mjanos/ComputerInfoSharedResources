import json
import os
from collections import OrderedDict
from .CIPathFixes import exe_path

class BadInputException(Exception):
    pass

"""Reads and writes settings to file"""
class Settings(object):
    settings_dict = {}
    success_file = None
    success_folder = None
    read_error = None
    other_error = None
    max_key_len = 0
    read_error_dict = {}

    def __init__(self,filename_list,**kwargs):
        self.filename = filename_list
        self.default_folder = kwargs.pop('default_folder',None)
        self.default_filename = kwargs.pop('default_filename',None)
        self.read_error_dict = kwargs.pop('read_error_dict',None)
        if type(filename_list) is not list:
            raise BadInputException("Input must be type list")
        for i,f in enumerate(self.filename):
            self.filename[i] = exe_path(f)
        self.filename.append(self.default_folder + "\\" + self.default_filename)
        self.read_from_file()
        if not os.path.exists(self.default_folder + "\\" + self.default_filename):
            #self.write_to_file(local_path=self.default_folder + "\\" + self.default_filename)
            self.import_file(input_file_path=self.success_file,local_path=self.default_folder + "\\" + self.default_filename)
    def import_file(self,input_file_path=None,local_path=None):
        with open(input_file_path,"r") as input_file:
            self.settings_dict = json.loads(input_file.read(),object_pairs_hook=OrderedDict)
            for key,value in self.settings_dict.items():
                if len(key) > self.max_key_len:
                    self.max_key_len = len(key)
            self.read_error = None
            self.other_error = None
            if local_path:
                self.write_to_file(local_path=local_path)
            else:
                self.write_to_file()
    def read_from_file(self):
        """Reads from files and loads settings into dict"""
        for f in reversed(self.filename):
            try:
                with open(f,'r') as read_file:
                    self.settings_dict = json.loads(read_file.read(),object_pairs_hook= OrderedDict)
                self.success_file = f
                for key,value in self.settings_dict.items():
                    if len(key) > self.max_key_len:
                        self.max_key_len = len(key)
                self.read_error = None
                self.other_error = None
                break
            except FileNotFoundError as e:
                self.read_error = e
            except Exception as e:
                self.other_error = e
        if self.read_error_dict:
            for k,v in self.read_error_dict.items():
                if not k in self.settings_dict:
                    self.settings_dict[k] = ""
        if self.read_error:
            self.settings_dict = self.read_error_dict
            if not os.path.isdir(self.default_folder):
                os.makedirs(self.default_folder)
            with open(self.default_folder + "\\" + self.default_filename,'w+') as default_data_file:
                json.dump(self.settings_dict,default_data_file,indent = 4,ensure_ascii=False)
            self.success_folder = self.default_folder
            self.success_file = self.default_folder + "\\" + self.default_filename
    def write_to_file(self,settings_dict_mod=None,local_path=None):
        """writes settings to file"""
        if self.default_folder and not os.path.isdir(self.default_folder):
            os.makedirs(self.default_folder)
        if not local_path:
            with open(self.success_file,'w+') as write_file:
                if settings_dict_mod:
                    json.dump(settings_dict_mod, write_file, indent = 4, ensure_ascii=False)
                elif self.settings_dict:
                    json.dump(self.settings_dict,write_file, indent = 4,ensure_ascii=False)
        else:
            with open(local_path,'w+') as write_file:
                if settings_dict_mod:
                    json.dump(settings_dict_mod, write_file, indent = 4, ensure_ascii=False)
                elif self.settings_dict:
                    json.dump(self.settings_dict,write_file, indent = 4,ensure_ascii=False)
