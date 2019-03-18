import socket
import struct
import threading
import time
import json
import os


class Log():
    '''log类'''
    def __init__(self, log_name):
        if type(log_name) != str:
            raise TypeError('Wrong log_name type, it should be str.')
        self.log_name = log_name + '.log'

    def write(self, strings):
        if type(strings) != str:
            raise TypeError('Wrong log string type, it should be str.')
        with open(self.log_name, 'a') as file:
            c_readable_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            file.write(c_readable_time + '  ' + strings)

    def trash(self):
        with open(self.log_name, 'w') as file:
            trash_warning = 'log deleted by host.'
            file.write(trash_warning)

class Inbox():
    '''模拟一个支持多线程的socket服务端'''

    def __init__(self, port_number):
        '''设置socket基础信息'''
        self.__record = []
        self.__led = False
        self.__s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__s.bind(('', port_number))
        self.__s.listen(5)
        self.__s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    def on(self):
        '''将serverDameon函数设置为守护线程，放置在后台运行'''
        def serverDaemon(self):
            '''无限循环接受远程联入信息，转交dataRecv函数处理，并为每一次联入单开一个线程，支持多线程'''
            def dataRecv(self, sock, addr, lock):
                '''获取锁以后，每1024个字节收一次数据包，解析并添加到类属性列表中，同时设置led状态为True，通讯完毕后端口关闭，释放锁'''
                lock.acquire()  # 获取进程锁
                dataBuffer = bytes()    # 初始化网络数据缓存区
                headerSize = 4  # 规定头信息所占用的字节数
                while True:    
                    data = sock.recv(1024)
                    if data:
                        dataBuffer += data
                        if len(dataBuffer) < headerSize:    # 模拟header信息接收不全的状态，
                            continue
                        headpack = struct.unpack('!I',dataBuffer[:headerSize])  # header仅包含数据包大小的描述信息
                        bodySize = headpack[0]
                        if len(dataBuffer) < headerSize + bodySize: # 模拟单次发送信息不全的情况
                            continue
                        body = dataBuffer[headerSize:headerSize+bodySize]
                        decode_data = json.loads(body.decode('utf-8'))
                        self.__record.append(decode_data)
                        self.__led = True
                        dataBuffer = bytes()    # 考虑到客户端脚本规定，发送完全部信息后关闭端口，dataBuffer无需处理粘包的情况
                        break
                    else:
                        break
                lock.release()
                sock.close()
                return
            lock = threading.Lock()
            while True:
                sock, addr = self.__s.accept()
                t1 = threading.Thread(target=dataRecv, args=(self, sock, addr, lock))
                t1.start()
            return
        t1 = threading.Thread(target=serverDaemon, args=(self,), daemon=True)
        t1.start()    

    def led(self):
        '''判断led灯当前状态'''
        return self.__led

    def vomit(self):
        '''返回属性类堆栈中的第一条信息'''
        if not self.__record:
            return None
        else:
            if len(self.__record) is 1:
                self.__led = False
            return self.__record.pop(0)

class DictCompare():
    '''模拟一个比较器，用来比较字典的内容'''
    def __init__(self):

        self.increase = []
        self.decrease = []
        self.diff = []
        
    def compare(self, new_item, old_item):
        self.increase = []  # bug fix: log打印重复信息
        self.decrease = []  # bug fix: log打印重复信息
        self.diff = []      # bug fix: log打印重复信息

        if not type(old_item) == type(new_item):
            raise ValueError('type error. different type cannot be compared.')
        if new_item and old_item:
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
        elif new_item:
            self.increase = list(old_item.keys())
        elif old_item:
            self.decrease = list(new_item.keys())

        return self.increase, self.decrease, self.diff    


def load_main_dict(main_dict_file):
    '''尝试从本地json文件恢复main_dict,以防止主控以外关闭导致的数据丢失'''

    if os.path.exists(main_dict_file):
        with open(main_dict_file, 'r') as main_dict_obj:
            main_dict = json.load(main_dict_obj)
    else:
        main_dict = dict()
    return main_dict

def process(message):
    if isinstance(message, dict) and "type" in message:
        message_type = message.pop("type")
    else:
        raise ValueError("message type error, it should be dict and contain 'type' key")
    
    if message_type == "monitor":
        monitor_processor(message)
    elif message_type == "powercycle":
        powercycle_processor(message)
    
def powercycle_processor(message):
    print('under construction.')
    pass

def monitor_processor(message):
    '''主字典刷新及log记录操作'''
    identifier = message.pop("id") # id should be timestamp + ip string,
    info_level = message.pop("level") # 0 init 1 update 2 heart_beat
    if info_level is 0:
        sub_init_process(identifier, message)
    elif info_level is 1:
        server_info = message.get("server_info")
        script_info = message.get("script_info")
        ssd_info = message.get("ssd_info")
        if server_info:
            sub_single_dict_process("server_info",server_info,identifier)
        if script_info:
            sub_single_dict_process("script_info",script_info,identifier)
        if ssd_info:
            sub_ssd_process(ssd_info, identifier)
    elif info_level is 2:
        info = '[{0}] ^^^ Alive Detected ^^^'.format(identifier)
        main_log.write(info)
    main_dict.update({identifier : message})
    return

def sub_init_process(identifier, message):
    # server_info = message.get("server_info")
    ssd_info = message.get("ssd_info")
    info = '====== New Clietn Join ======\n'


    for key, value in ssd_info.items():
        info = info + '{0} : {1}\n'.format(key, value)
    main_log.write(info)
    warning_log.write(info)

def sub_single_dict_process(single_dict_name, single_dict_info, identifier):
    old_record = main_dict.get(identifier)
    if old_record:
        old_dict_info = old_record.get(single_dict_name)
        increase_key, decrease_key, diff_key = dict_comp.compare(single_dict_info, old_dict_info)
        if increase_key:
            for key in increase_key:
                info = '[{0}] +++ Add Detected +++ [add {1} : {2}]\n'.format(identifier, key, single_dict_info[key])
                main_log.write(info)
                warning_log.write(info)
        if decrease_key:
            for key in decrease_key:
                info = '[{0}] xxx Remove Detected xxx [remove {1} : {2}]\n'.format(identifier, key, single_dict_info[key])
                main_log.write(info)
                warning_log.write(info)
                error_log.write(info)
        if diff_key:
            for key in diff_key:
                info = '[{0}] ??? Change Detected ??? [change {1} : {2} ===> {3}\n]'.format(identifier,key,old_dict_info[key],single_dict_info[key])
    else:
        print('{0} info not found, init client to resend the message.'.format(identifier))

    return

def sub_ssd_process(new_ssd_sum, identifier):
    old_ssd_sum = main_dict[identifier]["ssd_info"]
    insert_ssd, eject_ssd, diff_ssd = dict_comp.compare(new_ssd_sum, old_ssd_sum)
    if insert_ssd:
        for bus_num in insert_ssd:
            info = '{0} +++ SSD Insert Detected +++\n'.format(identifier)
            ssd_detail = new_ssd_sum[bus_num]
            for key, value in ssd_detail.items():
                info += '[{0} : {1}]\n'.format(key, value)
            print(info)
            main_log.write(info)
    if eject_ssd:
        for bus_num in eject_ssd:
            info = '{0} xxx SSD Eject Detected xxx\n'.format(identifier)
            ssd_detail = old_ssd_sum[bus_num]
            for key, value in ssd_detail.items():
                info += '[{0} : {1}]\n'.format(key, value)
            print(info)
            main_log.write(info)
    if diff_ssd:
        head = '{0} --- SSD Info Change Notice ---\n'.format(identifier)
        bodybox = []
        for bus_num in diff_ssd:
            new_ssd_detail = new_ssd_sum[bus_num]
            old_ssd_detail = old_ssd_sum[bus_num]
            disk_num = new_ssd_detail['disk_num']
            boot = new_ssd_detail['boot']
            pci_num = new_ssd_detail['pci_num']
            sn_num = new_ssd_detail['sn']
            body = '[{0}][{1}][{2}]-{3}-'.format(pci_num,sn_num,disk_num,boot)
            for item in new_ssd_detail:
                if new_ssd_detail[item] != old_ssd_detail[item]:
                    if item == 'temperature':
                        if int(new_ssd_detail[item]) < 60: 
                            continue
                    info = '  [{0} : {1} ===> {2}]\n'.format(item, old_ssd_detail[item], new_ssd_detail[item])
                    notice = body + info
                    bodybox.append(notice)
        if bodybox:
            print(head)
            main_log.write(head)
            for notice in bodybox:
                print(notice)
                main_log.write(notice)
        else:
            info = '[{0}] ^^^ Alive Detected ^^^'.format(identifier)
            print(info)
            main_log.write(info)


# ------ Danger Zone ------ #
main_dict_file = 'main_dict.json'
monitor_inbox = Inbox(1025) # 建立监控服务器
dict_comp = DictCompare()
main_log = Log('main')  # 定义主log
warning_log = Log('warning')    # 定义警告log
error_log = Log('error')    # 定义错误log

monitor_inbox.on()  # 开启监控进程
main_dict = load_main_dict(main_dict_file)  # 读取主数据库

while True:
    if monitor_inbox.led():
        message = monitor_inbox.vomit()
        process(message)
    else:
        with open(main_dict_file, 'w') as db:
            json.dump(main_dict, db)
        time.sleep(2)
