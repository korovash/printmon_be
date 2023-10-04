import asyncio
import aiosnmp
import re
from time import time, sleep
from print_mon_be.device import Device, check_dev_status, update_device_main_stats, insert_device_cart_stats
from print_mon_be.db_conn import DB_connection
import json

with open("print_mon_be/oid.json", "r") as read_file:
    oid = json.load(read_file)

def decode_value(value):
    if type(value) == bytes:
        value = value.decode('UTF8', errors="replace").replace("\x00", "\uFFFD")
    elif type(value) == int:
        value = ''
    else:
        value = str(value)
    return value

def count_cart_lvl(cur_value, max_value):
    if cur_value > 0 and max_value > 0:
        lvl_value = round(cur_value / max_value * 100, 0)
    else:
        lvl_value = 0
    return lvl_value


async def collect_main_stats(device, oid):
    with aiosnmp.Snmp(
        host=device.hostname,
        port=161,
        community="public",
        timeout=10,
        retries=1,
        max_repetitions=1,
        version=0
    ) as snmp:
        if device.status == 'Online':
            try:
                device.name = decode_value((await snmp.get_next(oid['name']))[0].value)
                device.sn = decode_value((await snmp.get_next(oid['sn']))[0].value)
                device.print_cnt = (await snmp.get_next(oid['print_cnt']))[0].value
                if re.match(r'^RICOH', device.name):
                    device.b_cartname = (await snmp.get_next(oid['b_cartname']))[0].value
                    device.b_cart_curprint = (await snmp.get_next(oid['b_cart_curprint']))[0].value
                    device.b_cart_maxprint = (await snmp.get_next(oid['b_cart_maxprint']))[0].value

                    device.c_cartname = (await snmp.get_next(oid['ricoh_c_cartname']))[0].value
                    device.c_cart_curprint = (await snmp.get_next(oid['ricoh_c_cart_curprint']))[0].value
                    device.c_cart_maxprint = (await snmp.get_next(oid['ricoh_c_cart_maxprint']))[0].value

                    device.m_cartname = (await snmp.get_next(oid['ricoh_m_cartname']))[0].value
                    device.m_cart_curprint = (await snmp.get_next(oid['ricoh_m_cart_curprint']))[0].value
                    device.m_cart_maxprint = (await snmp.get_next(oid['ricoh_m_cart_maxprint']))[0].value
                    
                    device.y_cartname = (await snmp.get_next(oid['ricoh_y_cartname']))[0].value
                    device.y_cart_curprint = (await snmp.get_next(oid['ricoh_y_cart_curprint']))[0].value
                    device.y_cart_maxprint = (await snmp.get_next(oid['ricoh_y_cart_maxprint']))[0].value
                else:
                    device.b_cartname = (await snmp.get_next(oid['b_cartname']))[0].value
                    device.b_cart_curprint = (await snmp.get_next(oid['b_cart_curprint']))[0].value
                    device.b_cart_maxprint = (await snmp.get_next(oid['b_cart_maxprint']))[0].value

                    device.c_cartname = (await snmp.get_next(oid['c_cartname']))[0].value
                    device.c_cart_curprint = (await snmp.get_next(oid['c_cart_curprint']))[0].value
                    device.c_cart_maxprint = (await snmp.get_next(oid['c_cart_maxprint']))[0].value

                    device.m_cartname = (await snmp.get_next(oid['m_cartname']))[0].value
                    device.m_cart_curprint = (await snmp.get_next(oid['m_cart_curprint']))[0].value
                    device.m_cart_maxprint = (await snmp.get_next(oid['m_cart_maxprint']))[0].value

                    device.y_cartname = (await snmp.get_next(oid['y_cartname']))[0].value
                    device.y_cart_curprint = (await snmp.get_next(oid['y_cart_curprint']))[0].value
                    device.y_cart_maxprint = (await snmp.get_next(oid['y_cart_maxprint']))[0].value
            except Exception as error:
                print(error)

def rebuild_cart_stats(dev_list):
    for device in dev_list:
        device.b_cartname = decode_value(device.b_cartname)
        device.c_cartname = decode_value(device.c_cartname)
        device.m_cartname = decode_value(device.m_cartname)
        device.y_cartname = decode_value(device.y_cartname)
        device.b_cartlvl = count_cart_lvl(device.b_cart_curprint, device.b_cart_maxprint)
        device.c_cartlvl = count_cart_lvl(device.c_cart_curprint, device.c_cart_maxprint)
        device.m_cartlvl = count_cart_lvl(device.m_cart_curprint, device.m_cart_maxprint)
        device.y_cartlvl = count_cart_lvl(device.y_cart_curprint, device.y_cart_maxprint)

async def collect_stats_task(dev_list):
    for dev in dev_list:
        task = collect_main_stats(dev, oid)
        await asyncio.gather(task)

def main():
    starttime = time()
    db_select_q = DB_connection()
    host_list = db_select_q.select_hostnames()
    dev_list = check_dev_status(host_list)
    asyncio.run(collect_stats_task(dev_list))
    rebuild_cart_stats(dev_list)
    update_device_main_stats(dev_list)
    insert_device_cart_stats(dev_list)
    print("Run time: {:.2F}".format(time() - starttime))
