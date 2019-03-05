import socket
import threading
import time
import json
import os


main_dict_file = 'main_dict.json'

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
            file.write(c_readable_time + '  ' + str)

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
                lock.acquire()
                while True:    
                    data = sock.recv(1024)
                    if not data:
                        break
                    decode_data = json.loads(data.decode('utf-8'))
                    self.__record.append(decode_data)
                    self.__led = True
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
            self.__led = False
            return None
        else:
            return self.__record.pop(0)


def load_main_dict(main_dict_file):
    '''尝试从本地json文件恢复main_dict,以防止主控以外关闭导致的数据丢失'''

    if os.path.exists(main_dict_file):
        with open(main_dict_file, 'r') as main_dict_obj:
            main_dict = json.loads(main_dict_obj)
    else:
        main_dict = {}
    return main_dict

def process(info):
    pass



# ------ Danger Zone ------ #
monitor_inbox = Inbox(1025)
main_log = Log('main.log')
warning_log = Log('warning.log')
error_log = Log('error.log')

monitor_inbox.on()
main_dict = load_main_dict(main_dict_file)

while True:
    if monitor_inbox.led():
        pass