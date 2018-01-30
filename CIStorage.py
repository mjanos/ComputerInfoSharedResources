import threading

"""Storage class for Users with shares mapped"""
class MappedUser(object):
    def __init__(self,name=None,sessionid=None):
        self.name = name
        self.sessionid = sessionid
        self.disks=[]

    def add_disk(self,disk=None):
        if isinstance(disk,'Disk'):
            if not any(d for d in self.disks if d.systemname==disk.systemname and d.name == disk.name and d.path == disk.path and d.sessionid == disk.sessionid):
                print("No duplicates")
                self.disks.append(disk)
            else:
                print("duplicate detected")
        else:
            print("Instance not Disk but %s" % (type(disk)))

    def get_name(self):
        for i in self.disks:
            if i.name == "Z:":
                self.name = i.path.rsplit('\\',1)[1]
                print(self.name)

"""Storage class for a user and their AD attributes"""
class NetworkUser(object):
    def __init__(self,name=None):
        self.name = name
        self.full_name = None
        self.home_directory = None
        self.last_log = None
        self.logon_server = None

"""Storage class for mapped drives"""
class Disk(object):
    def __init__(self,systemname=None,name=None,path=None,sessionid=None):
        self.systemname = systemname
        self.name = name
        self.path = path
        self.sessionid = sessionid

"""Storage class for printers"""
class Printer(object):
    def __init__(self,printer=None,port=None):
        self.printer = printer
        self.port = port

"""Storage class for installed programs"""
class Program(object):
    def __init__(self,name=None,version=None,date=None):
        self.name=name
        self.version = version
        self.date = date

    def __str__(self):
        return "%s %s" % (self.name,self.version)

"""
Bool that can be locked
(Might not be necessary)

"""
class ThreadSafeBool(object):
    def __init__(self):
        self.lock = threading.Lock()
        self.value = False
    def setTrue(self):
        with self.lock:
            self.value = True
    def setFalse(self):
        with self.lock:
            self.value = False
    def get(self):
        with self.lock:
            return self.value

"""Counter that can lock to prevent race condition"""
class ThreadSafeCounter(object):
    def __init__(self,counter=None):
        self.lock = threading.Lock()
        if counter:
            self.counter = counter
        else:
            self.counter=0

    def increment(self):
        with self.lock:
            self.counter+=1


    def decrement(self):
        with self.lock:
            self.counter-=1
            if self.counter < 0:
                self.counter = 0

    def get(self):
        with self.lock:
            return self.counter

    def set(self,val):
        with self.lock:
            self.counter = val
