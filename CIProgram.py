from winreg import *
from .CISettings import Settings
from .CIStorage import Program
import json
import os
import re
from .CIPathFixes import exe_path

"""Retrieves Uninstall keys from registry"""
def get_program_from_registry(input_name,reg_path,search_terms,exclude_terms,debug=False):
    programlist = []
    try:
        remote_registry = ConnectRegistry(input_name,HKEY_LOCAL_MACHINE)
        remote_key = OpenKey(remote_registry,reg_path)
        for i in range(1,1500):
            found = None
            try:
                inner_key = EnumKey(remote_key,i)
                inner_open_key = OpenKey(remote_key,inner_key)
                prog = Program()
                prog.name = QueryValueEx(inner_open_key,"DisplayName")[0]
                prog.date = QueryValueEx(inner_open_key,"InstallDate")[0]
                prog.version = QueryValueEx(inner_open_key,"DisplayVersion")[0]
                if search_terms:
                    for n in search_terms:
                        if not n.lower() in prog.name.lower():
                            found = False
                    for n in exclude_terms:
                        if n.lower() in prog.name.lower():
                            found = False
                    if found != False and prog.name:
                        if re.search("[A-Za-z]",prog.name) and not [p for p in programlist if p.name.lower() == prog.name.replace("\xae","").lower()]:
                            programlist.append(prog)
                else:
                    if re.search("[A-Za-z]",prog.name) and not [p for p in programlist if p.name.lower() == prog.name.replace("\xae","").lower()]:
                        programlist.append(prog)
            except FileNotFoundError:
                pass
            except OSError as e:
                if isinstance(e,WindowsError) and e.winerror == 259:
                    pass
                else: raise
            except Exception as e:
                raise
    except Exception as e:
        if debug:
            print(e)
        else:
            pass
    return programlist

"""Read JSON file to get options for what applications can be searched from "Find Apps""""
class ProgramChoices(Settings):
    def __init__(self,filename_list,**kwargs):
        self.filename = filename_list
        self.default_folder = kwargs.pop('default_folder',None)
        self.default_filename = kwargs.pop('default_filename',None)
        self.filename.append(self.default_folder + "\\" + self.default_filename)
        self.other_error = None
        self.read_error = None
        self.dict_list = []
        self.read_error_dict = {}
        self.max_key_len = 0
        for i,f in enumerate(self.filename):
            self.filename[i] = exe_path(f)
        self.read_from_file()
        if not os.path.exists(self.default_folder + "\\" + self.default_filename):
            self.write_to_file()

    def read_from_file(self):
        for f in reversed(self.filename):
            try:
                with open(f,'r') as read_file:
                    self.dict_list = json.loads(read_file.read())
                self.success_file = f
                self.read_error = None
                self.other_error = None
                break
            except FileNotFoundError as e:
                self.read_error = e
            except Exception as e:
                self.other_error = e

    def write_to_file(self):
        try:
            if self.default_folder and not os.path.isdir(self.default_folder):
                os.makedirs(self.default_folder)
            with open(self.default_folder + "\\" + self.default_filename,'w') as write_file:
                json.dump(self.dict_list, write_file, indent = 4, ensure_ascii=False)
        except Exception as e:
            print(e)
