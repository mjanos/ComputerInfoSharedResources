try:
    import nmap
except: print("Nmap not available")
import time

"""Class that retrieves printer information by ip address"""
class PrinterInfo(object):
    def __init__(self,**kwargs):
        self.nm = nmap.PortScanner()
        self.ip_address = kwargs.pop('ip_address',None)
        self.vendor = ""
        self.os_name = ""

    def get_info(self):
        self.output = self.nm.scan(hosts=self.ip_address.strip(),ports='22-443',arguments='-O -T5')
        vendor_name = self.output['scan'][self.ip_address.strip()]['vendor']
        self.vendor = next(v for k,v in vendor_name.items())

        self.os_name = self.output['scan'][self.ip_address.strip()]['osmatch'][0]['name']
