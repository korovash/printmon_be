import psycopg2
from datetime import datetime
import re

class DB_connection:
    try:
        connection = psycopg2.connect(user="django",
                                  password="",
                                  host="",
                                  port="5432",
                                  database="print_db")
        cursor = connection.cursor()

    except (Exception, psycopg2.Error) as error :
        if(connection):
            print("Failed to connect DB", error)
    finally:
        if(connection):
            cursor.close
            connection.close
    
    def insert_cart_stats(self, device):
        pg_insert_black = """INSERT INTO main_devicedetail(
                            device_id, black_cart_name, black_tonerlevel, 
                            printed_count, update_date, hostname) 
                            VALUES(%s, %s, %s, %s, %s, %s)"""
        
        pg_insert_color = """INSERT INTO main_devicedetail(
                            device_id, black_cart_name, black_tonerlevel, 
                            cyan_cart_name, cyan_tonerlevel, mag_cart_name, 
                            mag_tonerlevel, yel_cart_name, yel_tonerlevel, 
                            printed_count, update_date, hostname) 
                            VALUES(%s, %s, %s, %s, %s, %s, 
                                    %s, %s, %s, %s, %s, %s)"""

        if re.match(r'^\S+\.[dD][vV][fF][uU]\.[rR][uU]$', device.hostname):
            rebuilded_hostname = re.sub(r'\.[dD][vV][fF][uU]\.[rR][uU]$', '', device.hostname).upper()
        else:
            rebuilded_hostname = device.hostname.upper()

        if device.status == 'Online':
            try:    
                if device.c_cartname != '' and device.c_cartlvl and device.m_cartname != '' and device.m_cartlvl and device.y_cartname != '' and device.y_cartlvl and device.c_cartname != device.m_cartname and device.c_cartname != device.y_cartname:
                    self.cursor.execute(pg_insert_color, (device.devid, device.b_cartname, device.b_cartlvl, 
                                                        device.c_cartname, device.c_cartlvl, device.m_cartname, 
                                                        device.m_cartlvl, device.y_cartname, device.y_cartlvl, 
                                                        device.print_cnt, datetime.now(), rebuilded_hostname))
                    self.connection.commit()
                else:
                    self.cursor.execute(pg_insert_black, (device.devid, device.b_cartname, device.b_cartlvl, 
                                        device.print_cnt, datetime.now(), rebuilded_hostname))
                    self.connection.commit()
            except Exception as error:
                print(('Ошибка добавления деталей устройства {}: {}').format(rebuilded_hostname, error))

    def update_main_stats(self, device):
        pg_update = """UPDATE main_device SET hostname = %s, name = %s, ipaddr = %s, serial_num = %s, 
                    status = %s, update_date = %s  WHERE hostname = %s"""
        pg_update_status = """UPDATE main_device SET hostname = %s, status = %s WHERE hostname = %s"""
        
        if re.match(r'^\S+\.[dD][vV][fF][uU]\.[rR][uU]$', device.hostname):
            rebuilded_hostname = re.sub(r'\.[dD][vV][fF][uU]\.[rR][uU]$', '', device.hostname).upper()
        else:
            rebuilded_hostname = device.hostname.upper()
        if re.match(r"(^Xerox\s\S+\s\S+)\;.*$|(^Xerox\s\S+\s\S+)\s.*$", device.name):
            if re.findall(r"(^Xerox\s\S+\s\S+)\;.*$|(^Xerox\s\S+\s\S+)\s.*$", device.name)[0][0]:
                device.name = re.findall(r"(^Xerox\s\S+\s\S+)\;.*$|(^Xerox\s\S+\s\S+)\s.*$", device.name)[0][0]
            elif re.findall(r"(^Xerox\s\S+\s\S+)\;.*$|(^Xerox\s\S+\s\S+)\s.*$", device.name)[0][1]:
                device.name = re.findall(r"(^Xerox\s\S+\s\S+)\;.*$|(^Xerox\s\S+\s\S+)\s.*$", device.name)[0][1]
        try:
            if device.status == 'Online':
                self.cursor.execute(pg_update, (rebuilded_hostname, device.name[:200], device.ip, device.sn, device.status, 
                                    datetime.now(), device.hostname))
                self.connection.commit()
            else:
                self.cursor.execute(pg_update_status, (rebuilded_hostname, device.status, device.hostname))
                self.connection.commit()
        except Exception as error:
            print(('Ошибка обновления устройства {}: {}').format(rebuilded_hostname, error))
  
    def select_hostnames(self):
        pg_select = """SELECT hostname, id FROM main_device"""
        self.cursor.execute(pg_select)
        records = self.cursor.fetchall()
        return records
