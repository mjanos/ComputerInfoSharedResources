import subprocess
import wmi
import threading
import sys
import win32com.client, pywintypes
import pythoncom
import math
import socket
import queue
import time

import os
from shutil import copy2
import re
from winreg import *
import traceback
from .CIProgram import get_program_from_registry
from .CIStorage import MappedUser, NetworkUser, Disk, Printer,Program

"""
Classes and Functions to find Information about remote computers
"""

class DNSException(Exception):
    pass

ignored_usb = ["USB Root Hub",
                "Generic USB Hub",
                "USB Composite Device",
                "HID-compliant device",
                "HID Keyboard Device",
                "USB Input Device",
                "HID-compliant mouse",
                "HID-compliant consumer control device",
                "Intel(R) USB 3.0 Root Hub",
                "USB Human Interface Device",
                "Logitech"
            ]


class ComputerInfo(object):
    """
    Gets and stores computer info.
    """
    def __init__(self,q=None,qs=None,**kwargs):
        self.other_applications = kwargs.pop('other_applications',None)
        self.input_name=kwargs.pop('input_name',None)
        self.name=kwargs.pop('name',None)
        self.serial=kwargs.pop('serial',None)
        self.make=kwargs.pop('make',None)
        self.model=kwargs.pop('model',None)
        self.user=kwargs.pop('user',None)
        self.status=kwargs.pop('status',None)
        self.count=kwargs.pop('count',None)
        self.resolution=kwargs.pop('resolution',None)
        self.os=kwargs.pop('os',None)
        self.cpu=kwargs.pop('cpu',None)
        self.memory=kwargs.pop('memory',None)
        self.icon = kwargs.pop('icon',None)
        self.admin = kwargs.pop('admin',None)
        self.domainUserName = kwargs.pop('domainUserName',None)
        self.domainPasswd = kwargs.pop('domainPasswd',None)
        self.userName = kwargs.pop('userName',None)
        self.passwd = kwargs.pop('passwd',None)
        self.public_check = kwargs.pop('public',None)
        self.startup_check = kwargs.pop('startup',None)
        self.manual_user = kwargs.pop('manual_user',None)
        self.manual_pass = kwargs.pop('manual_pass',None)
        self.shortcut_filename = kwargs.pop('shortcut_filename',None)
        self.input_domain = kwargs.pop('input_domain',None)
        self.input_group = kwargs.pop('input_group',None)
        self.get_devices_bool = kwargs.pop('get_devices',None)
        self.get_monitors_bool = kwargs.pop('get_monitors',None)
        self.get_printers_bool = kwargs.pop('get_printers',None)
        self.get_apps_bool = kwargs.pop('get_apps',None)
        self.get_citrix_office_bool = kwargs.pop('get_citrix_office',None)
        self.install_applications = kwargs.pop('install_applications',None)
        self.single_app_install = kwargs.pop('single_app_install',None)
        self.other_profiles = kwargs.pop('other_profiles',None)
        self.profile_list = kwargs.pop('profile_list',[])
        self.debug = kwargs.pop('debug',False)
        self.profile = kwargs.pop('profile',False)
        self.verbose = kwargs.pop('verbose',False)
        self.manual_install_path = ""
        self.debug_log = ""
        self.out1 = ""
        self.out1_err = ""
        self.out2 = ""
        self.out2_err = ""

        self.programlist = []
        self.full_programlist = []
        self.found_apps = {}
        self.install_status = {}
        self.programstring = []
        if q:
            self.q = q
        else:
            self.q = queue.Queue(maxsize=1)
        self.manual_install_queue = queue.Queue(maxsize=1)
        self.monitors = 0
        self.printers=[]
        self.disks=[]
        self.networkusers = []
        self.monitors_detail = []
        self.users = {}
        self.icon_retval = None
        self.show_admin_btn = False
        self.ip_addresses = []
        self.devices = []
        self.full_error = None
        self.dns_error = False
        self.icon_status = {}
        self.paths = {}
        self.profile_time = None
        self.printer_queue = queue.Queue()
        self.programs_queue = queue.Queue()
        self.devices_queue = queue.Queue()
        self.drives_queue = queue.Queue()
        self.single_install_status = -1
        self.local = False
        self.done_processing = False
        if type(self.input_name) is str: self.input_name = self.input_name.strip()
        #self.create_paths()

    def set_manual_install_path(self,path):
        self.manual_install_path = path

    def start_service(self):
        service_name = "dwmrcs"
        retval = -1
        pythoncom.CoInitialize()
        try:
            self.search = self.wmi_wrapper(self.input_name,find_classes=False)
            for i in self.search.Win32_Service(['Name','Started'],Name=service_name):
                if i.Started:
                    retval = 0
                else:
                    retval = i.StartService()
        except Exception as e:
            self.debug_print(e)
        pythoncom.CoUninitialize()
        return retval

    def debug_print(self,data):
        if self.debug:
            print(data)
            self.debug_log = self.debug_log + "\n" + str(data)
    def verbose_print(self,data):
        if self.debug and self.verbose:
            print(data)
    def check_local(self):
        if self.admin:
            self.admin_status = self.add_admin(self.input_domain,self.input_group)
        try:
            s = wmi.WMI()
            testName = None

            for i in s.Win32_ComputerSystem():
                testName = i.Name
            if testName.lower().strip() == self.input_name.lower().strip():
                return True
            else:
                return False
        except Exception as e:
            self.debug_print(e)
            return False
    def wmi_wrapper(self,*args, **kwargs):
        """wrapper for the WMI class that allows for custom users and passwords"""
        if self.manual_user and self.manual_pass and not self.local:
            if self.manual_user.find("\\") == -1:
                self.manual_user = self.input_name + "\\" + self.manual_user
            kwargs['user'] = self.manual_user
            kwargs['password'] = self.manual_pass
        return wmi.WMI(*args,**kwargs)
    def ping_test(self,input_name):
        if input_name:
            ping_result = None
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = subprocess.SW_HIDE
            try:
                ping_result = subprocess.Popen(["ping","-n","1",input_name],stdout = subprocess.PIPE,stderr=subprocess.PIPE,stdin=subprocess.PIPE,shell=False, startupinfo=startupinfo)
            except OSError:
                pass
            if not ping_result is None:
                ping_result.communicate()
                return ping_result.returncode
            else:
                return -45
        else:
            return -1
    def get_info(self):
        """Main running class to get all the info."""
        if self.profile:
            start_time = time.time()
        def comp_system():
            for i in self.search.Win32_ComputerSystem(['Name','Manufacturer','UserName','Model','TotalPhysicalMemory']):
                if i.Name:
                    self.name = i.Name

                re_ip = re.compile('\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$')
                try:
                    self.name = self.name.lower().strip()
                except:pass
                if self.input_name.lower().strip() != self.name and not re_ip.match(self.input_name):
                    raise DNSException("Computer names do not match(%s)(%s)" % (self.input_name.lower().strip(),self.name))

                if i.Manufacturer:
                    self.make = i.Manufacturer

                if i.UserName:
                    self.user = i.UserName

                if i.Model:
                    self.model = i.Model

                if i.TotalPhysicalMemory:
                    self.memory = str(math.ceil(int(i.TotalPhysicalMemory)/1073741824)) + " GB"

            for i in self.search.Win32_SystemEnclosure(['SerialNumber']):
                if i.SerialNumber:
                    self.serial = i.SerialNumber
            try:
                for i in self.search.Win32_Processor(['Name']):
                    if i.Name:
                        self.cpu = i.Name
            except Exception as e: self.debug_print(e)

            try:
                for i in self.search.Win32_OperatingSystem(['Name']):
                    if i.Name:
                        try:
                            os_re = re.search("(Microsoft[\s]+)([^|]+)",i.Name)
                            self.os = os_re.group(2)
                        except:
                            if i.Name.find("Windows 7") != -1:
                                self.os = "Windows 7"
                            elif i.Name.find("Windows XP") != -1:
                                self.os = "Windows XP"
                            elif i.Name.find("Windows 8") != -1:
                                self.os = "Windows 8"
                            elif i.Name.find("Windows 10") != -1:
                                self.os = "Windows 10"
                            else:
                                self.os = "Other OS"

                for i in self.search.Win32_Processor(['DeviceID','AddressWidth']):
                    if i.DeviceID.lower().strip()=="cpu0" and str(i.AddressWidth).strip()=="64":
                        self.os = self.os + " x64"
                    else:
                        self.os = self.os + " x86"

            except Exception as e: self.debug_print(e)
            mon_count = 0
            start_bench = time.time()

            self.monitors = self.get_monitors(quick_info=False)
            self.ip_addresses.append(socket.gethostbyname(self.input_name))
            self.status = None
            self.debug_print("%s time to run thread" % (time.time()-start_bench))

        def lookup():
            self.verbose_print("Trying %s..." % self.input_name)
            return_value = None
            if not self.local:
                ping_result = self.ping_test(self.input_name)

                if ping_result == 0:
                    try:
                        self.search = self.wmi_wrapper(self.input_name,find_classes=False)
                        comp_system()
                        return_value = 0
                        self.status = None
                    except pythoncom.com_error as e:
                        exec_type, exec_value, exec_traceback = sys.exc_info()
                        self.debug_print(exec_value)
                        self.name = self.input_name
                        self.status = str(exec_value)
                        self.debug_print("-----------------")
                        self.debug_print("%s -- %s" % (e,self.input_name))
                        self.full_error = e
                        self.debug_print("-----------------")

                        return_value = 1
                    except wmi.x_wmi as e:
                        self.name = self.input_name
                        try:
                            temp = e.com_error.excepinfo
                            self.status = str(e.com_error.excepinfo[2])
                            self.show_admin_btn = True
                        except:
                            try:
                                self.status = str(e.com_error.strerror)
                            except:
                                self.status = str(e.com_error)
                            if self.status == "Access is denied.":
                                self.show_admin_btn = True
                        self.debug_print("+++++++++++++++++")
                        self.debug_print("%s -- %s" % (e,self.input_name))
                        self.full_error = e
                        self.debug_print("+++++++++++++++++")
                        return_value = 2
                    except DNSException as e:
                        self.name = self.input_name
                        self.status = "Computer Name Mismatch"
                        self.debug_print(e)
                        return_value = 7


                    except Exception as e:
                        #exc_type, exc_obj, exc_tb = sys.exc_info()
                        #fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                        #print()
                        self.debug_print("====================")
                        #self.debug_print("%s -- %s -- %s" % (exc_type, fname, exc_tb))
                        self.debug_print(traceback.format_exc())
                        #self.full_error = e
                        self.debug_print("====================")
                        self.name = self.input_name
                        self.status = str("Unknown Error")
                        self.debug_print(e)
                        return_value = 3

                else:
                    self.name = self.input_name
                    self.status = "Unavailable"
                    return_value = 4
            else:
                try:
                    self.search = self.wmi_wrapper(self.input_name,find_classes=False)
                    comp_system()
                    return_value = 0

                except pythoncom.com_error as e:
                    exec_type, exec_value, exec_traceback = sys.exc_info()
                    self.debug_print("......" + str(self.input_name) + ".......")
                    self.debug_print(exec_value)
                    self.status = str(exec_value.com_error.strerror)
                    return_value = 5

                except Exception as e:
                    exec_type, exec_value, exec_traceback = sys.exc_info()
                    self.debug_print("......" + str(self.input_name) + ".......")
                    self.debug_print(exec_value)
                    self.name = self.input_name
                    self.status = str(exec_type)
                    return_value = 6
            return return_value

        self.local = self.check_local()
        exit_code = lookup()
        if exit_code == 0:
            if self.get_devices_bool: self.get_devices()
            if self.get_monitors_bool: self.get_monitors()
            if self.single_app_install:
                self.single_install_status = -1
                self.single_install_status = self.run_script({'script_path':self.single_app_install})
                if self.single_install_status == 0:
                    self.single_install_status = "Success"
            if self.other_applications and self.get_apps_bool:
                for x in self.other_applications:
                    if 'show version' in x and x['show version']==True:
                        get_version = True
                    else:
                        get_version = False
                    self.found_apps[x['title']] = self.get_specific_program(search_terms=x['includes'],exclude_terms=x['excludes'],live=True,get_version=get_version,fresh=False)
                for x in self.install_applications:
                    if 'script_path' in x:
                        if 'show version' in x and x['show version']==True:
                            get_version = True
                        else:
                            get_version = False

                        if not self.found_apps[x['title']]:
                            temp_return = -1
                            self.install_status[x['title']] = temp_return = self.run_script(x)
                            if temp_return == 0:
                                self.found_apps[x['title']] = self.get_specific_program(search_terms=x['includes'],exclude_terms=x['excludes'],live=True,get_version=get_version,fresh=True)
                        else:
                            self.install_status[x['title']] = "Already Installed"
            if self.icon: self.copy_icons()

        if self.profile:
            self.profile_time = time.time() - start_time
        if self.get_printers_bool:
            self.get_printers()
        self.q.put(self,True,60)
        self.done_processing = True
    def add_admin(self,domain,bindUser):
        """Add bindUser to local 'Administrators' group"""
        NS = win32com.client.Dispatch('ADSNameSpaces')
        retval = "Unknown Error"
        if self.userName and self.passwd:
            dso = NS.getobject('','WinNT:')
            try:
                group = dso.OpenDSObject('WinNT://' + domain + '/' + self.input_name + '/Administrators,group', self.input_name + "\\" + self.userName, self.passwd, 1)
                if self.domainUserName and self.domainPasswd:
                    user = dso.OpenDSObject('WinNT://' + domain + '/' + bindUser + ',group', self.domainUserName, self.domainPasswd, 1)
                else:
                    user = NS.getobject('','WinNT://' + domain + '/' + bindUser + ',group')
                if not group.IsMember(user.ADsPath):
                    group.Add(user.ADsPath)
                    retval = "Added to group"
                else:
                    retval = "Already added to Admin Group"
            except Exception as e:
                exec_type, exec_value, exec_traceback = sys.exc_info()
                #self.debug_print("---------" + self.input_name + "--------")
                #self.debug_print(exec_value)
                retval = "Authentication Failed"
        else:
            retval = "Invalid Credentials"
        return retval
    def create_paths(self):
        """Generates paths for dropping icons"""
        if self.public_check: self.paths['public desktop'] = {'path':"\\\\%s\\c$\\users\\public\\desktop" % (self.input_name),'result':None}
        if self.other_profiles:
            for p in self.profile_list:
                if p:
                    self.paths[p + " desktop"] = {'path':"\\\\%s\\c$\\users\\%s\\desktop" %(self.input_name,p),'result':None}
        if self.startup_check: self.paths['startup folder'] = {'path':"\\\\%s\\c$\\programdata\\microsoft\\windows\\start menu\\programs\\startup" % (self.input_name),'result':None}
    def copy_icons(self):
        self.create_paths()
        """Copies icons to paths and specifies if the operation completed, the folder does not exist (DNE) or other error"""
        self.debug_print("Copying to %s" % self.input_name)
        if self.input_name and self.shortcut_filename:
            for s,v in self.paths.items():
                try:
                    if os.path.isdir(v['path']):
                         public_result = copy2(self.shortcut_filename,v['path'])
                         v['result'] = "Done"
                    else:
                         v['result'] = "DNE"
                except Exception as e:
                    self.icon_retval = v['result'] = "Error Copying Icons"
                    self.debug_print(e)
    def get_printers(self):
        """Returns printers of computer. Designed to be thread safe"""
        self.printers = []
        pythoncom.CoInitialize()
        try:
            self.search = self.wmi_wrapper(self.input_name,find_classes=False)
            for i in self.search.Win32_Printer(['Name','PortName']):
                self.printers.append(Printer(printer=i.Name,port=i.PortName))
        except Exception as e:
            self.debug_print(e)
        pythoncom.CoUninitialize()
        self.printer_queue.put(self.printers)
    def get_users(self):
        """Get users information to help find drives later"""
        pythoncom.CoInitialize()
        self.networkusers = []
        try:
            self.search = self.wmi_wrapper(self.input_name,find_classes=False)
            for i in self.search.Win32_NetworkLoginProfile(['Name','FullName','HomeDirectory','LastLogon','LogonServer']):
                if i.UserType:
                    n = NetworkUser()
                    n.name = i.Name
                    n.full_name = i.FullName
                    n.home_directory = i.HomeDirectory
                    n.last_log = i.LastLogon
                    n.logon_server = i.LogonServer
                    self.networkusers.append(n)

        except Exception as e:
            self.debug_print(e)
        pythoncom.CoUninitialize()
    def get_disks(self):
        """Gets mapped drives per user"""
        pythoncom.CoInitialize()
        try:
            self.search = self.wmi_wrapper(self.input_name,find_classes=False)
            for i in self.search.Win32_MappedLogicalDisk(['SystemName','Name','ProviderName','SessionID']):
                self.disks.append(Disk(systemname=i.SystemName,name=i.Name,path=i.ProviderName,sessionid=i.SessionID))
                if str(i.SessionID) in self.users:
                    self.users[str(i.SessionID)].add_disk(disk=self.disks[-1])
                else:
                    self.users[str(i.SessionID)] = MappedUser(sessionid=i.SessionID)
                    self.users[str(i.SessionID)].add_disk(self.disks[-1])
            for key,value in self.users.items():
                value.get_name()
        except Exception as e:
            self.debug_print(e)
        pythoncom.CoUninitialize()
        self.drives_queue.put(True)
    def get_devices(self):
        """Find devices such as scanners. ***WIP***"""
        pythoncom.CoInitialize()
        try:
            self.search = self.wmi_wrapper(self.input_name,find_classes=False)
            for i in self.search.Win32_USBControllerDevice(['Dependent']):
                if not i.Dependent.Caption in ignored_usb:
                    self.devices.append(i.Dependent.Caption)
        except Exception as e:
            self.debug_print(e)
        pythoncom.CoUninitialize()
        if not self.devices:
            try:
                remote_registry = ConnectRegistry(self.input_name,HKEY_LOCAL_MACHINE, access=KEY_READ | KEY_WOW64_64KEY)
                remote_key = OpenKey(remote_registry,r"SOFTWARE\Wow6432Node\Microsoft\Windows\CurrentVersion\Uninstall")
                for i in range(1,5000):
                    try:
                        inner_key = EnumKey(remote_key,i)
                        inner_open_key = OpenKey(remote_key,inner_key)
                        program_name = QueryValueEx(inner_open_key,"DisplayName")[0]
                        if "scansnap" in program_name.lower() or "fi-" in program_name.lower():
                            self.devices.append(program_name)
                            break
                    except FileNotFoundError:
                        pass
                    except:
                        break
            except:pass

        self.devices_queue.put(self.devices)
    def get_monitors(self,quick_info=False):
        """Gets monitor information from registry"""
        mon_count = 0

        try:
            remote_registry = ConnectRegistry(self.input_name,HKEY_LOCAL_MACHINE)
            remote_key = OpenKey(remote_registry,r"SYSTEM\ControlSet001\Enum\DISPLAY")
            for r in self.rec_keys(remote_key): self.monitors_detail.append(r)
        except: pass

        mon_count = 0
        mon_count_backup = 0
        self.search = self.wmi_wrapper(self.input_name,find_classes=False)
        for i in self.search.Win32_PnPEntity(['service'],service='monitor'):
            mon_count += 1

        if not quick_info:
            try:
                for i in self.search.Win32_VideoController(['CurrentHorizontalResolution','CurrentVerticalResolution']):
                    if i.CurrentHorizontalResolution and i.CurrentHorizontalResolution > 0:
                        mon_count_backup += 1
                        if self.resolution:
                            self.resolution = self.resolution + "\nScreen {0}: {1} x {2}".format(mon_count_backup, i.CurrentHorizontalResolution,i.CurrentVerticalResolution)
                        else:
                            self.resolution = "Screen {0}: {1} x {2}".format(mon_count_backup, i.CurrentHorizontalResolution,i.CurrentVerticalResolution)
            except:
                raise
                self.resolution = ""
                mon_count_backup = 0
                try:
                    self.search = self.wmi_wrapper(self.input_name,find_classes=False)
                    for i in self.search.VideoController(['CurrentHorizontalResolution','CurrentVerticalResolution']):
                        #print(i)
                        if i.CurrentHorizontalResolution and i.CurrentHorizontalResolution > 0:
                            mon_count_backup += 1
                            if self.resolution:
                                self.resolution = self.resolution + "\nScreen {0}: {1} x {2}".format(mon_count_backup, i.CurrentHorizontalResolution,i.CurrentVerticalResolution)
                            else:
                                self.resolution = "Screen {0}: {1} x {2}".format(mon_count_backup, i.CurrentHorizontalResolution,i.CurrentVerticalResolution)
                except: pass
        if not mon_count:
            mon_count = mon_count_backup
        return mon_count
    def run_script(self,install_dict):
        self.debug_print("Installing app")
        """Runs script associated with applications"""
        if 'script_path' in install_dict:
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = subprocess.SW_HIDE
            result = subprocess.Popen(["cscript.exe",install_dict['script_path'].replace("/","\\"),self.input_name],stdout=subprocess.PIPE,stderr=subprocess.PIPE,stdin=subprocess.PIPE,shell=False, startupinfo=startupinfo)
            self.out1, self.out1_err = result.communicate()
            return result.returncode
        else:
            return -9000
    def manual_run_script(self):
        self.debug_print("Installing app")
        if self.manual_install_path:
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = subprocess.SW_HIDE
            result = subprocess.Popen(["cscript.exe",self.manual_install_path.replace("/","\\"),self.input_name],stdout=subprocess.PIPE,stderr=subprocess.PIPE,stdin=subprocess.PIPE,shell=False, startupinfo=startupinfo)
            self.out2, self.out2_err = result.communicate()
            self.manual_install_queue.put(result.returncode)
            return result.returncode
        else:
            self.manual_install_queue.put(-9000)
            return -9000
    def get_specific_program(self,search_terms = [],exclude_terms=[],live=False,get_version=False,fresh=False,complete_query=None):
        start_time = time.time()
        """
        Returns programs or a list of programs based on search terms and excluded terms.
        Live should be true when the WMI object is still active such as in the get_info method, False otherwise
        """
        returned_list = []
        if not self.full_programlist or fresh:
            self.debug_print("finding all programs")
            self.full_programlist = get_program_from_registry(self.input_name,r"SOFTWARE\Wow6432Node\Microsoft\Windows\CurrentVersion\Uninstall",[],[])
            self.full_programlist.extend(get_program_from_registry(self.input_name,r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall",[],[]))
            if not self.full_programlist:
                pythoncom.CoInitialize()
                if not live:
                    try:
                        self.search = self.wmi_wrapper(self.input_name,find_classes=False)
                    except: pass
                try:
                    for i in self.search.Win32_Product(['Name','Version']):
                        #if i.Name and re.search("[A-Za-z]",i.Name.replace("\xae","")) and not [p for p in self.full_programlist if p.name == i.Name.replace("\xae","")]:
                        #if not "microsoft" in i.Name.lower(): print(i.Name)
                        self.full_programlist.append(Program(name=i.Name.replace("\xae",""),version=i.Version))
                except: pass

                pythoncom.CoUninitialize()
            self.debug_print("all programs list is %s long" % len(self.full_programlist))
        if search_terms and self.full_programlist:
            for p in self.full_programlist:
                if all([s.lower().strip() in p.name.lower().strip() for s in search_terms]):
                    self.debug_print("All search terms matched for %s" % p.name.lower())
                    if exclude_terms:
                        if any([e.lower().strip() in p.name.lower().strip() for e in exclude_terms]):
                            self.debug_print("Search term matched for %s...discarding match" % p.name.lower())
                        if not any([e.lower().strip() in p.name.lower().strip() for e in exclude_terms]):
                            self.debug_print("Including %s" % p)
                            returned_list.append(p)
                    else:
                        self.debug_print(p)
                        returned_list.append(p)
            if returned_list == []:
                returned_list = None

        if returned_list:
            if get_version:
                self.programs_queue.put(returned_list[-1])
                return returned_list[-1]
            else:
                try:
                    self.programs_queue.put(returned_list[-1].name)
                    return returned_list[-1].name
                except:
                    self.programs_queue.put(returned_list[-1])
                    return returned_list[-1]
        else:
            if not returned_list is None:
                if self.programlist and search_terms:
                    if get_version:
                        self.programs_queue.put(self.programlist[-1])
                        return self.programlist[-1]
                    else:
                        try:
                            self.programs_queue.put(self.programlist[-1].name)
                            return self.programlist[-1].name
                        except:
                            self.programs_queue.put(self.programlist[-1])
                            return self.programlist[-1]

                else:
                    temp_result = []
                    for p in self.full_programlist:
                        if not any(p.name in s.name for s in temp_result):
                            temp_result.append(p)
                    self.programs_queue.put(list(set(temp_result)))

                    return list(set(temp_result))
            else:
                return
    def rec_keys(self,key):
        """Recursive method to dig into registry keys"""
        values = []
        sub_keys = []
        i=0
        while True:
            temp = None
            try:
                temp= EnumKey(key,i)
                sub_keys.append(OpenKey(key,temp))

            #inner_open_key = OpenKey(remote_key,inner_key)
            except OSError as e:
                if e.winerror == 259:
                    break
            except:
                raise
            i+=1
        i=0
        try:
            full_string = QueryValueEx(key,"DeviceDesc")[0]
            values.append(full_string.split(";")[-1])
        except:
            pass
        for k in sub_keys:
            values.extend(self.rec_keys(k))
        return values
    def __str__(self):
        try: ip_address = self.ip_addresses[0]
        except: ip_address = "-"
        return "input:%s\nname:%s\nip:%s\nserial:%s" % (self.input_name,self.name, ip_address,self.serial)
"""
Helper class to start the ComputerInfo class
"""
class WMIThread(threading.Thread):
    def run(self):
        pythoncom.CoInitialize()
        try:
            super().run()
        finally:
            pythoncom.CoUninitialize()
