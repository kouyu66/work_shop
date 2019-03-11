import socket
import json
import time
import re
import os


class Client():

    def __init__(self, ip, port_number):
        self.__ip = ip
        self.__port_number = port_number
        self.__s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__s.connect((self.__ip, self.__port_number))

    def send(self, data):
        encode_data = (json.dumps(data)).encode('utf-8')
        self.__s.send(encode_data)
        self.__s.send(('').encode('utf-8')) # 发送约定的空字符作为结束标志

    def close(self):
        self.__s.close()

class SSD():
    def __init__(self, disk_num):
        self.disk_num = disk_num
        self.__detail = {}

    def __list_to_dict(self, list_info, sep=':'):
        '''将包含冒号的长字符串转换为字典格式，输入列表，输出字典'''
        list_temp = []
        for line in list_info:
            if line.count(sep) != 1:    # 检查分隔符数量是否为1
                continue
            seprate_line = re.split(sep, line)
            seprate_line = [
                x.replace('\t', '').replace('\n', '').replace(' ', '')
                for x in seprate_line
            ]
            list_temp.append(seprate_line)
        dict_info = dict(list_temp)
        return dict_info

    def __get_pci_bus_num(self):
        get_pci_cmd = 'find /sys/* -name {0} | grep devices'.format(self.disk_num)
        hit = os.popen(get_pci_cmd).readlines()
        if hit:
            pci_line_str = hit[0]
            split_hit = re.split('/', pci_line_str)
            return split_hit[-3]

    def __get_pci_speed(self):
        pci_bus_num = self.__get_pci_bus_num()
        get_pci_speed_cmd = "lspci -vvv -s {0} | grep 'LnkSta:' | cut -d ' ' -f 2,4".format(pci_bus_num)
        lspci_info = os.popen(get_pci_speed_cmd).readlines()
        lspci_info_strip = [x.strip('\n') for x in lspci_info][0]
        pci_speed = ''.join(lspci_info_strip.split(','))
        return pci_speed

    def __get_smart(self):
        device_full_name = '/dev/' + self.disk_num
        get_smart_cmd = 'nvme smart-log {0}'.format(device_full_name)
        smart_info = os.popen(get_smart_cmd).readlines()
        info_dict = self.__list_to_dict(smart_info)
        return info_dict

    def __get_boot_info(self):
        get_boot_drive_cmd = "df -h | grep -E '/boot$'"
        boot_drive_info = os.popen(get_boot_drive_cmd).readlines()[0]
        if self.disk_num in boot_drive_info:
            boot = 'Master'
        else:
            boot = 'Slave'
        return boot

    def load(self):
        self.__detail['disk_num'] = self.disk_num
        self.__detail['boot'] = self.__get_boot_info()
        self.__detail['pci_speed'] = self.__get_pci_speed()
        smart_dict = self.__get_smart()
        self.__detail.update(smart_dict)
        return

    def dump(self):
        return self.__detail

class DictCompare():
    '''模拟一个比较器，用来比较字典的内容'''
    def __init__(self):

        self.increase = []
        self.decrease = []
        self.diff = []
        
    def compare(self, new_item, old_item):
        if not type(old_item) == type(new_item):
            raise ValueError('type error. different type cannot be compared.')
        for key in new_item:
            if key not in old_item:
                self.increase.append(key)
            else:
                if new_item[key] == old_item[key]:
                    continue
                else:
                    self.diff.append(key)
        for key in old_item:
            if key not in new_item:
                self.decrease.append(key)
        return self.increase, self.decrease, self.diff  

# === Danger Zone ===

# test_client = Client('109.101.80.172', 1025)
# nvme_sample = SSD('nvme0')
# nvme_sample.load()
# print(nvme_sample.dump())