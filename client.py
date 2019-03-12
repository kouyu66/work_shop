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
    def __init__(self, char_device):
        self.__char_device = char_device
        self.disk_num = re.split('/', self.__char_device)[-1]
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
        get_smart_cmd = 'nvme smart-log {0}'.format(self.__char_device)
        smart_info = os.popen(get_smart_cmd).readlines()
        info_dict = self.__list_to_dict(smart_info)
        return info_dict

    def __get_boot_info(self):
        get_boot_drive_cmd = "df -h | grep -E '/boot$'"
        boot_drive_info = os.popen(get_boot_drive_cmd).readlines()[0]
        key_char = self.__char_device + 'n1'    # 精确匹配，避免nvme1匹配到nvme11.
        if key_char in boot_drive_info:
            boot = 'Master'
        else:
            boot = 'Slave'
        return boot

    def __get_sn_info(self):
        get_sn_cmd = "nvme id-ctrl {0} | grep -E '^vid|sn|\<mn\>|\<fr\>'".format(self.__char_device)
        sn_info = os.popen(get_sn_cmd).readlines()
        info_dict = self.__list_to_dict(sn_info)
        return info_dict

    def load(self):
        self.__detail['disk_num'] = self.disk_num
        self.__detail['boot'] = self.__get_boot_info()
        self.__detail['pci_speed'] = self.__get_pci_speed()
        smart_dict = self.__get_smart()
        sn_info_dict = self.__get_sn_info()
        self.__detail.update(smart_dict)
        self.__detail.update(sn_info_dict)
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

class Commander():
    '''命令交互框架，内部处理系统打印的返回信息。'''
    def __init__(self):
        pass
    def input(self):
        '''输入系统命令'''
        pass
    def output(self):
        '''输出系统输出'''
        pass

def get_char_info():
    '''获取dera nvme ssd字符设备信息'''
    get_nvme_node_command = "ls /dev/nvme* | grep nvme.$"
    node_info_raw = os.popen(get_nvme_node_command).readlines()
    char_info = [
        x.replace('\n', '').replace(' ', '').replace('\t', '')
        for x in node_info_raw if node_info_raw
    ]
    return char_info
# ========== Western Wall ========== #
char_info = get_char_info()
ssd_instanse_list = []
for char_device in char_info:
    ssd_instanse = SSD(char_device)
    ssd_instanse_list.append(ssd_instanse)

for ssd_instanse in ssd_instanse_list:
    ssd_instanse.load()
    print(ssd_instanse.dump())



# test_client = Client('109.101.80.172', 1025)
# nvme_sample = SSD('nvme0')
# nvme_sample.load()
# print(nvme_sample.dump())
