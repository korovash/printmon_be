from pysnmp.hlapi import *
from datetime import datetime
from print_mon_be.db_conn import DB_connection
from print_mon_be.ping import ping
import codecs
import re
from time import time


def snmp_getcmd(community, ip, port, OID):
    return (nextCmd(SnmpEngine(),
                    CommunityData(community, mpModel=0),
                    UdpTransportTarget((ip, port)),
                    ContextData(),
                    ObjectType(ObjectIdentity(OID))))

""" Функция snmpgetnext (получение данных по SNMP) """
def snmp_get_next(host, oid):
    community = "public"
    port = "161"
    errorIndication, errorStatus, errorIndex, varBinds = next(snmp_getcmd(community, host, port, oid))
    for name, val in varBinds:
        if (type(val) == OctetString):
            val = val.asOctets().decode('utf8', errors="replace").replace("\x00", "\uFFFD")
        else:
            val = val.prettyPrint()
        return (val)

class Device_oid:
    devid = 0
    name = "1.3.6.1.2.1.25.3.2.1.3"
    ip = "1.3.6.1.2.1.4.20.1.1.1"
    sn = "1.3.6.1.2.1.43.5.1.1.17"
    
    b_cartname = "1.3.6.1.2.1.43.11.1.1.6."
    b_cart_maxprint = "1.3.6.1.2.1.43.11.1.1.8"
    b_cart_curprint = "1.3.6.1.2.1.43.11.1.1.9"
    c_cartname = "1.3.6.1.2.1.43.11.1.1.6.1.1"
    c_cart_maxprint = "1.3.6.1.2.1.43.11.1.1.8.1.1"
    c_cart_curprint = "1.3.6.1.2.1.43.11.1.1.9.1.1"
    m_cartname = "1.3.6.1.2.1.43.11.1.1.6.1.2"
    m_cart_maxprint = "1.3.6.1.2.1.43.11.1.1.8.1.2"
    m_cart_curprint = "1.3.6.1.2.1.43.11.1.1.9.1.2"
    y_cartname = "1.3.6.1.2.1.43.11.1.1.6.1.3"
    y_cart_maxprint = "1.3.6.1.2.1.43.11.1.1.8.1.3"
    y_cart_curprint = "1.3.6.1.2.1.43.11.1.1.9.1.3"
    ricoh_c_cartname = "1.3.6.1.2.1.43.11.1.1.6.1.2"
    ricoh_c_cart_maxprint = "1.3.6.1.2.1.43.11.1.1.8.1.2"
    ricoh_c_cart_curprint = "1.3.6.1.2.1.43.11.1.1.9.1.2"
    ricoh_m_cartname = "1.3.6.1.2.1.43.11.1.1.6.1.3"
    ricoh_m_cart_maxprint = "1.3.6.1.2.1.43.11.1.1.8.1.3"
    ricoh_m_cart_curprint = "1.3.6.1.2.1.43.11.1.1.9.1.3"
    ricoh_y_cartname = "1.3.6.1.2.1.43.11.1.1.6.1.4"
    ricoh_y_cart_maxprint = "1.3.6.1.2.1.43.11.1.1.8.1.4"
    ricoh_y_cart_curprint = "1.3.6.1.2.1.43.11.1.1.9.1.4"
    print_cnt = "1.3.6.1.2.1.43.10.2.1.4.1" 


class Device:
    
    name = ''
    ip = ''
    sn = ''
    b_cartname = ''
    c_cartname = ''
    m_cartname = ''
    y_cartname = ''
    b_cartlvl = 0
    c_cartlvl = 0
    m_cartlvl = 0
    y_cartlvl = 0
    print_cnt = 0

    def check_status(self, host):
        if ping(host, 1, 1):
            self.hostname = host
            self.status = 'Online'
        else:
            print("Host {} is unreachable".format(host))
            self.hostname = host
            self.status = 'Offline'                
    
    def collect_main_stats(self):
        if self.status == 'Online':
            try:
                oid = Device_oid()
                self.name = str(snmp_get_next(self.hostname, oid.name))
                self.ip = str(snmp_get_next(self.hostname, oid.ip)) 
                self.sn = str(snmp_get_next(self.hostname, oid.sn)) 
                self.main_stats_collect_date = datetime.now()
            except Exception as error:
                print("Unable to get data of {}: {}".format(self.hostname, error))
                self.status = 'Offline'

    def snmpgetnext_cartname(self, oid_cartname):
        cartname = str(snmp_get_next(self.hostname, oid_cartname)) 
        return cartname
    
    def snmpgetnext_cartlvl(self, oid_curprint, oid_maxprint):
        curprint = int(snmp_get_next(self.hostname, oid_curprint))
        maxprint = int(snmp_get_next(self.hostname, oid_maxprint))

        if curprint > 0:
            cartlvl = curprint/maxprint*100
        else:
            cartlvl = 0
        return cartlvl

    def collect_cartrigde_stats(self):
        if self.status == 'Online':
            try:
                oid = Device_oid()
                self.b_cartname = self.snmpgetnext_cartname(oid.b_cartname)
                self.b_cartlvl = self.snmpgetnext_cartlvl(oid.b_cart_curprint, oid.b_cart_maxprint)
                if re.match(r'^RICOH',self.name):
                    self.c_cartname = self.snmpgetnext_cartname(oid.ricoh_c_cartname)
                    self.c_cartlvl = self.snmpgetnext_cartlvl(oid.ricoh_c_cart_curprint, oid.ricoh_c_cart_maxprint)
                    self.m_cartname = self.snmpgetnext_cartname(oid.ricoh_m_cartname)
                    self.m_cartlvl = self.snmpgetnext_cartlvl(oid.ricoh_m_cart_curprint, oid.ricoh_m_cart_maxprint)
                    self.y_cartname = self.snmpgetnext_cartname(oid.ricoh_y_cartname)
                    self.y_cartlvl = self.snmpgetnext_cartlvl(oid.ricoh_y_cart_curprint, oid.ricoh_y_cart_maxprint)
                else:
                    self.c_cartname = self.snmpgetnext_cartname(oid.c_cartname)
                    self.c_cartlvl = self.snmpgetnext_cartlvl(oid.c_cart_curprint, oid.c_cart_maxprint)
                    self.m_cartname = self.snmpgetnext_cartname(oid.m_cartname)
                    self.m_cartlvl = self.snmpgetnext_cartlvl(oid.m_cart_curprint, oid.m_cart_maxprint)
                    self.y_cartname = self.snmpgetnext_cartname(oid.y_cartname)
                    self.y_cartlvl = self.snmpgetnext_cartlvl(oid.y_cart_curprint, oid.y_cart_maxprint)

                self.print_cnt = str(snmp_get_next(self.hostname, oid.print_cnt))
                self.cart_stats_collect_date = datetime.now()
            except Exception as error:
                print("Unable to get data of {}: {}".format(self.hostname,error))

    def update_main_stats(self):
        db_conn = DB_connection()
        db_conn.update_main_stats(self)
        
    def insert_cart_stats(self):
        db_conn = DB_connection()
        db_conn.insert_cart_stats(self)

def update_device_main_stats(dev_list):
    print("*** Updating main stats of devices in DB ***")
    for dev in dev_list:
        dev.update_main_stats()
    print("*** Update of main stats of devices in DB has completed***")

def insert_device_cart_stats(dev_list):
    print("*** Inserting cartrige data in DB ***")
    for dev in dev_list:
        dev.insert_cart_stats()
    print("*** Insert cartrige data has completed in DB ***")

def check_dev_status(host_list):
    dev_list = []
    print("=== Starting to check hosts status ===")
    for host in host_list:
        device = Device()
        device.check_status(host[0])
        device.devid = host[1]
        dev_list.append(device)
    print("=== Hosts status checking has completed ===")
    return dev_list

def collect_dev_main_stats(dev_list):
    print("=== Starting to gather device main stats ===")
    for device in dev_list:
        device.collect_main_stats()
    print("=== Device gathering main stats has completed ===")

def collect_dev_cart_stats(dev_list):
    print("=== Starting to gather cartridge data ===")
    for device in dev_list:
        device.collect_cartrigde_stats()
    print("=== Cartridge data gathering has completed ===")

"""def main():
    starttime = time()
    db_select_q = DB_connection()
    host_list = db_select_q.select_hostnames()
    dev_list = check_dev_status(host_list)
    collect_dev_main_stats(dev_list)
    update_device_main_stats(dev_list)
    collect_dev_cart_stats(dev_list)
    insert_device_cart_stats(dev_list)
    print("Run time: {:.2F}".format(time() - starttime))"""