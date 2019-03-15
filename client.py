import socket
import struct
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
        body = json.dumps(data)
        header = [body.__len__()]
        headerPack = struct.pack("!I", *header)
        encode_data = headerPack + body.encode('utf-8')
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
        get_smart_cmd = 'nvme smart-log {0}|grep -E "criti|temp|power|unsafe|media|num"'.format(self.__char_device)
        smart_info = os.popen(get_smart_cmd).readlines()
        info_dict = self.__list_to_dict(smart_info)
        return info_dict

    def __get_boot_info(self):
        get_boot_drive_cmd = "df -h | grep -E '/boot$'"
        boot_drive_info = os.popen(get_boot_drive_cmd).readlines()[0]
        key_char = self.__char_device + 'n1'    # 精确匹配，避免nvme1匹配到nvme11.
        if key_char in boot_drive_info:
            boot = "Master"
        else:
            boot = "Slave"
        return boot

    def __get_sn_info(self):
        get_sn_cmd = "nvme id-ctrl {0} | grep -E '^vid|sn|\<mn\>|\<fr\>'".format(self.__char_device)
        sn_info = os.popen(get_sn_cmd).readlines()
        info_dict = self.__list_to_dict(sn_info)
        return info_dict

    def load(self):
        self.__detail["disk_num"] = self.disk_num
        self.__detail["boot"] = self.__get_boot_info()
        self.__detail["pci_num"] = self.__get_pci_bus_num()
        self.__detail["pci_speed"] = self.__get_pci_speed()
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

def compare():
    pass

def get_current_ssd_info():
    ssd_info = {}
    char_info = get_char_info()
    for char_device in char_info:   # 获取当前ssd信息列表
        ssd_instanse = SSD(char_device)
        ssd_instanse.load()
        single_detail = ssd_instanse.dump()
        pci_number = single_detail.pop('pci_num')
        ssd_info.update({pci_number : single_detail})
    return ssd_info

def get_current_server_info():
    pass
    return {}

def get_current_script_info():
    pass
    return {}
def get_last_info(file_name):
    if os.path.exists(file_name):
        with open(file_name, 'r') as last_trace:
            last_info = json.load(last_trace)
    else:
        last_info = {}
    return last_info

def get_host_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    finally:
        s.close()
 
    return ip

def pack(identifier, info_type, info_level):
    
    info_tobe_send = {"id":identifier, "type":info_type, "level":info_level}
    if info_level is 2:
        pass
    else:
        info_tobe_send.update({"ssd_info" : current_ssd_info})
        info_tobe_send.update({"script_info" : current_script_info})
        info_tobe_send.update({"server_info" : current_server_info})
        with open('dump.json', 'w') as dump_file:
            json.dump(info_tobe_send, dump_file)
    return info_tobe_send

# ========== Western Wall ========== #

differ = DictCompare()
info_type = "monitor"

while True:
    last_info = get_last_info('dump.json')
    current_ssd_info = get_current_ssd_info()
    current_script_info = get_current_script_info()
    current_server_info = get_current_server_info()

    if last_info:
        identifier = last_info['id']
        last_ssd_info = last_info['ssd_info']
        last_script_info = last_info['script_info']
        last_machine_info = last_info['server_info']

        # 需要判断发送什么数据出去，该功能将在下个版本修复。暂时对主程序不构成影响。
        if last_info != current_ssd_info:
            info_level = 1
        else:
            info_level = 2
    else:
        identifier = str(time.time())+ get_host_ip()
        info_level = 0

    deliver = Client('109.101.80.172', 1025)
    info_tobe_send = pack(identifier, info_type, info_level)
    deliver.send(info_tobe_send)
