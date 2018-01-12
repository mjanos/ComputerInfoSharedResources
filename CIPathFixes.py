import sys
import os

"""Returns directory of input"""
def exe_path(input_path):
    if getattr(sys,'frozen',False):
        ico_path = os.path.dirname(sys.executable)
    else:
        ico_path = os.path.dirname(__file__)
    return os.path.join(ico_path,input_path)
