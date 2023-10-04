from print_mon_be.db_conn import DB_connection
from print_mon_be.ping import ping
from print_mon_be.async_resolve import resolve_host
from print_mon_be.async_ping2 import ping_host
import re

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
    b_cart_curprint = 0
    c_cart_curprint = 0
    m_cart_curprint = 0
    y_cart_curprint = 0
    b_cart_maxprint = 0
    c_cart_maxprint = 0
    m_cart_maxprint = 0
    y_cart_maxprint = 0
    print_cnt = 0

    def update_main_stats(self):
        db_conn = DB_connection()
        db_conn.update_main_stats(self)
        
    def insert_cart_stats(self):
        db_conn = DB_connection()
        db_conn.insert_cart_stats(self)

def get_ip_address(host):
    if not(re.match(r'\d+\.\d+\.\d+\.\d+', host)):
        ip = resolve_host(host)
    else:
        ip = host
    return ip

def check_status(host):
    if ping_host(host) == True:
        status = 'Online'
    else:
        print("Host {} is unreachable".format(host))
        status = 'Offline'
    return status

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
    print("=== Starting to check hosts status ===")
    dev_list = list()
    host_ip_list = list()
    host_ip_status_list = list()
    resolve_fail_cnt = 0
    ping_fail_cnt = 0

    for host in host_list:
        resolved_ip = get_ip_address(host[0])
        if resolved_ip:
            host_ip_list.append([host[0], host[1], resolved_ip])
        else:
            host_ip_list.append([host[0], host[1], ""])
            resolve_fail_cnt += 1
    print("Failed to resolve {} hosts".format(resolve_fail_cnt))

    for host in host_ip_list:
        if host[2]:
            status = check_status(host[2])
        else:
            status = 'Offline'
        if status == 'Online':
            host_ip_status_list.append([host[0], host[1], host[2], status])
        elif status == 'Offline':
            host_ip_status_list.append([host[0], host[1], host[2], status])
            ping_fail_cnt += 1
    print("Failed to ping {} hosts".format(ping_fail_cnt))
        
    for host in host_ip_status_list:
        device = Device()
        device.hostname = host[0]
        device.devid = host[1]
        device.ip = host[2]
        device.status = host[3]
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